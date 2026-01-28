import streamlit as st
import google.generativeai as genai
from PIL import Image
import pypdfium2 as pdfium
import json
import re

# --- 1. ブランド・定数設定 ---
BRAND_NAME = "EKAI" 
PROJECT_NAME = "閃 (HIRAMEKI)"
TOTAL_WORK_TIME = "4.5時間 + バグ取り（2026/01/28 19:50）"

st.set_page_config(page_title=f"{PROJECT_NAME}", layout="wide")

# スタイル定義
st.markdown("""
    <style>
    .warning-box { border: 2px solid red; padding: 15px; border-radius: 10px; background-color: #fff0f0; margin-bottom: 15px; color: black; }
    .normal-box { border: 1px solid #ddd; padding: 15px; border-radius: 10px; background-color: #f0f8ff; margin-bottom: 15px; color: black; }
    .stButton>button { width: 100%; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title(f"{PROJECT_NAME} - ハイブリッド制御版")

# --- サイドバー ---
api_key = st.sidebar.text_input("Google API Key", type="password")
st.sidebar.write(f"作業累計: **{TOTAL_WORK_TIME}**")
st.sidebar.info("「判定の数式はPythonで100%制御しています」")

# 数値のクリーニング関数（φや±を除去して計算可能にする）
def clean_num(text):
    if text is None or text == "" or text == "―": return None
    try:
        # 数字、小数点、マイナス記号以外をすべて除去
        cleaned = re.sub(r'[^0-9.\-]', '', str(text))
        return float(cleaned) if cleaned else None
    except:
        return None

uploaded_file = st.file_uploader("PDFまたは画像をアップロード", type=["png", "jpg", "jpeg", "pdf"])

if api_key and uploaded_file:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-flash-lite-latest')

    if st.button("🚀 閃光解析を実行"):
        try:
            images = []
            if uploaded_file.type == "application/pdf":
                pdf = pdfium.PdfDocument(uploaded_file)
                for page in pdf:
                    images.append(page.render(scale=3).to_pil())
            else:
                images.append(Image.open(uploaded_file))

            for page_idx, img in enumerate(images):
                st.image(img, caption=f"解析対象 ({page_idx+1}ページ目)", use_container_width=True)
                
                with st.spinner(f"ページ {page_idx+1} からデータを読み取り中..."):
                    prompt = """
                    検査成績書の表からデータを抽出し、以下のJSON形式のリストのみで返してください。
                    [
                      {"項目": "A", "図面寸法": "350", "許容値": "5", "結果": "350", "社内": "なし", "署名": true}
                    ]
                    ※許容値が「±5」なら「5」と抽出してください。
                    ※署名はページ内に石田様の氏名があれば一律 true としてください。
                    """
                    response = model.generate_content([prompt, img])
                    json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
                    
                    if json_match:
                        raw_data = json.loads(json_match.group())
                        st.subheader(f"【第 {page_idx+1} ページ 判定結果】")

                        for item_idx, item in enumerate(raw_data):
                            # --- Pythonによる厳格判定 ---
                            base = clean_num(item.get("図面寸法"))
                            tol = clean_num(item.get("許容値"))
                            val = clean_num(item.get("結果"))
                            
                            judge = "判定不可"
                            is_ok = False
                            
                            if base is not None and tol is not None and val is not None:
                                lower = base - tol
                                upper = base + tol
                                if lower <= val <= upper:
                                    judge = "合格"
                                    is_ok = True
                                else:
                                    judge = "不合格"
                                    is_ok = False
                            
                            # 社内検査チェック（✓/J/V 等があればTrue）
                            has_check = item.get("社内") not in ["なし", "空欄", "ー", "―", "", None]
                            
                            # 警告フラグ：不合格、署名なし、社内チェックなしのいずれかで赤枠
                            is_warning = (judge == "不合格") or (not item.get("署名")) or (not has_check)
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

                            # 転記ボタンの表示条件
                            if is_ok and has_check:
                                st.info(f"💡 自主検査の『{judge}』を転記しますか？")
                                if st.button(f"承認: {item['項目']}", key=f"btn_{page_idx}_{item_idx}"):
                                    st.success(f"{item['項目']} を転記しました。")
                    else:
                        st.write("解析に失敗しました。原文：", response.text)

        except Exception as e:
            st.error(f"システムエラー: {e}")
