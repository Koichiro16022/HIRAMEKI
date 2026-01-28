import streamlit as st
import google.generativeai as genai
from PIL import Image

st.title("閃 (HIRAMEKI) - 朝の開通勝負")

api_key = st.sidebar.text_input("API Key", type="password")
uploaded_file = st.file_uploader("画像をアップロード", type=["png", "jpg", "jpeg"])

if api_key and uploaded_file:
    genai.configure(api_key=api_key)
    
    # 【作戦変更】2.0が混んでいるため、制限の緩い「Lite」で確実に道を通します
    # これも最新世代の安定版です
    model = genai.GenerativeModel('models/gemini-flash-lite-latest')

    if st.button("🚀 閃光解析・突入"):
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="解析対象", width=300)
            
            with st.spinner("Liteモデルで高速ルートを通過中..."):
                response = model.generate_content(
                    ["画像内の文字を読み取ってください", image]
                )
                
                st.success("通信成功！ついに門が開きました。")
                st.write("--- 解析結果 ---")
                st.write(response.text)

        except Exception as e:
            st.error(f"エラー発生: {e}")
            st.info("これでも429が出る場合は、Google Studio側で新しいAPIキーを生成するのが最短かもしれません。")
