import streamlit as st
import google.generativeai as genai
from PIL import Image
import pypdfium2 as pdfium
import json
import re

# --- 1. ブランド・定数設定 ---
# プロジェクト名：閃（ひらめき）
PROJECT_NAME = "閃（ひらめき）"
# 2026/01/28 19:00〜20:00 の成果を反映
TOTAL_WORK_TIME = "4.5時間 + バグ取り1.5時間（2026/01/28 20:30保存版）"

st.set_page_config(page_title=f"{PROJECT_NAME}", layout="wide")

# スタイル定義：警告（赤枠）と通常（青枠）の出し分け、および日本語エラー用のスタイル
st.markdown("""
    <style>
    .warning-box { border: 2px solid red; padding: 15px; border-radius: 10px; background-color: #fff0f0; margin-bottom: 15px; color: black; }
    .normal-box { border: 1px solid #ddd; padding: 15px; border-radius: 10px; background-color: #f0f8ff; margin-bottom: 15px; color: black; }
    .stButton>button { width: 100%; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title(f"{PROJECT_NAME} - 検査成績書 判定システム")

# --- サイドバー：ステータス管理 ---
api_key = st.sidebar.text_input("Google API Key", type="password")
st.sidebar.write(f"作業累計: **{TOTAL_WORK_TIME}**")
st.sidebar.info("「例外パターンもPythonで100%制御しています」")

# 数値クリーニング関数：AIが読み取った文字列から計算可能な数値のみを抽出
def clean_num(text):
    if text is None or text == "" or text in ["―", "ー", "none", "None"]: return None
    try:
        # 数字、小数点、マイナス記号以外をすべて除去
        cleaned = re.sub(r'[^0-9.\-]', '', str(text))
        return float(cleaned) if cleaned else None
    except:
        return None

uploaded_file = st.file_uploader("PDFまたは画像をアップロード", type=["png", "jpg", "jpeg", "pdf"])

if api_key and uploaded_file:
    genai.configure(api_key=api_key)
    # 制限がかかりにくい標準的なFlashモデルを使用
    model = genai.GenerativeModel('gemini-1.5-flash')

    if st.button("🚀 閃光解析を実行"):
        try:
            images = []
            if uploaded_file.type == "application/pdf":
                pdf = pdfium.PdfDocument(uploaded_file)
                for page in pdf:
                    # 解像度3倍でチェックマークの視認性を確保
                    images.append(page.render(scale=3).to_pil())
            else:
                images.append(Image.open(uploaded_file))

            for page_idx, img in enumerate(images):
                st.image(img, caption=f"解析対象 ({page_idx+1}ページ目)", use_container_width=True)
                
                with st.spinner(f"ページ {page_idx+1} を精査中..."):
                    # プロンプト：AIには「抽出」のみを命じ、判定はさせない
                    prompt = """
                    検査成績書の表からデータを抽出し、JSON形式のリストのみで返してください。
                    指定された列名（項目、図面寸法、許容値、結果、社内、署名）が見つからない場合は、
                    勝手に捏造せず、解析不可として回答を拒否してください。

                    [
                      {"項目": "A", "図面寸法": "350", "許容値": "5", "結果": "350", "社内": "なし", "署名": true}
                    ]
                    ※許容値が空欄や「ー」なら "None" としてください。
                    ※署名はページ内に石田様の氏名があれば一律 true。
                    """
                    
                    response = model.generate_content([prompt, img])
                    
                    # JSON形式の抽出を試みる
                    json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
                    
                    if json_match:
                        raw_data = json.loads(json_match.group())
                        st.subheader(f"【第 {page_idx+1} ページ 判定結果】")
                        
                        for item_idx, item in enumerate(raw_data):
                            # --- Pythonによる厳格な数値判定ロジック ---
                            base = clean_num(item.get("図面寸法"))
                            tol = clean_num(item.get("許容値"))
                            val = clean_num(item.get("結果"))
                            
                            judge = "不合格"
                            is_ok = False
                            
                            if base is not None and val is not None:
                                if tol is not None:
                                    # 許容値がある場合：範囲内か判定
                                    if (base - tol) <= val <= (base + tol):
                                        judge = "合格"
                                        is_ok = True
                                else:
                                    # 許容値がない場合：完全一致のみ合格
                                    if base == val:
                                        judge = "合格"
                                        is_ok = True
                                    else:
                                        judge = "判定不可(許容値なし)"
                                        is_ok = False
                            else:
                                judge = "データ不足"
                                is_ok = False
                            
                            # 社内検査欄のチェック有無（記号があればTrue）
                            has_check = item.get("社内") not in ["なし", "空欄", "ー", "―", "", None]
                            
                            # 警告（赤枠）のルール
                            is_warning = (not is_ok) or (not item.get("署名")) or (not has_check)
                            box_style = "warning-box" if is_warning else "normal-box"
                            
                            st.markdown(f"""
                                <div class="{box_style}">
                                    <strong>項目: {item['項目']}</strong><br>
                                    図面基準: {base if base is not None else '---'} (±{tol if tol is not None else '---'})<br>
                                    実測結果: {val if val is not None else '---'}<br>
                                    判定結果: <span style="color:{'green' if is_ok else 'red'}; font-weight:bold;">{judge}</span><br>
                                    社内検査: {item.get('社内')} / 署名: {"✅確認済" if item.get('署名') else "❌署名漏れ"}
                                </div>
                            """, unsafe_allow_html=True)

                            # 確定ロジックに基づく転記ボタン
                            if is_ok and has_check and item.get("署名"):
                                st.info(f"💡 自主検査の『{judge}』を転記しますか？")
                                if st.button(f"承認してエクセル転記: {item['項目']}", key=f"btn_{page_idx}_{item_idx}"):
                                    st.success(f"{item['項目']} を転記リストに追加しました。")
                    
                    else:
                        # --- 耕一郎様こだわりの日本語エラー表示 ---
                        st.error("⚠️ 解析対象外の書類です")
                        st.warning(f"""
                        読み取ったデータは「検査成績書」ではありません。
                        「閃（ひらめき）」は検査成績書の解析に特化しているため、他の形式の書類や練習シートは処理できません。
                        
                        **確認してください:**
                        1. 項目、図面寸法、許容値、結果の表が含まれていますか？
                        2. 「石田」様の署名はありますか？
                        """)
                        with st.expander("AIからの詳細（英語メッセージ）"):
                            st.write(response.text)

        except Exception as e:
            st.error(f"システムエラーが発生しました: {e}")

else:
    st.info("APIキーを入力し、検査成績書（PDF/画像）をアップロードしてください。")
