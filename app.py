import streamlit as st
import requests

# Ambil API key dari secrets
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
MODEL = "deepseek/deepseek-chat-v3-0324"
HEADERS = {
  "Authorization": f"Bearer {OPENROUTER_API_KEY}",
  "HTTP-Referer": "https://chatbot-by-dangdingdung.streamlit.app/",
  "X-Title": "AI Chatbot Streamlit"
}
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Tampilkan peringatan jika API key tidak tersedia
if not OPENROUTER_API_KEY:
    st.error("⚠️ OPENROUTER_API_KEY tidak ditemukan dalam secrets. Silakan tambahkan di Streamlit Cloud dashboard.")

st.title("🧠 AI Chatbot Bubble Style")
st.markdown(f"Powered by {MODEL} via OpenRouter 🤖")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

user_input = st.chat_input("Tulis pesan di sini...")

if user_input:
    st.chat_message("user").markdown(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    with st.spinner("Mengetik..."):
        try:
            payload = {
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_input}
                ]
            }
            
            response = requests.post(API_URL, headers=HEADERS, json=payload)
            
            if response.status_code == 200:
                bot_reply = response.json()['choices'][0]['message']['content']
            else:
                # Tampilkan detail error untuk membantu debugging
                error_message = f"Error code: {response.status_code}, Response: {response.text}"
                st.error(error_message)
                bot_reply = f"⚠️ Maaf, gagal mengambil respons dari OpenRouter. Status code: {response.status_code}"
                
        except Exception as e:
            bot_reply = f"⚠️ Terjadi kesalahan: {str(e)}"
        
        st.chat_message("assistant").markdown(bot_reply)
        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
