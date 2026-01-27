import streamlit as st
import google.generativeai as genai
from PIL import Image

st.title("閃 (HIRAMEKI) - 疎通確認")

# 1. 最小限の入力
api_key = st.sidebar.text_input("API Key", type="password")
uploaded_file = st.file_uploader("画像をアップロード", type=["png", "jpg", "jpeg", "pdf"])

if api_key and uploaded_file:
    # 2. 安定版(v1)の設定
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    if st.button("🚀 疎通テスト実行"):
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="解析対象", width=300)
            
            with st.spinner("通信中..."):
                # 3. 最小限のプロンプト
                response = model.generate_content(["画像の内容を簡潔にテキスト化してください", image])
                
                # 4. 結果表示（これが出れば呪い解除成功！）
                st.success("通信成功！")
                st.write(response.text)

        except Exception as e:
            st.error(f"エラー発生: {e}")
