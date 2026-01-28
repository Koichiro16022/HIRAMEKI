import streamlit as st
import google.generativeai as genai
from PIL import Image
import pypdfium2 as pdfium
import json
import re

# --- 1. ブランド・定数設定 ---
BRAND_NAME = "EKAI" 
PROJECT_NAME = "閃 (HIRAMEKI)"
TOTAL_WORK_TIME = "4.5時間 + バグ取り（2026/01/28 19:25）"

st.set_page_config(page_title=f"{PROJECT_NAME}", layout="wide")

st.markdown("""
    <style>
    .warning-box { border: 2px solid red; padding: 15px; border-radius: 10px; background-color: #fff0f0; margin-bottom: 15px; color: black; }
    .normal-box { border: 1px solid #ddd; padding: 15px; border-radius: 10px; background-color: #f0f2f6; margin-bottom: 15px; color: black; }
    </style>
    """, unsafe_allow_html=True)

st.title(f"{PROJECT_NAME} - 視覚認識強化版")

api_key = st.sidebar.text_input("Google API Key", type="password")
st.sidebar.write(f"作業累計: **{TOTAL_WORK_TIME}**")
st.sidebar.info("「私が100%制御しています」")

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
                    # scale=3 に上げ、より微細なチェックマークを拾いやすくする
                    bitmap = page.render(scale=3)
                    images.append(bitmap.to_pil())
            else:
                images.append(Image.open(uploaded_file))

            for page_idx, img in enumerate(images):
                st.image(img, caption=f"解析対象 ({page_idx+1}ページ目)", use_container_width=True)
                
                with st.spinner(f"ページ {page_idx+1} の微細なチェックをスキャン中..."):
                    # 指示をさらに鋭く（社内検査の記号に特化）
                    prompt = """
                    この検査成績書の表を、虫眼鏡で見るように精密に解析し、必ず以下のJSON形式リストのみで返してください。
                    [
                      {"項目": "A", "自主": "合格", "社内": "✓", "署名": true}
                    ]
                    【重要ルール】
                    1. 「社内検査」欄を凝視してください。単なるハイフン「ー」なのか、手書きの「✓」「J」「V」「L」などのチェック記号なのかを厳密に区別してください。
                    2. 記号があればその文字を、なければ「空欄」としてください。
                    3. 数値（自主検査結果）と許容値を比較し、範囲内なら「合格」、外なら「不合格」と判定。
                    4. ページ内に石田様の署名があれば全項目 署名: true としてください。
                    """
                    response = model.generate_content([prompt, img])
                    
                    json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
                    
                    if json_match:
                        parsed_items = json.loads(json_match.group())
                        st.subheader(f"【第 {page_idx+1} ページ 判定結果】")

                        for item_idx, item in enumerate(parsed_items):
                            # 自主不合格、または署名なし、または社内空欄なら赤枠
                            is_warning = (item["自主"] == "不合格") or (not item["署名"]) or (not item["社内"] or item["社内"] in ["", "―", "ー", "（空欄）"])
                            box_style = "warning-box" if is_warning else "normal-box"

                            st.markdown(f"""
                                <div class="{box_style}">
                                    <strong>項目: {item['項目']}</strong><br>
                                    自主判定: {item['自主']} / 社内検査: {item['社内']} / 
                                    署名: {"✅確認済" if item['署名'] else "❌署名漏れ"}
                                </div>
                            """, unsafe_allow_html=True)

                            # 転記ボタン：自主合格 かつ 社内チェックが「ー」以外の場合
                            has_check = item["社内"] not in ["", "―", "ー", "（空欄）"]
                            if item["自主"] in ["合格", "良"] and has_check:
                                st.info(f"💡 自主検査の『{item['自主']}』を転記しますか？")
                                if st.button(f"承認: {item['項目']}", key=f"btn_{page_idx}_{item_idx}"):
                                    st.success(f"{item['項目']} を転記しました。")
                    else:
                        st.write("解析原文：", response.text)

        except Exception as e:
            st.error(f"エラー: {e}")
