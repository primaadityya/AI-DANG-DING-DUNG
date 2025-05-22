import streamlit as st
import uuid
import requests
from datetime import datetime

# ------------------------- Konfigurasi Halaman --------------------------------
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------- Model & API --------------------------------------
AVAILABLE_MODELS = {
    "Deepseek v3": "deepseek/deepseek-chat-v3-0324",
    "Llama 4"    : "meta-llama/llama-4-maverick:free",
    "Gemini 2.0" : "google/gemini-2.0-flash-exp:free",
    "Mistral Nemo": "mistralai/mistral-nemo:free",
}

OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
API_URL            = "https://openrouter.ai/api/v1/chat/completions"
HEADERS            = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer" : "https://ai-dang-ding-dung.streamlit.app/",  # ganti kalau domain beda
    "X-Title"     : "AI Chatbot Streamlit",
}

# --------------------------- State Inisialisasi -------------------------------
if "chats" not in st.session_state:
    chat_id = str(uuid.uuid4())
    st.session_state.chats = {
        chat_id: {
            "title"      : "Chat Baru",
            "messages"   : [],  # list of dict {role, content, timestamp}
            "created_at" : datetime.now(),
        }
    }
    st.session_state.current_chat_id = chat_id

if "selected_model" not in st.session_state:
    st.session_state.selected_model = list(AVAILABLE_MODELS.keys())[0]

# ------------------------------ Sidebar ---------------------------------------
with st.sidebar:
    st.title("💬 Chat History")

    # ➕ Chat Baru
    if st.button("➕ Chat Baru", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.chats[new_id] = {
            "title"     : "Chat Baru",
            "messages"  : [],
            "created_at": datetime.now(),
        }
        st.session_state.current_chat_id = new_id
        st.experimental_rerun()

    st.divider()

    # Daftar chat
    for cid, data in sorted(st.session_state.chats.items(), key=lambda x: x[1]["created_at"], reverse=True):
        is_active = cid == st.session_state.current_chat_id
        btn_label = data["title"] if data["title"] != "Chat Baru" else "(untitled)"
        if st.button(btn_label, key=f"open_{cid}", type="primary" if is_active else "secondary", use_container_width=True):
            st.session_state.current_chat_id = cid
            st.experimental_rerun()
        # tombol delete kecil
        if st.button("🗑️", key=f"del_{cid}"):
            if len(st.session_state.chats) > 1:
                del st.session_state.chats[cid]
                st.session_state.current_chat_id = list(st.session_state.chats.keys())[0]
                st.experimental_rerun()
            else:
                st.error("Tidak bisa menghapus chat terakhir!")

    st.divider()

    st.subheader("🤖 Pilih Model")
    model_choice = st.selectbox("Model AI:", list(AVAILABLE_MODELS.keys()), index=list(AVAILABLE_MODELS.keys()).index(st.session_state.selected_model))
    if model_choice != st.session_state.selected_model:
        st.session_state.selected_model = model_choice
        st.experimental_rerun()

# ------------------------------ Main ------------------------------------------
current_chat   = st.session_state.chats[st.session_state.current_chat_id]
provider_model = AVAILABLE_MODELS[st.session_state.selected_model]

st.title("🤖 AI Chatbot")
st.caption(f"Model: {st.session_state.selected_model} • Provider: OpenRouter")
st.divider()

# --------------------------- AREA CHAT ----------------------------------------
# Bungkus dengan div untuk css ter-scope (jika nanti mau styling)
st.markdown("<div id='chat-area'>", unsafe_allow_html=True)

for msg in current_chat["messages"]:
    role = "assistant" if msg["role"] == "assistant" else "user"
    timestamp = msg["timestamp"].strftime("%H:%M")
    with st.chat_message(role):
        st.markdown(msg["content"])
        st.caption(timestamp)

st.markdown("</div>", unsafe_allow_html=True)

# --------------------------- Input User ---------------------------------------
user_text = st.chat_input("Ketik pesan Anda di sini…")

if user_text:
    # simpan pesan user
    current_chat["messages"].append({
        "role"     : "user",
        "content"  : user_text,
        "timestamp": datetime.now(),
    })

    # set judul jika masih default
    if current_chat["title"] == "Chat Baru":
        current_chat["title"] = user_text[:30] + ("…" if len(user_text) > 30 else "")

    # tampilkan pesan user langsung
    with st.chat_message("user"):
        st.markdown(user_text)

    # panggil API
    with st.spinner("AI sedang memikirkan jawaban…"):
        try:
            messages_api = [{"role": "system", "content": "You are a helpful assistant."}] + [
                {"role": m["role"], "content": m["content"]} for m in current_chat["messages"]
            ]
            payload = {"model": provider_model, "messages": messages_api}
            resp    = requests.post(API_URL, headers=HEADERS, json=payload, timeout=90)
            resp.raise_for_status()
            ai_reply = resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            ai_reply = f"⚠️ Terjadi kesalahan: {e}"

    # simpan & tampilkan jawaban AI
    current_chat["messages"].append({
        "role"     : "assistant",
        "content"  : ai_reply,
        "timestamp": datetime.now(),
    })
    with st.chat_message("assistant"):
        st.markdown(ai_reply)

# --------------------------- Scoped CSS (minimal) -----------------------------
# Hanya mempercantik bubble, TANPA mem‑pengaruhi elemen lain di luar #chat-area
st.markdown(
    """
    <style>
    #chat-area .stChatMessage:first-child {margin-top:0;}
    #chat-area .stChatMessage {margin-bottom:1rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------- Footer ------------------------------------------
st.divider()
st.caption(
    f"Powered by {st.session_state.selected_model} via OpenRouter • Total Chats: {len(st.session_state.chats)} • Pesan di chat ini: {len(current_chat['messages'])}"
)
