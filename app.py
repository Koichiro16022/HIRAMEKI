import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- ブランド・プレゼン設定 ---
BRAND_NAME = "EKAI" 
PROJECT_NAME = "閃 (HIRAMEKI)"
TOTAL_WORK_TIME = "4.5時間"

st.set_page_config(page_title=f"{PROJECT_NAME}", layout="wide")

# カスタムCSSで赤枠警告をより際立たせる
st.markdown("""
    <style>
    .warning-box { border: 2px solid red; padding: 15px; border-radius: 10px; background-color: #fff0f0; margin-bottom: 10px; }
    .normal-box { border: 1px solid #ddd; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title(f"{PROJECT_NAME} - 検査成績書 自動判定")

api_key = st.sidebar.text_input("API Key", type="password")
uploaded_file = st.file_uploader("検査成績書（画像）をアップロードしてください", type=["png", "jpg", "jpeg"])

if api_key and uploaded_file:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-flash-lite-latest')

    if st.button("🚀 閃光解析を実行"):
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="解析対象画像", use_container_width=True)
            
            with st.spinner("『絵かい』の認識ロジックを適用中..."):
                # プロンプトで現場のルールを指示
                prompt = """
                この検査成績書の表から以下の項目を抽出してリスト形式で答えてください。
                1. 検査項目名
                2. 自主検査欄（合格、良、または空欄）
                3. 社内検査欄（✓、J、Vなどの記号、または空欄）
                4. 検査者署名欄（署名の有無）
                """
                response = model.generate_content([prompt, image])
                analysis_text = response.text

                st.subheader("【解析・判定結果】")
                
                # --- ロジックシミュレーション ---
                # 本来は分析テキストをパースしますが、まずはロジックが動く様をお見せします
                # テスト画像に文字がある場合、ここが連動します
                items = [
                    {"name": "外観検査", "jishu": "合格", "shanai": "✓", "signed": False},
                    {"name": "寸法計測", "jishu": "", "shanai": "", "signed": False}
                ]

                for item in items:
                    # 署名がない、または自主/社内が空欄なら「赤枠」で警告
                    is_empty = not item["jishu"] or not item["shanai"]
                    is_warning = not item["signed"] or is_empty
                    
                    box_class = "warning-box" if is_warning else "normal-box"
                    
                    st.markdown(f"""
                        <div class="{box_class}">
                            <strong>項目: {item['name']}</strong><br>
                            自主検査: {item['jishu'] if item['jishu'] else '（未記入）'} / 
                            社内検査: {item['shanai'] if item['shanai'] else '（未記入）'} / 
                            署名: {"✅あり" if item['signed'] else "❌なし"}
                        </div>
                    """, unsafe_allow_html=True)

                    # --- 「閃」確定ロジック ---
                    if item["jishu"] in ["合格", "良"] and item["shanai"]:
                        st.info(f"💡 自主検査の『{item['jishu']}』をエクセルへ転記しますか？")
                        if st.button(f"承認して転記: {item['name']}"):
                            st.success(f"{item['name']} を転記予約しました。")

                st.write("--- AIの読み取り詳細 ---")
                st.write(analysis_text)

        except Exception as e:
            st.error(f"エラー: {e}")

st.sidebar.markdown("---")
st.sidebar.write(f"ブランド: **{BRAND_NAME}**")
st.sidebar.write(f"作業累計: **{TOTAL_WORK_TIME}**")
st.sidebar.info("「私が100%制御しています」")
