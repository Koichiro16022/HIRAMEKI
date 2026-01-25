import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
from pdf2image import convert_from_bytes
import os

# --- ページ設定 ---
st.set_page_config(page_title="SOU - HIRAMEKI", layout="centered")

# 黄金色のテーマ
st.markdown("""
    <style>
    .main { background-color: #1a1a1a; color: #f4f4f4; }
    .stButton>button { background-color: #FFD700; color: black; font-weight: bold; border-radius: 5px; width: 100%; }
    h1 { color: #FFD700; border-bottom: 2px solid #FFD700; }
    </style>
    """, unsafe_allow_html=True)

st.title("SOU - HIRAMEKI")

# --- サイドバー設定 ---
st.sidebar.title("設定")
api_key = st.sidebar.text_input("Google API Keyを入力", type="password")

if api_key:
    try:
        # 【重要】通信をREST形式に強制し、v1betaを回避します
        genai.configure(api_key=api_key, transport='rest')
        
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
                    # 【重要】不具合の出にくい最新のモデル名をフルパスで指定
                    model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
                    
                    prompt = """
                    この成績書の画像から以下の情報を抽出し、Markdownの表形式で出力してください。
                    1. 製造番号 (例: T1257ZTu)
                    2. 各項目の検査数値
                    3. 検査者名 (例: 石田耕一郎)
                    """
                    
                    # 生成実行
                    response = model.generate_content([prompt, image])
                    
                    st.subheader("📊 解析結果")
                    st.markdown(response.text)
                    st.download_button("📥 保存", data=response.text, file_name="result.txt")
                    
    except Exception as e:
        # 404が出た場合に、より分かりやすいヒントを表示します
        if "404" in str(e):
            st.error("Googleのサーバーが古い窓口(v1beta)を案内しています。このエラーが出る場合は、新しいAPIキーを再度作成するか、しばらく時間をおいて試してください。")
        st.error(f"解析中にエラーが発生しました。\n詳細: {e}")
else:
    st.warning("左のサイドバーにGoogle API Keyを入力してください。")
