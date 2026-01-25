import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
from pdf2image import convert_from_bytes

# ページ設定
st.set_page_config(page_title="閃 - HIRAMEKI", layout="centered")

# 黄金色のテーマ
st.markdown("""
    <style>
    .main { background-color: #1a1a1a; color: #f4f4f4; }
    .stButton>button { background-color: #FFD700; color: black; font-weight: bold; border-radius: 5px; width: 100%; }
    h1 { color: #FFD700; border-bottom: 2px solid #FFD700; }
    </style>
    """, unsafe_allow_html=True)

st.title("閃 - HIRAMEKI")

# --- サイドバー：APIキーの入力 ---
st.sidebar.title("設定")
api_key = st.sidebar.text_input("Google API Keyを入力", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        uploaded_file = st.file_uploader("手書きのPDFまたは画像をアップロード", type=["pdf", "png", "jpg", "jpeg"])

        if uploaded_file:
            # PDF/画像の読み込み
            if uploaded_file.type == "application/pdf":
                file_bytes = uploaded_file.read()
                images = convert_from_bytes(file_bytes)
                image = images[0]
            else:
                image = Image.open(uploaded_file)
            
            st.image(image, caption="解析対象の書類", use_column_width=True)

            if st.button("🚀 閃光解析（OCR実行）"):
                with st.spinner("慧(Kei)が解析中..."):
                    # --- エラー回避用の二段構えモデル選択 ---
                    try:
                        # 第一候補: 最新の正式名称
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        prompt = "この成績書の画像から数値を抽出し、Markdownの表形式で出力してください。"
                        response = model.generate_content([prompt, image])
                    except Exception:
                        # 第二候補: 404が出た場合の代替指定法
                        model = genai.GenerativeModel('models/gemini-1.5-flash')
                        response = model.generate_content([prompt, image])
                    
                    st.subheader("📊 解析結果")
                    st.markdown(response.text)
                    st.download_button("📥 保存", data=response.text, file_name="result.txt")
                    
    except Exception as e:
        st.error(f"解析中にエラーが発生しました: {e}")
else:
    st.warning("左のサイドバーにGoogle API Keyを入力してください。")
