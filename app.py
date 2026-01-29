import streamlit as st
import requests
import json
import base64
from PIL import Image
import pypdfium2 as pdfium
import re
import io

# --- 1. ブランド・定数設定 ---
PROJECT_NAME = "閃 (HIRAMEKI)"
TOTAL_WORK_TIME = "4.5時間 + バグ取り4時間（REST API直結版）"

st.set_page_config(page_title=f"{PROJECT_NAME}", layout="wide")

st.markdown("""
<style>
.warning-box { border: 2px solid red; padding: 15px; border-radius: 10px; background-color: #fff0f0; margin-bottom: 15px; color: black; }
.normal-box { border: 1px solid #ddd; padding: 15px; border-radius: 10px; background-color: #f0f8ff; margin-bottom: 15px; color: black; }
</style>
""", unsafe_allow_html=True)

st.title(f"{PROJECT_NAME} - 最終通信突破版")

api_key = st.sidebar.text_input("Google API Key", type="password")
st.sidebar.write(f"作業累計: **{TOTAL_WORK_TIME}**")

def clean_num(text):
    if text is None or text == "" or text in ["―", "ー", "none", "None"]: return None
    try:
        cleaned = re.sub(r'[^0-9.\-]', '', str(text))
        return float(cleaned) if cleaned else None
    except: return None

uploaded_file = st.file_uploader("PDFまたは画像をアップロード", type=["png", "jpg", "jpeg", "pdf"])

if api_key and uploaded_file:
    if st.button("🚀 閃光解析を実行"):
        try:
            images = []
            if uploaded_file.type == "application/pdf":
                pdf = pdfium.PdfDocument(uploaded_file)
                for page in pdf: images.append(page.render(scale=3).to_pil())
            else:
                images.append(Image.open(uploaded_file))

            for page_idx, img in enumerate(images):
                st.image(img, caption=f"解析対象 ({page_idx+1}ページ目)", use_container_width=True)
                
                with st.spinner(f"ページ {page_idx+1} を精査中..."):
                    # 画像をBase64に変換
                    buffered = io.BytesIO()
                    img.save(buffered, format="JPEG")
                    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

                    # --- 【ここが肝】ライブラリを通さず、最新(v1)のAPIへ直接リクエストを送る ---
                    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
                    
                    payload = {
                        "contents": [{
                            "parts": [
                                {"text": "検査成績書の表からデータを抽出し、JSON形式のリストのみで返してください。[{\"項目\": \"A\", \"図面寸法\": \"350\", \"許容値\": \"5\", \"結果\": \"350\", \"社内\": \"なし\", \"署名\": true}] ※許容値が空欄や「ー」なら \"None\"。※署名はページ内に石田様の氏名があれば一律 true。"},
                                {"inline_data": {"mime_type": "image/jpeg", "data": img_base64}}
                            ]
                        }]
                    }
                    
                    response = requests.post(url, json=payload)
                    res_json = response.json()

                    if response.status_code == 200:
                        res_text = res_json['candidates'][0]['content']['parts'][0]['text']
                        json_match = re.search(r'\[.*\]', res_text, re.DOTALL)
                        
                        if json_match:
                            raw_data = json.loads(json_match.group())
                            st.subheader(f"【第 {page_idx+1} ページ 判定結果】")
                            for item in raw_data:
                                base = clean_num(item.get("図面寸法"))
                                tol = clean_num(item.get("許容値"))
                                val = clean_num(item.get("結果"))
                                judge = "合格" if (base and val and (base-tol if tol else base) <= val <= (base+tol if tol else base)) else "不合格"
                                is_ok = (judge == "合格")
                                has_check = item.get("社内") not in ["なし", "空欄", "ー", "―", "", None]
                                has_sign = item.get("署名", False)
                                box_style = "normal-box" if (is_ok and has_check and has_sign) else "warning-box"
                                
                                st.markdown(f"""<div class="{box_style}">
                                    <strong>項目: {item['項目']}</strong><br>
                                    実測結果: {val} / 判定: {judge}<br>
                                    社内検査: {item.get('社内')} / 署名: {"✅確認済" if has_sign else "❌署名漏れ"}
                                    </div>""", unsafe_allow_html=True)
                        else:
                            st.error("JSON解析エラー")
                    else:
                        st.error(f"APIエラー: {res_json}")
        except Exception as e:
            st.error(f"システムエラー: {e}")
