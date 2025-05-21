import streamlit as st
import requests
from datetime import datetime
import base64

# Custom CSS agar mirip ChatGPT (bubble, layout tengah, salin, waktu, indent)
st.markdown(
    """
    <style>
    .centered-container {
        max-width: 600px;
        margin: 0 auto;
        padding-top: 1.5rem;
    }
    .chat-container {
        max-height: 70vh;
        overflow-y: auto;
        padding: 1rem 0.5rem 1rem 0.5rem;
        background: #f7f7f8;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    }
    .bubble {
        display: flex;
        align-items: flex-end;
        margin-bottom: 0.7rem;
        position: relative;
    }
    .bubble.user {
        flex-direction: row-reverse;
        justify-content: flex-end;
        margin-left: 60px;
    }
    .bubble.assistant {
        justify-content: flex-start;
        margin-right: 60px;
    }
    .bubble .avatar {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        margin: 0 0.5rem;
        background: #e0e0e0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        flex-shrink: 0;
    }
    .bubble .msg {
        max-width: 70vw;
        padding: 0.7rem 1.1rem;
        border-radius: 16px;
        font-size: 1.08rem;
        line-height: 1.5;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        position: relative;
        word-break: break-word;
    }
    .bubble.user .msg {
        background: #0084ff;
        color: #fff;
        border-bottom-right-radius: 4px;
        border-top-right-radius: 4px;
        border-top-left-radius: 16px;
        border-bottom-left-radius: 16px;
    }
    .bubble.assistant .msg {
        background: #fff;
        color: #222;
        border-bottom-left-radius: 4px;
        border-top-left-radius: 4px;
        border-top-right-radius: 16px;
        border-bottom-right-radius: 16px;
        border: 1px solid #e0e0e0;
    }
    .bubble .timestamp {
        font-size: 0.8rem;
        color: #888;
        margin: 0 0.5rem;
        align-self: flex-end;
        min-width: 70px;
        text-align: right;
    }
    .bubble .copy-btn {
        background: none;
        border: none;
        color: #888;
        font-size: 1.1rem;
        cursor: pointer;
        margin-left: 0.3rem;
        margin-bottom: 0.1rem;
        transition: color 0.2s;
    }
    .bubble .copy-btn:hover {
        color: #0084ff;
    }
    .stChatInputContainer {margin-top: 0.5rem;}
    </style>
    """,
    unsafe_allow_html=True
)

# Ambil API key dari secrets
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
MODEL = "deepseek/deepseek-chat-v3-0324"
HEADERS = {
  "Authorization": f"Bearer {OPENROUTER_API_KEY}",
  "HTTP-Referer": "https://ai-dang-ding-dung.streamlit.app/",
  "X-Title": "AI Chatbot Streamlit"
}
API_URL = "https://openrouter.ai/api/v1/chat/completions"

st.markdown('<div class="centered-container">', unsafe_allow_html=True)
st.title("🧠 AI Chatbot Bubble Style")
st.markdown(f"Powered by {MODEL} via OpenRouter 🤖")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Bubble chat area
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for idx, chat in enumerate(st.session_state.chat_history):
    role = chat["role"]
    content = chat["content"]
    timestamp = chat.get("timestamp", "")
    if not timestamp:
        timestamp = datetime.now().strftime("%H:%M")
        chat["timestamp"] = timestamp
    if role == "user":
        avatar = "<span class='avatar' style='background:#0084ff;color:#fff;'>🧑</span>"
        bubble_class = "bubble user"
        copy_btn = ""
    else:
        avatar = "<span class='avatar'>🤖</span>"
        bubble_class = "bubble assistant"
        # Tombol salin (copy) untuk bot
        copy_btn = f"<button class='copy-btn' onclick=\"navigator.clipboard.writeText(`{content.replace('`','\\`')}`)\">📋</button>"
    st.markdown(f"""
    <div class='{bubble_class}'>
        {avatar}
        <div class='msg'>{content}{copy_btn}</div>
        <div class='timestamp'>{timestamp}</div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

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
        st.experimental_rerun()
st.markdown('</div>', unsafe_allow_html=True)
