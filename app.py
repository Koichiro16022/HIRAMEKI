import streamlit as st
import google.generativeai as genai
from PIL import Image

st.title("閃 (HIRAMEKI) - 呪い完全封印Ver.")

api_key = st.sidebar.text_input("API Key", type="password")
uploaded_file = st.file_uploader("画像をアップロード", type=["png", "jpg", "jpeg", "pdf"])

if api_key and uploaded_file:
    # 接続設定
    genai.configure(api_key=api_key)
    
    # 呪いの「1.5」を避け、2.0系を「models/」付きで厳密に指定
    # これが今、最も確実な「新しい窓口」への切符です
    model = genai.GenerativeModel(model_name='models/gemini-2.0-flash')

    if st.button("🚀 2.0世代で勝負を開始する"):
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="解析対象", width=300)
            
            with st.spinner("最新世代の『閃』がゲートを通過中..."):
                response = model.generate_content(["画像の内容を抽出してください", image])
                
                st.success("通信成功！ついに呪いを焼き払いました。")
                st.write("--- 解析結果 ---")
                st.write(response.text)

        except Exception as e:
            if "404" in str(e):
                st.error("まだ古い窓口に案内されています。ブラウザの『再読み込み』ではなく、Streamlitの『Deploy』ボタン横のメニューから『Reboot App』を試す価値があります。")
            elif "429" in str(e):
                st.warning("道は繋がっています！ただいま大混雑中です。あと60秒待ってから、もう一度だけボタンを押してください。")
            else:
                st.error(f"エラー発生: {e}")
