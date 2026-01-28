import streamlit as st
import google.generativeai as genai
from PIL import Image
import pypdfium2 as pdfium
import json
import re

# --- 1. ブランド・定数設定 ---
BRAND_NAME = "EKAI" 
PROJECT_NAME = "閃 (HIRAMEKI)"
TOTAL_WORK_TIME = "4.5時間 + バグ取り（2026/01/28 19:45）"

st.set_page_config(page_title=f"{PROJECT_NAME}", layout="wide")

st.markdown("""
    <style>
    .warning-box { border: 2px solid red; padding: 15px; border-radius: 10px; background-color: #fff0f0; margin-bottom: 15px; color: black; }
    .normal-box { border: 1px solid #ddd; padding: 15px; border-radius: 10px; background-color: #f0f2f6; margin-bottom: 15px; color: black; }
    </style>
    """, unsafe_allow_html=True)

st.title(f"{PROJECT_NAME} - 厳格数値監査版")

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
                    images.append(page.render(scale=4).to_pil())
            else:
                images.append(Image.open(uploaded_file))

            for page_idx, img in enumerate(images):
                st.image(img, caption=f"解析対象 ({page_idx+1}ページ目)", use_container_width=True)
                
                with st.spinner(f"ページ {page_idx+1} の数値を監査中..."):
                    # 数値判定の思考プロセスを強制するプロンプト
                    prompt = """
                    検査成績書を解析し、以下のJSONリスト形式のみで返してください。
                    
                    【判定の鉄則】
                    1. 各項目について、[図面寸法] [許容値] [自主検査結果] の3点を必ず抽出せよ。
                    2. 計算を行え：(図面寸法 - 許容値) <= 自主検査結果 <= (図面寸法 + 許容値) かどうか。
                    3. 1ミリでも、0.1でも範囲外なら、必ず「不合格」と判定せよ。
                    4. ページ内に「石田」の署名があれば 署名: true。
                    5. 「社内検査」欄に記号がなければ「なし」。
                    
                    JSON format:
                    [{"項目": "A", "自主": "不合格", "理由": "506 > 505のため", "社内": "なし", "署名": true}]
                    """
                    response = model.generate_content([prompt, img])
                    
                    json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
                    
                    if json_match:
                        parsed_items = json.loads(json_match.group())
                        st.subheader(f"【第 {page_idx+1} ページ 判定結果】")

                        for item_idx, item in enumerate(parsed_items):
                            has_check = item["社内"] not in ["なし", "空欄", "ー", "―", ""]
                            # 不合格、署名なし、社内なしのいずれかで赤枠
                            is_warning = (item["自主"] == "不合格") or (not item["署名"]) or (not has_check)
                            box_style = "warning-box" if is_warning else "normal-box"

                            st.markdown(f"""
                                <div class="{box_style}">
                                    <strong>項目: {item['項目']}</strong><br>
                                    自主判定: <span style="color:red; font-weight:bold;">{item['自主']}</span> ({item.get('理由', '')})<br>
                                    社内検査: {item['社内']} / 署名: {"✅確認済" if item['署名'] else "❌署名漏れ"}
                                </div>
                            """, unsafe_allow_html=True)

                            if item["自主"] in ["合格", "良"] and has_check:
                                st.info(f"💡 転記しますか？")
                                if st.button(f"承認: {item['項目']}", key=f"btn_{page_idx}_{item_idx}"):
                                    st.success(f"{item['項目']} を転記しました。")
                    else:
                        st.write("解析原文：", response.text)

        except Exception as e:
            st.error(f"エラー: {e}")
