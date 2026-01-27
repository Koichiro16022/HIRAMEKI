import streamlit as st
import google.generativeai as genai
from PIL import Image

st.title("閃 (HIRAMEKI) - 最終疎通テスト")

# サイドバー設定
api_key = st.sidebar.text_input("API Key", type="password")
uploaded_file = st.file_uploader("画像をアップロード", type=["png", "jpg", "jpeg", "pdf"])

if api_key and uploaded_file:
    # Google AI Studioの最新仕様に合わせた設定
    genai.configure(api_key=api_key)
    
    # 2026年現在、最も安定してリクエストを受け付ける「latest」を明示
    # これにより、v1betaの404エラーを完全に回避します
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    if st.button("🚀 閃光解析・最終確認"):
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="解析対象", width=300)
            
            with st.spinner("通信経路を確認中..."):
                # 非常にシンプルな命令で、まずは疎通だけを確認します
                response = model.generate_content(
                    ["この画像に書かれている文字を、箇条書きでいくつか抽出してください。", image]
                )
                
                # これが表示されれば、ついに「勝負」の舞台が整います！
                st.success("通信成功！呪いは完全に解けました。")
                st.write("--- 抽出された文字 ---")
                st.write(response.text)

        except Exception as e:
            st.error(f"エラー発生: {e}")
            if "429" in str(e):
                st.warning("現在、Google側の無料枠制限（混雑）に達しています。1分ほど待ってから再度ボタンを押してください。")
            else:
                st.info("モデル名を 'gemini-2.0-flash' に戻すか、APIキーの権限を再確認してください。")
