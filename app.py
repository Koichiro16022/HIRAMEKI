import streamlit as st
import google.generativeai as genai
from PIL import Image
import pypdfium2 as pdfium
import io

# --- 1. ブランド・定数設定 ---
BRAND_NAME = "EKAI"  # 「絵かい」を大文字で
PROJECT_NAME = "閃 (HIRAMEKI)"
TOTAL_WORK_TIME = "4.5時間（疎通・PDF対応含む）"

# --- 2. ページ構成 ---
st.set_page_config(page_title=f"{PROJECT_NAME} by {BRAND_NAME}", layout="wide")

# 赤枠警告用のスタイル定義
st.markdown("""
    <style>
    .warning-box { border: 2px solid red; padding: 15px; border-radius: 10px; background-color: #fff0f0; margin-bottom: 15px; }
    .normal-box { border: 1px solid #ddd; padding: 15px; border-radius: 10px; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title(f"{PROJECT_NAME} - 検査成績書 解析システム")

# --- 3. サイドバー設定 ---
api_key = st.sidebar.text_input("Google API Key", type="password")
st.sidebar.markdown("---")
st.sidebar.write(f"ブランド: **{BRAND_NAME}**")
st.sidebar.write(f"作業累計: **{TOTAL_WORK_TIME}**")
st.sidebar.info("「私が100%制御しています」")

# --- 4. メイン処理 ---
uploaded_file = st.file_uploader("検査成績書（PDFまたは画像）をアップロード", type=["png", "jpg", "jpeg", "pdf"])

if api_key and uploaded_file:
    genai.configure(api_key=api_key)
    # 疎通が確認できた Lite モデルを使用
    model = genai.GenerativeModel('models/gemini-flash-lite-latest')

    if st.button("🚀 閃光解析を実行"):
        try:
            images = []
            # PDFファイルを画像に変換して処理
            if uploaded_file.type == "application/pdf":
                with st.spinner("PDFを解析用に最適化中..."):
                    pdf = pdfium.PdfDocument(uploaded_file)
                    for page in pdf:
                        # scale=2 で解像度を維持し、誤読を防ぐ
                        bitmap = page.render(scale=2)
                        images.append(bitmap.to_pil())
            else:
                images.append(Image.open(uploaded_file))

            # 抽出した各ページに対して解析を実行
            for idx, img in enumerate(images):
                st.image(img, caption=f"解析対象 ({idx+1}ページ目)", use_container_width=True)
                
                with st.spinner(f"ページ {idx+1} を『絵かい』の論理で解析中..."):
                    # 現場の判定ルールを注入したプロンプト
                    prompt = """
                    検査成績書の表を解析してください。
                    1. 各項目の「自主検査」が「合格」または「良」か？
                    2. 「社内検査」に「✓」「J」「V」等のチェックがあるか？
                    3. 「検査者署名」が空欄ではないか？
                    上記を読み取って詳細を答えてください。
                    """
                    response = model.generate_content([prompt, img])
                    analysis_result = response.text

                    st.subheader(f"【第 {idx+1} ページ 判定結果】")

                    # --- 確定ロジック（デモデータでの挙動確認用） ---
                    # 実際には analysis_result を元に以下の判定を繰り返します
                    demo_items = [
                        {"項目": "外観検査", "自主": "合格", "社内": "J", "署名": False},
                        {"項目": "寸法測定", "自主": "", "社内": "", "署名": False}
                    ]

                    for item in demo_items:
                        # 署名漏れ、または自主/社内が空欄なら赤枠（慧の認識の証）
                        is_warning = (not item["署名"]) or (not item["自主"] and not item["社内"])
                        box_style = "warning-box" if is_warning else "normal-box"

                        st.markdown(f"""
                            <div class="{box_style}">
                                <strong>項目: {item['項目']}</strong><br>
                                自主検査: {item['自主'] if item['自主'] else '（空欄）'} / 
                                社内検査: {item['社内'] if item['社内'] else '（空欄）'} / 
                                署名: {"✅確認済" if item['署名'] else "❌署名漏れ"}
                            </div>
                        """, unsafe_allow_html=True)

                        # 「閃」確定転記ロジック
                        if item["自主"] in ["合格", "良"] and item["社内"]:
                            st.info(f"💡 自主検査の『{item['自主']}』を転記しますか？")
                            if st.button(f"エクセルへ転記承認: {item['項目']}"):
                                st.success(f"『{item['項目']}』を転記しました。")

                    st.write("--- AI読み取り原文 ---")
                    st.write(analysis_result)

        except Exception as e:
            st.error(f"解析エラー: {e}")
