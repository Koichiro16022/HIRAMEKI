import streamlit as st
import google.generativeai as genai
from PIL import Image
import pypdfium2 as pdfium
import json
import re

# --- 1. ブランド・定数設定 ---
PROJECT_NAME = "閃（ひらめき）"
# 作業時間を更新
TOTAL_WORK_TIME = "4.5時間 + バグ取り1.5時間 + 安定版への復旧（2026/01/29 19:15版）"

st.set_page_config(page_title=f"{PROJECT_NAME}", layout="wide")

st.markdown("""
    <style>
    .warning-box { border: 2px solid red; padding: 15px; border-radius: 10px; background-color: #fff0f0; margin-bottom: 15px; color: black; }
    .normal-box { border: 1px solid #ddd; padding: 15px; border-radius: 10px; background-color: #f0f8ff; margin-bottom: 15px; color: black; }
    .stButton>button { width: 100%; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title(f"{PROJECT_NAME} - 検査成績書 判定システム")

api_key = st.sidebar.text_input("Google API Key", type="password")
st.sidebar.write(f"作業累計: **{TOTAL_WORK_TIME}**")
st.sidebar.info("「昨日成功した安定ロジックに復旧しました」")

def clean_num(text):
    if text is None or text == "" or text in ["―", "ー", "none", "None"]: return None
    try:
        cleaned = re.sub(r'[^0-9.\-]', '', str(text))
        return float(cleaned) if cleaned else None
    except:
        return None

uploaded_file = st.file_uploader("PDFまたは画像をアップロード", type=["png", "jpg", "jpeg", "pdf"])

if api_key and uploaded_file:
    genai.configure(api_key=api_key)
    # 昨日、唯一 404 が出なかったモデル名に戻します
    model = genai.GenerativeModel('gemini-2.0-flash-lite-preview-02-05')

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
                
                with st.spinner(f"ページ {page_idx+1} を精査中..."):
                    prompt = """
                    検査成績書の表からデータを抽出し、JSON形式のリストのみで返してください。
                    指定された列名（項目、図面寸法、許容値、結果、社内、署名）が見つからない場合は、
                    解析不可として回答を拒否してください。
                    [{"項目": "A", "図面寸法": "350", "許容値": "5", "結果": "350", "社内": "なし", "署名": true}]
                    ※署名はページ内に石田様の氏名があれば一律 true。
                    """
                    
                    response = model.generate_content([prompt, img])
                    json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
                    
                    if json_match:
                        raw_data = json.loads(json_match.group())
                        st.subheader(f"【第 {page_idx+1} ページ 判定結果】")
                        
                        for item_idx, item in enumerate(raw_data):
                            base = clean_num(item.get("図面寸法"))
                            tol = clean_num(item.get("許容値"))
                            val = clean_num(item.get("結果"))
                            judge = "不合格"; is_ok = False
                            
                            if base is not None and val is not None:
                                if tol is not None:
                                    if (base - tol) <= val <= (base + tol):
                                        judge = "合格"; is_ok = True
                                else:
                                    if base == val:
                                        judge = "合格"; is_ok = True
                            
                            has_check = item.get("社内") not in ["なし", "空欄", "ー", "―", "", None]
                            is_warning = (not is_ok) or (not item.get("署名")) or (not has_check)
                            box_style = "warning-box" if is_warning else "normal-box"
                            
                            st.markdown(f"""
                                <div class="{box_style}">
                                    <strong>項目: {item['項目']}</strong><br>
                                    判定結果: <span style="color:{'green' if is_ok else 'red'}; font-weight:bold;">{judge}</span><br>
                                    社内検査: {item.get('社内')} / 署名: {"✅確認済" if item.get('署名') else "❌署名漏れ"}
                                </div>
                            """, unsafe_allow_html=True)

                            if is_ok and has_check and item.get("署名"):
                                st.info(f"💡 自主検査の『{judge}』を転記しますか？")
                                if st.button(f"承認してエクセル転記: {item['項目']}", key=f"btn_{page_idx}_{item_idx}"):
                                    st.success(f"{item['項目']} を転記しました。")
                    else:
                        # ここだけ日本語エラー表示を組み込みました
                        st.error("⚠️ 解析対象外の書類です")
                        st.warning("読み取ったデータは「検査成績書」ではありません。正しい形式のPDFをアップロードしてください。")
                        with st.expander("AIからの詳細（英語）"):
                            st.write(response.text)

        except Exception as e:
            st.error(f"システムエラー: {e}")

else:
    st.info("APIキーを入力し、検査成績書をアップロードしてください。")
