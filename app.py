import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
from pdf2image import convert_from_bytes
import os

# ページ設定
st.set_page_config(page_title="閃 - HIRAMEKI", layout="centered")

# 黄金色のテーマ
st.markdown("""<style>.main { background-color: #1a1a1a; color: #f4f4f4; } .stButton>button { background-color: #FFD700; color: black; font-weight: bold; width: 100%; } h1 { color: #FFD700; }</style>""", unsafe_allow_html=True)

st.title("閃 - HIRAMEKI")

st.sidebar.title("設定")
api_key = st.sidebar.text_input("Google API Keyを入力", type="password")

if api_key:
    try:
        # 【強制リセット】古い通信設定を物理的に消し去り、正式なv1に固定
        os.environ["GOOGLE_API_VERSION"] = "v1"
        genai.configure(api_key=api_key)
        
        uploaded_file = st.file_uploader("手書きのPDFまたは画像をアップロード", type=["pdf", "png", "jpg", "jpeg"])

        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                file_bytes = uploaded_file.read()
                images = convert_from_bytes(file_bytes)
                image = images[0]
            else:
                image = Image.open(uploaded_file)
            
            st.image(image, caption="解析対象の書類", use_column_width=True)

            if st.button("🚀 閃光解析（OCR実行）"):
                with st.spinner("慧(Kei)が解析中..."):
                    # モデル名をあえてフルパスで書かず、SDKに任せます
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt = "この成績書の画像から、製造番号(T1257ZTuなど)、検査数値、検査者名(石田耕一郎など)を全て抽出し、Markdownの表形式で出力してください。"
                    
                    # 最もシンプルな呼び出しに戻しつつ、内部で「v1」へ強制転換
                    # もしこれでもダメなら、SDKのバグそのものです
                    response = model.generate_content([prompt, image])
                    
                    st.subheader("📊 解析結果")
                    st.markdown(response.text)
                    st.download_button("📥 保存", data=response.text, file_name="result.txt")
                    
    except Exception as e:
        # エラー発生時の表示
        st.error(f"解析中にエラーが発生しました。\n詳細: {e}")
else:
    st.warning("左のサイドバーにGoogle API Keyを入力してください。")
