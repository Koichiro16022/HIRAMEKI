import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
# 追加
from pdf2image import convert_from_bytes

st.set_page_config(page_title="閃 - HIRAMEKI", layout="centered")

# 黄金色のテーマ
st.markdown("""<style>.main { background-color: #1a1a1a; color: #f4f4f4; } .stButton>button { background-color: #FFD700; color: black; font-weight: bold; width: 100%; } h1 { color: #FFD700; }</style>""", unsafe_allow_html=True)

st.title("閃 - HIRAMEKI")

st.sidebar.title("設定")
api_key = st.sidebar.text_input("Google API Keyを入力", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        # 'models/' を頭に付け、最新の識別子に変更します
model = genai.GenerativeModel('models/gemini-1.5-flash-latest')

        uploaded_file = st.file_uploader("手書きのPDFまたは画像をアップロード", type=["pdf", "png", "jpg", "jpeg"])

        if uploaded_file:
            # --- PDFを画像に変換する処理を追加 ---
            if uploaded_file.type == "application/pdf":
                images = convert_from_bytes(uploaded_file.read())
                image = images[0] # 1ページ目を対象にする
            else:
                image = Image.open(uploaded_file)
            
            st.image(image, caption="解析対象の書類", use_column_width=True)

            if st.button("🚀 閃光解析（OCR実行）"):
                with st.spinner("慧(Kei)が解析中..."):
                    prompt = "この成績書から数値を抽出し、Markdownの表形式で出力してください。"
                    response = model.generate_content([prompt, image])
                    st.subheader("📊 解析結果")
                    st.markdown(response.text)
                    st.download_button("📥 保存", data=response.text, file_name="result.txt")
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
else:
    st.warning("左のサイドバーにGoogle API Keyを入力してください。")
