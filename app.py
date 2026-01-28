import streamlit as st
import google.generativeai as genai
from PIL import Image
import pypdfium2 as pdfium
import json
import re

# --- 1. ブランド・定数設定 ---
BRAND_NAME = "EKAI" 
PROJECT_NAME = "閃 (HIRAMEKI)"
TOTAL_WORK_TIME = "4.5時間 + バグ取り（19:00開始）"

# --- 2. ページ構成 ---
st.set_page_config(page_title=f"{PROJECT_NAME} by {BRAND_NAME}", layout="wide")

st.markdown("""
    <style>
    .warning-box { border: 2px solid red; padding: 15px; border-radius: 10px; background-color: #fff0f0; margin-bottom: 15px; }
    .normal-box { border: 1px solid #ddd; padding: 15px; border-radius: 10px; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title(f"{PROJECT_NAME} - 検査成績書 解析システム")

# --- 3. サイドバー設定 ---
api_key = st.sidebar.text_input("Google API Key", type="password")
st.sidebar.markdown("---")
st.sidebar.write(f"ブランド: **{BRAND_NAME}**")
st.sidebar.write(f"作業累計: **{TOTAL_WORK_TIME}**")
st.sidebar.info("「私が100%制御しています」")

# --- 4. メイン処理 ---
uploaded_file = st.file_uploader("検査成績書（PDFまたは画像）をアップロード", type=["png", "jpg", "jpeg", "pdf"])

if api_key and uploaded_file:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-flash-lite-latest')

    if st.button("🚀 閃光解析を実行"):
        try:
            images = []
            if uploaded_file.type == "application/pdf":
                with st.spinner("PDFを解析用に最適化中..."):
                    pdf = pdfium.PdfDocument(uploaded_file)
                    for page in pdf:
                        bitmap = page.render(scale=2)
                        images.append(bitmap.to_pil())
            else:
                images.append(Image.open(uploaded_file))

            for page_idx, img in enumerate(images):
                st.image(img, caption=f"解析対象 ({page_idx+1}ページ目)", use_container_width=True)
                
                with st.spinner(f"ページ {page_idx+1} を『絵かい』の論理で解析中..."):
                    # プロンプトをJSON出力に固定するよう強化
                    prompt = """
                    検査成績書の表を解析し、必ず以下のJSON形式のみで返答してください。
                    [
                      {"項目": "項目名", "自主": "合格または良または空欄", "社内": "✓またはJまたはVまたは空欄", "署名": true/false}
                    ]
                    ※署名は「検査者署名欄」に名前が書いてあればtrue、空欄や「ー」ならfalseとしてください。
                    """
                    response = model.generate_content([prompt, img])
                    
                    # JSON部分だけを抽出する処理
                    json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
                    
                    if json_match:
                        parsed_items = json.loads(json_match.group())
                        
                        st.subheader(f"【第 {page_idx+1} ページ 判定結果】")

                        for item_idx, item in enumerate(parsed_items):
                            # --- 慧の確定ロジック ---
                            # 署名がfalse、または自主/社内が空欄なら赤枠
                            is_warning = (not item["署名"]) or (not item["自主"] and not item["社内"])
                            box_style = "warning-box" if is_warning else "normal-box"

                            st.markdown(f"""
                                <div class="{box_style}">
                                    <strong>項目: {item['項目']}</strong><br>
                                    自主検査: {item['自主'] if item['自主'] else '（未記入）'} / 
                                    社内検査: {item['社内'] if item['社内'] else '（未記入）'} / 
                                    署名: {"✅確認済" if item['署名'] else "❌署名漏れ"}
                                </div>
                            """, unsafe_allow_html=True)

                            # 「閃」確定転記ロジック
                            if item["自主"] in ["合格", "良"] and item["社内"] in ["✓", "J", "V"]:
                                st.info(f"💡 自主検査の『{item['自主']}』を転記しますか？")
                                if st.button(f"エクセルへ転記承認: {item['項目']}", key=f"btn_{page_idx}_{item_idx}"):
                                    st.success(f"『{item['項目']}』を転記しました。")
                    else:
                        st.warning("AIの回答からデータを抽出できませんでした。原文を確認してください。")
                        st.write(response.text)

        except Exception as e:
            st.error(f"解析エラー: {e}")
