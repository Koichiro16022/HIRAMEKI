import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
from pdf2image import convert_from_bytes
import os

# --- ページ設定 ---
st.set_page_config(page_title="SOU - HIRAMEKI", layout="centered")

# 黄金色のテーマ
st.markdown("""<style>.main { background-color: #1a1a1a; color: #f4f4f4; } .stButton>button { background-color: #FFD700; color: black; font-weight: bold; width: 100%; } h1 { color: #FFD700; }</style>""", unsafe_allow_html=True)

st.title("SOU - HIRAMEKI")

st.sidebar.title("設定")
api_key = st.sidebar.text_input("Google API Keyを入力", type="password")

if api_key:
    try:
        # 【物理的強制】通信ライブラリの深層部で「v1」を使うように環境変数を上書き
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
                    # モデル名を「models/」抜きで指定（最新仕様）
                    # これによりライブラリが古い地図を参照するのを防ぎます
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt = "画像から製造番号(T1257ZTu等)と検査数値を抽出し表にしてください。検査者名(石田耕一郎)も必須です。"
                    
                    # 通信の瞬間に「正式版」を指定する特別オプション
                    from google.generativeai.types import RequestOptions
                    response = model.generate_content(
                        [prompt, image],
                        request_options={'api_version': 'v1'}
                    )
                    
                    st.subheader("📊 解析結果")
                    st.markdown(response.text)
                    st.download_button("📥 保存", data=response.text, file_name="result.txt")
                    
    except Exception as e:
        # もしこれでも「v1beta」と言ってきたら、エラー内容を表示
        st.error(f"解析中にエラーが発生しました。\n詳細: {e}")
else:
    st.warning("左のサイドバーにGoogle API Keyを入力してください。")
