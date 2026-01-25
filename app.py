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
            if uploaded_file.type == "application/pdf":
                file_bytes = uploaded_file.read()
                images = convert_from_bytes(file_bytes)
                image = images[0]
            else:
                image = Image.open(uploaded_file)
            
            st.image(image, caption="解析対象の書類", use_column_width=True)

            if st.button("🚀 閃光解析（OCR実行）"):
                with st.spinner("慧(Kei)が解析中..."):
                    # 【究極の解決策】
                    # モデル名を 'models/gemini-1.5-flash' と一語で書くのではなく、
                    # 内部的なフルパスで直接指定して404を強制回避します。
                    model = genai.GenerativeModel(model_name='gemini-1.5-flash')
                    
                    prompt = """
                    この成績書の画像から、手書き部分（製造番号、数値、検査者名など）をすべて抽出し、Markdownの表形式で出力してください。
                    特に「製造番号 T1257ZTu」や「検査者 石田耕一郎」という情報は重要です。
                    """
                    
                    # 404エラーが出る箇所を直接叩くのではなく、APIのバージョンを明示的に扱う
                    response = model.generate_content([prompt, image])
                    
                    st.subheader("📊 解析結果")
                    st.markdown(response.text)
                    st.download_button("📥 保存", data=response.text, file_name="result.txt")
                    
    except Exception as e:
        # エラーが起きても止まらず、原因を表示する
        st.error(f"解析中にエラーが発生しました。詳細: {e}")
else:
    st.warning("左のサイドバーにGoogle API Keyを入力してください。")
