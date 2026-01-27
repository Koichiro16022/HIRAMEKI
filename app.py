import streamlit as st
import google.generativeai as genai
from PIL import Image

st.title("閃 (HIRAMEKI) - 2.0世代接続テスト")

api_key = st.sidebar.text_input("API Key", type="password")
uploaded_file = st.file_uploader("画像をアップロード", type=["png", "jpg", "jpeg", "pdf"])

if api_key and uploaded_file:
    # 設定
    genai.configure(api_key=api_key)
    
    # 【変更点】リストの4番目にあった正確な名称 'models/gemini-2.0-flash' を指定
    # models/ を含めることで、ライブラリの自動推測を抑制します
    model = genai.GenerativeModel('models/gemini-2.0-flash')

    if st.button("🚀 2.0世代で解析実行"):
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="解析対象", width=300)
            
            with st.spinner("最新の閃（2.0）が通信中..."):
                response = model.generate_content(
                    ["画像内の表から文字を読み取ってください", image]
                )
                
                st.success("ついに呪いが解けました！2.0世代で接続成功です。")
                st.write(response.text)

        except Exception as e:
            st.error(f"エラー発生: {e}")
            st.info("このエラーが出る場合、モデル名を 'gemini-2.0-flash-001' (リスト5番) に微調整します。")
