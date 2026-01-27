import streamlit as st
import google.generativeai as genai
from PIL import Image

st.title("閃 (HIRAMEKI) - 疎通確認(2026最新版)")

api_key = st.sidebar.text_input("API Key", type="password")
uploaded_file = st.file_uploader("画像をアップロード", type=["png", "jpg", "jpeg", "pdf"])

if api_key and uploaded_file:
    genai.configure(api_key=api_key)
    
    # リストにある最新モデル「gemini-2.0-flash」を明示的に指定
    # これにより v1beta の呪いを回避し、最新世代で実行します
    model = genai.GenerativeModel('gemini-2.0-flash')

    if st.button("🚀 閃光解析・起動"):
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="解析対象", width=300)
            
            with st.spinner("最新世代の『閃』が思考中..."):
                response = model.generate_content(
                    ["画像の内容をテキスト化してください", image]
                )
                
                st.success("呪い解除成功！最新世代で接続しました。")
                st.write("--- 解析結果 ---")
                st.write(response.text)

        except Exception as e:
            st.error(f"エラー発生: {e}")
            st.info("もしこれでもダメな場合は、'gemini-flash-latest' を試します。")
