import streamlit as st
import google.generativeai as genai
from PIL import Image
import time

st.title("閃 (HIRAMEKI) - 疎通確認(2.0-001版)")

api_key = st.sidebar.text_input("API Key", type="password")
uploaded_file = st.file_uploader("画像をアップロード", type=["png", "jpg", "jpeg", "pdf"])

if api_key and uploaded_file:
    genai.configure(api_key=api_key)
    
    # リスト5番の特定バージョンを指定。混雑回避を狙います。
    model = genai.GenerativeModel('models/gemini-2.0-flash-001')

    if st.button("🚀 解析実行（1分待機後に推奨）"):
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="解析対象", width=300)
            
            with st.spinner("2.0-001の列に並んでいます..."):
                response = model.generate_content(
                    ["画像内のテキストをすべて抽出してください", image]
                )
                
                st.success("接続成功！呪いも混雑も突破しました。")
                st.write("--- 解析結果 ---")
                st.write(response.text)

        except Exception as e:
            st.error(f"エラー発生: {e}")
            if "429" in str(e):
                st.warning("まだ列が混んでいます。あと1分待ってから再試行してください。")
