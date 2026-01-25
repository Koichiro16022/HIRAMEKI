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

st.sidebar.title("設定")
api_key = st.sidebar.text_input("Google API Keyを入力", type="password")

if api_key:
    try:
        # APIの設定
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
                    # 【究極の修正】
                    # models/gemini-1.5-flash ではなく
                    # 通信エラーを避けるためにモデルを直接生成する関数を微調整します
                    model = genai.GenerativeModel(
                        model_name='gemini-1.5-flash',
                    )
                    
                    # プロンプトの構築
                    prompt = "この成績書の画像から、製造番号(T1257ZTuなど)、検査数値、検査者名(石田耕一郎など)を全て抽出し、Markdownの表形式で出力してください。"
                    
                    # 生成実行
                    # もしこれでもダメなら、内部で 'v1' を強制する特別な呼び出しを行います
                    response = model.generate_content([prompt, image])
                    
                    st.subheader("📊 解析結果")
                    st.markdown(response.text)
                    st.download_button("📥 保存", data=response.text, file_name="result.txt")
                    
    except Exception as e:
        # エラーが出た場合、詳細を表示
        st.error(f"解析中にエラーが発生しました。\n詳細: {e}")
else:
    st.warning("左のサイドバーにGoogle API Keyを入力してください。")
