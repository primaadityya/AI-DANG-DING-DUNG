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

# Custom CSS untuk styling mirip Claude
st.markdown("""
<style>
    .main-content {
        max-width: 800px;
        margin: 0 auto;
        padding: 0 20px;
    }
    
    .user-message {
        background-color: #f0f2f6;
        padding: 15px 20px;
        border-radius: 18px;
        margin: 10px 0;
        margin-left: 20%;
        position: relative;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .assistant-message {
        background-color: white;
        padding: 15px 20px;
        border-radius: 18px;
        margin: 10px 0;
        margin-right: 20%;
        position: relative;
        border: 1px solid #e1e5e9;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    .message-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        font-size: 12px;
        color: #6b7280;
    }
    
    .copy-btn {
        background: none;
        border: none;
        cursor: pointer;
        padding: 4px 8px;
        border-radius: 4px;
        color: #6b7280;
        font-size: 12px;
    }
    
    .copy-btn:hover {
        background-color: #f3f4f6;
    }
    
    .chat-title {
        font-size: 14px;
        font-weight: 500;
        color: #374151;
        margin-bottom: 5px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .chat-preview {
        font-size: 12px;
        color: #6b7280;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .sidebar-section {
        margin-bottom: 20px;
    }
    
    .new-chat-btn {
        width: 100%;
        padding: 10px;
        background-color: #3b82f6;
        color: white;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-weight: 500;
    }
    
    .chat-item {
        padding: 12px;
        border-radius: 6px;
        cursor: pointer;
        margin-bottom: 4px;
        border: 1px solid transparent;
    }
    
    .chat-item:hover {
        background-color: #f3f4f6;
    }
    
    .chat-item.active {
        background-color: #eff6ff;
        border-color: #3b82f6;
    }
    
    .delete-chat-btn {
        background: none;
        border: none;
        color: #ef4444;
        cursor: pointer;
        float: right;
        padding: 2px 6px;
        border-radius: 3px;
        font-size: 12px;
    }
    
    .delete-chat-btn:hover {
        background-color: #fee2e2;
    }
</style>
""", unsafe_allow_html=True)

# Ambil API key dari secrets
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
MODEL = "deepseek/deepseek-chat-v3-0324"
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

# Sidebar
with st.sidebar:
    st.title("💬 Chat History")
    
    # Tombol chat baru
    if st.button("➕ Chat Baru", key="new_chat", help="Mulai percakapan baru"):
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
                type="primary" if is_active else "secondary"
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

# Main content
current_chat = st.session_state.chats[st.session_state.current_chat_id]

# Header
st.title("🤖 AI Chatbot")
st.markdown(f"**Model:** {MODEL} | **Provider:** OpenRouter")
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
                    <span><strong>Anda</strong> • {timestamp}</span>
                    <button class="copy-btn" onclick="navigator.clipboard.writeText('{message['content'].replace("'", "\\'")}')">📋 Copy</button>
                </div>
                <div>{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="assistant-message">
                <div class="message-header">
                    <span><strong>AI Assistant</strong> • {timestamp}</span>
                    <button class="copy-btn" onclick="navigator.clipboard.writeText('{message['content'].replace("'", "\\'")}')">📋 Copy</button>
                </div>
                <div>{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)

# Input chat di bagian bawah
st.markdown("---")
user_input = st.chat_input("Ketik pesan Anda di sini...")

if user_input:
    # Tambahkan pesan user
    user_message = {
        "role": "user", 
        "content": user_input,
        "timestamp": datetime.now()
    }
    current_chat["messages"].append(user_message)
    
    # Update title chat jika ini pesan pertama
    if len(current_chat["messages"]) == 1:
        if len(user_input) > 30:
            current_chat["title"] = user_input[:30] + "..."
        else:
            current_chat["title"] = user_input
    
    # Tampilkan pesan user
    with chat_container:
        timestamp = user_message["timestamp"].strftime("%H:%M")
        st.markdown(f"""
        <div class="user-message">
            <div class="message-header">
                <span><strong>Anda</strong> • {timestamp}</span>
                <button class="copy-btn" onclick="navigator.clipboard.writeText('{user_input.replace("'", "\\'")}')">📋 Copy</button>
            </div>
            <div>{user_input}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Dapatkan respons dari AI
    with st.spinner("AI sedang mengetik..."):
        try:
            # Siapkan riwayat percakapan untuk API
            messages_for_api = [{"role": "system", "content": "You are a helpful assistant."}]
            for msg in current_chat["messages"]:
                messages_for_api.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            payload = {
                "model": MODEL,
                "messages": messages_for_api
            }
            
            response = requests.post(API_URL, headers=HEADERS, json=payload)
            
            if response.status_code == 200:
                bot_reply = response.json()['choices'][0]['message']['content']
            else:
                error_message = f"Error {response.status_code}: {response.text}"
                st.error(error_message)
                bot_reply = f"⚠️ Maaf, terjadi kesalahan saat menghubungi AI. Status: {response.status_code}"
                
        except Exception as e:
            bot_reply = f"⚠️ Terjadi kesalahan: {str(e)}"
        
        # Tambahkan respons AI
        ai_message = {
            "role": "assistant",
            "content": bot_reply,
            "timestamp": datetime.now()
        }
        current_chat["messages"].append(ai_message)
        
        # Tampilkan respons AI
        with chat_container:
            timestamp = ai_message["timestamp"].strftime("%H:%M")
            st.markdown(f"""
            <div class="assistant-message">
                <div class="message-header">
                    <span><strong>AI Assistant</strong> • {timestamp}</span>
                    <button class="copy-btn" onclick="navigator.clipboard.writeText('{bot_reply.replace("'", "\\'")}')">📋 Copy</button>
                </div>
                <div>{bot_reply}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Rerun untuk update tampilan
    st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #6b7280; font-size: 12px;'>"
    f"Powered by {MODEL} via OpenRouter • "
    f"Total Chats: {len(st.session_state.chats)} • "
    f"Messages in current chat: {len(current_chat['messages'])}"
    "</div>",
    unsafe_allow_html=True
)
