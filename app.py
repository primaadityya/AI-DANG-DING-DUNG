import streamlit as st
import requests
import uuid
from datetime import datetime
import json

# Konfigurasi halaman
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk styling yang responsive terhadap dark/light theme
st.markdown("""
<style>
    .main-content {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px; /* Increased padding for better spacing */
        font-size: 14px; /* Consistent font size */
    }
    
    .user-message, .assistant-message {
        padding: 15px 20px;
        border-radius: 15px;
        margin: 10px 0; /* Spacing between messages */
        max-width: 80%; /* Limit width for better readability */
        overflow-wrap: break-word; /* Prevent overflow */
    }

    .user-message {
        background-color: var(--background-color-secondary);
        color: var(--text-color);
        margin-left: auto; /* Align user messages to the right */
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
    }

    .assistant-message {
        background-color: var(--background-color);
        color: var(--text-color);
        margin-right: auto; /* Align assistant messages to the left */
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
    }

    .chat-input {
        margin-top: 20px;
    }
    
    .message-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 12px;
        color: var(--secondary-text-color);
    }

    .message-avatar {
        width: 30px; /* Slightly larger avatars */
        height: 30px;
        border-radius: 50%;
    }

</style>
""", unsafe_allow_html=True)

# Main chat display (inside the chat container)
with chat_container:
    for message in current_chat["messages"]:
        timestamp = message.get("timestamp", datetime.now()).strftime("%H:%M")

        if message["role"] == "user":
            st.markdown(f"""
            <div class="user-message">
                <div class="message-header">
                    <span><div class="user-avatar message-avatar">YOU</div><strong>Anda</strong> • {timestamp}</span>
                    <div class="message-actions">
                        <button class="action-btn" onclick="navigator.clipboard.writeText('{message['content'].replace("'", "\\'")}')">📋 Copy</button>
                    </div>
                </div>
                <div>{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="assistant-message">
                <div class="message-header">
                    <span><div class="ai-avatar message-avatar">AI</div><strong>AI Assistant</strong> • {timestamp}</span>
                    <div class="message-actions">
                        <button class="action-btn" onclick="navigator.clipboard.writeText('{message['content'].replace("'", "\\'")}')">📋 Copy</button>
                    </div>
                </div>
                <div>{message["content"]}</div>
            </div>
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

if "regenerate_last" not in st.session_state:
    st.session_state.regenerate_last = False

# Sidebar
with st.sidebar:
    st.title("💬 Chat History")
    
    # Tombol chat baru
    if st.button("➕ Chat Baru", key="new_chat", help="Mulai percakapan baru", use_container_width=True):
        chat_id = str(uuid.uuid4())
        st.session_state.current_chat_id = chat_id
        st.session_state.chats[chat_id] = {
            "title": "Chat Baru",
            "messages": [],
            "created_at": datetime.now()
        }
        st.rerun()
    
    st.markdown("---")
    
    # Daftar chat
    for chat_id, chat_data in sorted(st.session_state.chats.items(), 
                                   key=lambda x: x[1]["created_at"], reverse=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            # Buat preview dari pesan pertama user
            title = chat_data["title"]
            if chat_data["messages"] and len(chat_data["messages"]) > 0:
                first_user_msg = next((msg["content"] for msg in chat_data["messages"] 
                                     if msg["role"] == "user"), "Chat Baru")
                if len(first_user_msg) > 30:
                    title = first_user_msg[:30] + "..."
                else:
                    title = first_user_msg
            
            is_active = chat_id == st.session_state.current_chat_id
            
            if st.button(
                title,
                key=f"chat_{chat_id}",
                help=f"Buka chat - {chat_data['created_at'].strftime('%d/%m/%Y %H:%M')}",
                type="primary" if is_active else "secondary",
                use_container_width=True
            ):
                st.session_state.current_chat_id = chat_id
                st.rerun()
        
        with col2:
            if st.button("🗑️", key=f"delete_{chat_id}", help="Hapus chat"):
                if len(st.session_state.chats) > 1:
                    del st.session_state.chats[chat_id]
                    if chat_id == st.session_state.current_chat_id:
                        # Pilih chat pertama yang tersedia
                        st.session_state.current_chat_id = list(st.session_state.chats.keys())[0]
                    st.rerun()
                else:
                    st.error("Tidak bisa menghapus chat terakhir!")

    st.markdown("---")
    
    # Model selector
    st.subheader("🤖 Pilih Model")
    selected_model = st.selectbox(
        "Model AI:",
        options=list(AVAILABLE_MODELS.keys()),
        index=list(AVAILABLE_MODELS.keys()).index(st.session_state.selected_model),
        key="model_selector"
    )
    
    if selected_model != st.session_state.selected_model:
        st.session_state.selected_model = selected_model
        st.rerun()

# Main content
current_chat = st.session_state.chats[st.session_state.current_chat_id]
current_model = AVAILABLE_MODELS[st.session_state.selected_model]

# Header
st.title("🤖 AI Chatbot")
st.markdown(f"**Model:** {st.session_state.selected_model} | **Provider:** OpenRouter")
st.markdown("---")

# Container untuk chat
chat_container = st.container()

with chat_container:
    # Tampilkan riwayat chat
    for i, message in enumerate(current_chat["messages"]):
        timestamp = message.get("timestamp", datetime.now()).strftime("%H:%M")
        
        if message["role"] == "user":
            st.markdown(f"""
            <div class="user-message">
                <div class="message-header">
                    <span><div class="user-avatar message-avatar">YOU</div><strong>Anda</strong> • {timestamp}</span>
                    <div class="message-actions">
                        <button class="action-btn" onclick="navigator.clipboard.writeText('{message['content'].replace("'", "\\'")}')">📋 Copy</button>
                    </div>
                </div>
                <div>{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="assistant-message">
                <div class="message-header">
                    <span><div class="ai-avatar message-avatar">AI</div><strong>AI Assistant</strong> • {timestamp}</span>
                    <div class="message-actions">
                        <button class="action-btn" onclick="navigator.clipboard.writeText('{message['content'].replace("'", "\\'")}')">📋 Copy</button>
                    </div>
                </div>
                <div>{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)

# Tombol regenerate untuk pesan AI terakhir
if (current_chat["messages"] and 
    current_chat["messages"][-1]["role"] == "assistant"):
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Regenerate Response", key="regenerate_btn", 
                   help="Generate ulang respons terakhir", use_container_width=True):
            st.session_state.regenerate_last = True
            st.rerun()

# Input chat di bagian bawah
st.markdown("---")
user_input = st.chat_input("Ketik pesan Anda di sini...")

# Handle regenerate
if st.session_state.regenerate_last:
    st.session_state.regenerate_last = False
    
    # Hapus pesan AI terakhir
    if current_chat["messages"] and current_chat["messages"][-1]["role"] == "assistant":
        current_chat["messages"].pop()
        
        # Ambil pesan user terakhir untuk regenerate
        last_user_message = None
        for msg in reversed(current_chat["messages"]):
            if msg["role"] == "user":
                last_user_message = msg["content"]
                break
        
        if last_user_message:
            user_input = last_user_message  # Set sebagai input untuk diproses

if user_input:
    # Jika bukan regenerate, tambahkan pesan user baru
    if not st.session_state.regenerate_last:
        user_message = {
            "role": "user", 
            "content": user_input,
            "timestamp": datetime.now()
        }
        current_chat["messages"].append(user_message)
        
        # Update title chat jika ini pesan pertama
        if len([msg for msg in current_chat["messages"] if msg["role"] == "user"]) == 1:
            if len(user_input) > 30:
                current_chat["title"] = user_input[:30] + "..."
            else:
                current_chat["title"] = user_input
    
    # Tampilkan loading spinner
    with st.spinner("AI sedang memikirkan jawaban..."):
        try:
            # Siapkan riwayat percakapan untuk API
            messages_for_api = [{"role": "system", "content": "You are a helpful assistant."}]
            for msg in current_chat["messages"]:
                messages_for_api.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            payload = {
                "model": current_model,
                "messages": messages_for_api
            }
            
            response = requests.post(API_URL, headers=HEADERS, json=payload)
            
            if response.status_code == 200:
                bot_reply = response.json()['choices'][0]['message']['content']
            else:
                bot_reply = f"⚠️ Error {response.status_code}: {response.text}"
                
        except Exception as e:
            bot_reply = f"⚠️ Terjadi kesalahan: {str(e)}"
    
    # Tambahkan respons AI ke chat history
    ai_message = {
        "role": "assistant",
        "content": bot_reply,
        "timestamp": datetime.now()
    }
    current_chat["messages"].append(ai_message)
    
    # Rerun untuk update tampilan
    st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: var(--secondary-text-color); font-size: 12px;'>"
    f"Powered by {st.session_state.selected_model} via OpenRouter • "
    f"Total Chats: {len(st.session_state.chats)} • "
    f"Messages in current chat: {len(current_chat['messages'])}"
    "</div>",
    unsafe_allow_html=True
)
