import streamlit as st
import requests
import uuid
from datetime import datetime
import json
import time

# Konfigurasi halaman
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS yang diperbaiki
st.markdown("""
<style>
    /* Reset dan base styling */
    .stApp {
        max-width: none !important;
    }
    
    .main .block-container {
        padding-top: 1rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Message styling */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0 8px 25%;
        position: relative;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        word-wrap: break-word;
    }
    
    .assistant-message {
        background: #f1f3f4;
        color: #202124;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 25% 8px 0;
        position: relative;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        word-wrap: break-word;
    }
    
    /* Dark mode support */
    [data-theme="dark"] .assistant-message {
        background: #2d2d2d;
        color: #e8eaed;
    }
    
    /* Message header */
    .msg-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
        font-size: 11px;
        opacity: 0.7;
    }
    
    .msg-info {
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    .msg-actions {
        display: flex;
        gap: 4px;
        align-items: center;
    }
    
    /* Avatar styling */
    .avatar {
        width: 16px;
        height: 16px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 8px;
        font-weight: bold;
        color: white;
    }
    
    .user-avatar {
        background: rgba(255,255,255,0.3);
    }
    
    .ai-avatar {
        background: linear-gradient(135deg, #ff6b6b, #ee5a24);
    }
    
    /* Button styling */
    .msg-btn {
        background: rgba(255,255,255,0.2);
        border: none;
        border-radius: 4px;
        padding: 2px 6px;
        font-size: 10px;
        cursor: pointer;
        transition: all 0.2s;
        opacity: 0.7;
    }
    
    .msg-btn:hover {
        opacity: 1;
        background: rgba(255,255,255,0.3);
    }
    
    /* Message footer for regenerate */
    .msg-footer {
        margin-top: 8px;
        text-align: right;
    }
    
    .regen-btn {
        background: rgba(0,0,0,0.1);
        border: none;
        border-radius: 4px;
        padding: 2px 6px;
        font-size: 10px;
        cursor: pointer;
        transition: all 0.2s;
        opacity: 0.6;
    }
    
    .regen-btn:hover {
        opacity: 1;
        background: rgba(0,0,0,0.2);
    }
    
    /* Typing animation */
    .typing-indicator {
        display: inline-flex;
        align-items: center;
        gap: 2px;
    }
    
    .typing-dot {
        width: 4px;
        height: 4px;
        border-radius: 50%;
        background: currentColor;
        animation: typing 1.4s ease-in-out infinite;
    }
    
    .typing-dot:nth-child(1) { animation-delay: 0s; }
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes typing {
        0%, 60%, 100% { opacity: 0.3; transform: scale(0.8); }
        30% { opacity: 1; transform: scale(1); }
    }
    
    /* Hide Streamlit elements */
    .stDeployButton {
        display: none;
    }
    
    #MainMenu {
        visibility: hidden;
    }
    
    footer {
        visibility: hidden;
    }
    
    header {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)

# Definisi model yang tersedia
AVAILABLE_MODELS = {
    "Deepseek v3": "deepseek/deepseek-chat-v3-0324",
    "Llama 4": "meta-llama/llama-4-maverick:free", 
    "Gemini 2.0": "google/gemini-2.0-flash-exp:free",
    "Mistral Nemo": "mistralai/mistral-nemo:free"
}

# Ambil API key dari secrets
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "https://ai-dang-ding-dung.streamlit.app/",
    "X-Title": "AI Chatbot Streamlit"
}

API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Inisialisasi session state
if "chats" not in st.session_state:
    st.session_state.chats = {}
    
if "current_chat_id" not in st.session_state:
    chat_id = str(uuid.uuid4())
    st.session_state.current_chat_id = chat_id
    st.session_state.chats[chat_id] = {
        "title": "Chat Baru",
        "messages": [],
        "created_at": datetime.now()
    }

if "selected_model" not in st.session_state:
    st.session_state.selected_model = "Deepseek v3"

if "is_typing" not in st.session_state:
    st.session_state.is_typing = False

# Fungsi untuk menampilkan pesan
def display_message(message, msg_type, timestamp, is_last_ai=False, is_typing=False):
    """Display message dengan styling yang konsisten"""
    if msg_type == "user":
        content = f"""
        <div class="user-message">
            <div class="msg-header">
                <div class="msg-info">
                    <div class="avatar user-avatar">U</div>
                    <span>Anda • {timestamp}</span>
                </div>
                <div class="msg-actions">
                    <button class="msg-btn" onclick="copyText('{message.replace("'", "\\'")}')">📋</button>
                </div>
            </div>
            <div>{message}</div>
        </div>
        """
    else:
        typing_indicator = ""
        if is_typing:
            typing_indicator = ' <span class="typing-indicator"><span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span></span>'
        
        regen_btn = ""
        if is_last_ai and not is_typing:
            regen_btn = '<div class="msg-footer"><button class="regen-btn" onclick="regenerateResponse()">🔄</button></div>'
        
        content = f"""
        <div class="assistant-message">
            <div class="msg-header">
                <div class="msg-info">
                    <div class="avatar ai-avatar">AI</div>
                    <span>AI Assistant • {timestamp}</span>
                </div>
                <div class="msg-actions">
                    <button class="msg-btn" onclick="copyText('{message.replace("'", "\\'")}')">📋</button>
                </div>
            </div>
            <div>{message}{typing_indicator}</div>
            {regen_btn}
        </div>
        """
    
    return content

# Fungsi untuk simulasi typing effect
def simulate_typing_effect(text, placeholder):
    """Simulasi mengetik kata demi kata"""
    words = text.split()
    current_text = ""
    
    for i, word in enumerate(words):
        current_text += word + " "
        timestamp = datetime.now().strftime("%H:%M")
        
        # Tampilkan dengan typing indicator jika belum selesai
        is_typing = (i < len(words) - 1)
        content = display_message(current_text.strip(), "assistant", timestamp, True, is_typing)
        placeholder.markdown(content, unsafe_allow_html=True)
        
        # Delay untuk efek mengetik
        time.sleep(0.1)
    
    return current_text.strip()

# JavaScript untuk interaksi
st.markdown("""
<script>
function copyText(text) {
    navigator.clipboard.writeText(text).then(function() {
        console.log('Text copied to clipboard');
    });
}

function regenerateResponse() {
    // Trigger regenerate melalui session state
    window.parent.postMessage({
        type: 'streamlit:setComponentValue',
        value: {action: 'regenerate'}
    }, '*');
}
</script>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("💬 Chat History")
    
    # Tombol chat baru
    if st.button("➕ Chat Baru", use_container_width=True):
        chat_id = str(uuid.uuid4())
        st.session_state.current_chat_id = chat_id
        st.session_state.chats[chat_id] = {
            "title": "Chat Baru",
            "messages": [],
            "created_at": datetime.now()
        }
        st.rerun()
    
    st.divider()
    
    # Daftar chat
    for chat_id, chat_data in sorted(st.session_state.chats.items(), 
                                   key=lambda x: x[1]["created_at"], reverse=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            # Buat preview dari pesan pertama user
            title = "Chat Baru"
            if chat_data["messages"]:
                first_user_msg = next((msg["content"] for msg in chat_data["messages"] 
                                     if msg["role"] == "user"), "Chat Baru")
                title = first_user_msg[:30] + "..." if len(first_user_msg) > 30 else first_user_msg
            
            if st.button(
                title,
                key=f"chat_{chat_id}",
                help=f"Dibuat: {chat_data['created_at'].strftime('%d/%m/%Y %H:%M')}",
                type="primary" if chat_id == st.session_state.current_chat_id else "secondary",
                use_container_width=True
            ):
                st.session_state.current_chat_id = chat_id
                st.rerun()
        
        with col2:
            if st.button("🗑️", key=f"delete_{chat_id}", help="Hapus chat"):
                if len(st.session_state.chats) > 1:
                    del st.session_state.chats[chat_id]
                    if chat_id == st.session_state.current_chat_id:
                        st.session_state.current_chat_id = list(st.session_state.chats.keys())[0]
                    st.rerun()

    st.divider()
    
    # Model selector
    st.subheader("🤖 Model AI")
    selected_model = st.selectbox(
        "Pilih model:",
        options=list(AVAILABLE_MODELS.keys()),
        index=list(AVAILABLE_MODELS.keys()).index(st.session_state.selected_model)
    )
    
    if selected_model != st.session_state.selected_model:
        st.session_state.selected_model = selected_model
        st.rerun()

# Main content
st.title("🤖 AI Chatbot")
st.caption(f"Model: {st.session_state.selected_model} | Provider: OpenRouter")

current_chat = st.session_state.chats[st.session_state.current_chat_id]

# Tampilkan chat history
chat_container = st.container()
with chat_container:
    for i, message in enumerate(current_chat["messages"]):
        timestamp = message.get("timestamp", datetime.now()).strftime("%H:%M")
        is_last_ai = (i == len(current_chat["messages"]) - 1 and message["role"] == "assistant")
        
        content = display_message(
            message["content"], 
            message["role"], 
            timestamp, 
            is_last_ai
        )
        st.markdown(content, unsafe_allow_html=True)

# Tombol regenerate terpisah untuk debugging
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("🔄 Regenerate", key="manual_regen", help="Generate ulang respons terakhir"):
        if (current_chat["messages"] and 
            current_chat["messages"][-1]["role"] == "assistant"):
            # Hapus pesan AI terakhir
            current_chat["messages"].pop()
            st.rerun()

# Input area
user_input = st.chat_input("Ketik pesan Anda...")

# Proses input user
if user_input:
    # Tambahkan pesan user
    user_message = {
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now()
    }
    current_chat["messages"].append(user_message)
    
    # Update judul chat
    if len([msg for msg in current_chat["messages"] if msg["role"] == "user"]) == 1:
        current_chat["title"] = user_input[:30] + "..." if len(user_input) > 30 else user_input
    
    # Refresh untuk menampilkan pesan user
    st.rerun()

# Proses respons AI jika ada pesan user tanpa respons
if (current_chat["messages"] and 
    current_chat["messages"][-1]["role"] == "user" and 
    not st.session_state.is_typing):
    
    st.session_state.is_typing = True
    
    # Placeholder untuk respons AI
    response_placeholder = st.empty()
    
    try:
        # Siapkan messages untuk API
        messages_for_api = [{"role": "system", "content": "You are a helpful assistant."}]
        for msg in current_chat["messages"]:
            messages_for_api.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Panggil API
        current_model = AVAILABLE_MODELS[st.session_state.selected_model]
        payload = {
            "model": current_model,
            "messages": messages_for_api
        }
        
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        
        if response.status_code == 200:
            ai_response = response.json()['choices'][0]['message']['content']
        else:
            ai_response = f"⚠️ Error {response.status_code}: {response.text}"
        
        # Simulasi typing effect
        final_response = simulate_typing_effect(ai_response, response_placeholder)
        
        # Simpan respons AI
        ai_message = {
            "role": "assistant",
            "content": final_response,
            "timestamp": datetime.now()
        }
        current_chat["messages"].append(ai_message)
        
    except Exception as e:
        error_msg = f"⚠️ Terjadi kesalahan: {str(e)}"
        timestamp = datetime.now().strftime("%H:%M")
        content = display_message(error_msg, "assistant", timestamp, True)
        response_placeholder.markdown(content, unsafe_allow_html=True)
        
        # Simpan error message
        ai_message = {
            "role": "assistant",
            "content": error_msg,
            "timestamp": datetime.now()
        }
        current_chat["messages"].append(ai_message)
    
    finally:
        st.session_state.is_typing = False
        time.sleep(1)
        st.rerun()

# Footer
st.divider()
st.markdown(
    f"<div style='text-align: center; color: #666; font-size: 12px;'>"
    f"Total Chats: {len(st.session_state.chats)} • "
    f"Messages: {len(current_chat['messages'])}"
    f"</div>",
    unsafe_allow_html=True
)
