import streamlit as st
import google.generativeai as genai
from PIL import Image

st.title("閃 (HIRAMEKI) - 疎通確認(1.5-Pro版)")

api_key = st.sidebar.text_input("API Key", type="password")
uploaded_file = st.file_uploader("画像をアップロード", type=["png", "jpg", "jpeg", "pdf"])

if api_key and uploaded_file:
    genai.configure(api_key=api_key)
    
    # 【変更点】Flashが混んでいるので、あえて「Pro」の列に並びます
    model = genai.GenerativeModel('models/gemini-1.5-pro')

    if st.button("🚀 1.5-Proで解析実行"):
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="解析対象", width=300)
            
            with st.spinner("1.5-Pro（賢いモデル）で通信中..."):
                response = model.generate_content(
                    ["画像内のテキストをすべて抽出してください", image]
                )
                
                st.success("通信成功！Proの列は空いていました！")
                st.write("--- 解析結果 ---")
                st.write(response.text)

        except Exception as e:
            st.error(f"エラー発生: {e}")
