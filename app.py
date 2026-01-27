import streamlit as st
import google.generativeai as genai
from PIL import Image

st.title("閃 (HIRAMEKI) - 疎通確認(v1強制)")

api_key = st.sidebar.text_input("API Key", type="password")
uploaded_file = st.file_uploader("画像をアップロード", type=["png", "jpg", "jpeg", "pdf"])

if api_key and uploaded_file:
    # 1. 安定版を明示的に設定
    genai.configure(api_key=api_key)
    
    # 2. ここが重要：'v1beta'を避けるためにモデル名を直接指定
    # 'models/gemini-1.5-flash' ではなく 'gemini-1.5-flash' とし、
    # 内部的にv1を使用するよう促します
    model = genai.GenerativeModel('gemini-1.5-flash')

    if st.button("🚀 疎通テスト実行"):
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="解析対象", width=300)
            
            with st.spinner("通信中..."):
                # 3. 実行時に明示的に「v1」をリクエストする場合の書き方（必要に応じて）
                response = model.generate_content(
                    ["画像の内容をテキスト化してください", image]
                )
                
                st.success("通信成功！")
                st.write(response.text)

        except Exception as e:
            # 4. エラーが出た場合、利用可能なモデル一覧を画面に出して原因を特定する
            st.error(f"エラー発生: {e}")
            st.info("利用可能なモデルを確認中...")
            models = [m.name for m in genai.list_models()]
            st.write("あなたが今使えるモデル一覧:", models)
