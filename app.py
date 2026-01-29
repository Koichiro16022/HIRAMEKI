import streamlit as st
import requests

st.title("閃 (HIRAMEKI) - モデル生存確認テスト")

api_key = st.sidebar.text_input("Google API Key", type="password")

if api_key:
    if st.button("🔍 稼働中のモデルをリストアップ"):
        # Googleの窓口から、現在使用可能な全モデルを取得
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        
        try:
            response = requests.get(url)
            res_json = response.json()
            
            if response.status_code == 200:
                st.success("接続成功！使用可能なモデル一覧:")
                # モデル名だけを抽出して表示
                models = [m['name'] for m in res_json.get('models', [])]
                for m_name in models:
                    st.code(m_name)
            else:
                st.error(f"エラーが発生しました: {res_json}")
        except Exception as e:
            st.error(f"通信エラー: {e}")
else:
    st.info("左にAPIキーを入力してください。")
