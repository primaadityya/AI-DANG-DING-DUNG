import streamlit as st
import requests
from datetime import datetime

OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
MODEL = "deepseek/deepseek-chat-v3-0324"
HEADERS = {
  "Authorization": f"Bearer {OPENROUTER_API_KEY}",
  "HTTP-Referer": "https://ai-dang-ding-dung.streamlit.app/",
  "X-Title": "AI Chatbot Streamlit"
}
API_URL = "https://openrouter.ai/api/v1/chat/completions"

st.title("🧠 AI Chatbot Bubble Style")
st.markdown(f"Powered by {MODEL} via OpenRouter 🤖")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Tampilkan chat history dengan st.chat_message (mirip ChatGPT)
for chat in st.session_state.chat_history:
    role = chat["role"]
    content = chat["content"]
    timestamp = chat.get("timestamp", "")
    with st.chat_message(role):
        st.markdown(content)
        if role == "assistant":
            st.caption(f"{timestamp}")
            st.code(content, language=None)
        elif role == "user":
            st.caption(f"{timestamp}")

user_input = st.chat_input("Tulis pesan di sini...")

if user_input:
    now = datetime.now().strftime("%H:%M")
    st.session_state.chat_history.append({"role": "user", "content": user_input, "timestamp": now})
    with st.spinner("Mengetik..."):
        try:
            payload = {
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    *[
                        {"role": c["role"], "content": c["content"]}
                        for c in st.session_state.chat_history if c["role"] in ["user", "assistant"]
                    ],
                ]
            }
            response = requests.post(API_URL, headers=HEADERS, json=payload)
            if response.status_code == 200:
                bot_reply = response.json()['choices'][0]['message']['content']
            else:
                error_message = f"Error code: {response.status_code}, Response: {response.text}"
                st.error(error_message)
                bot_reply = f"⚠️ Maaf, gagal mengambil respons dari OpenRouter. Status code: {response.status_code}"
        except Exception as e:
            bot_reply = f"⚠️ Terjadi kesalahan: {str(e)}"
        now = datetime.now().strftime("%H:%M")
        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply, "timestamp": now})
