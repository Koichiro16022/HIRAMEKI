import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="閃 - HIRAMEKI")
st.title("閃 - HIRAMEKI")

st.sidebar.title("設定")
api_key = st.sidebar.text_input("新しいGoogle API Keyを入力", type="password")

if api_key:
    try:
        # 最新版(0.8.3)はこれで自動的に v1 に繋がります
        genai.configure(api_key=api_key)
        uploaded_file = st.file_uploader("画像をアップロード(JPG/PNG)", type=["png", "jpg", "jpeg"])

        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="解析対象", use_column_width=True)

            if st.button("🚀 閃光解析"):
                with st.spinner("解析中..."):
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(["画像から製造番号、数値を抽出し表にしてください。検査者(石田耕一郎)も必須です。", image])
                    st.markdown(response.text)
                    
    except Exception as e:
        st.error(f"詳細: {e}")
