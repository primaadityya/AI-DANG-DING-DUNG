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

# Custom CSS untuk styling yang responsive terhadap dark/light theme
st.markdown("""
<style>
    .main-content {
        max-width: 800px;
        margin: 0 auto;
        padding: 0 20px;
    }
    
    .user-message {
        background-color: var(--background-color-secondary);
        color: var(--text-color);
        padding: 15px 20px;
        border-radius: 18px;
        margin: 10px 0;
        margin-left: 20%;
        position: relative;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid var(--border-color);
    }
    
    .assistant-message {
        background-color: var(--background-color);
        color: var(--text-color);
        padding: 15px 20px;
        border-radius: 18px;
        margin: 10px 0;
        margin-right: 20%;
        position: relative;
        border: 1px solid var(--border-color);
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    /* Light theme variables */
    :root {
        --background-color: #ffffff;
        --background-color-secondary: #f0f2f6;
        --text-color: #262730;
        --border-color: #e1e5e9;
        --secondary-text-color: #6b7280;
        --hover-color: #f3f4f6;
    }

    /* Dark theme variables */
    @media (prefers-color-scheme: dark) {
        :root {
            --background-color: #1e1e1e;
            --background-color-secondary: #2d2d2d;
            --text-color: #fafafa;
            --border-color: #404040;
            --secondary-text-color: #a1a1a1;
            --hover-color: #404040;
        }
    }

    /* Streamlit dark theme detection */
    .stApp[data-theme="dark"] {
        --background-color: #0e1117;
        --background-color-secondary: #262730;
        --text-color: #fafafa;
        --border-color: #30363d;
        --secondary-text-color: #8b949e;
        --hover-color: #21262d;
    }
    
    .message-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        font-size: 12px;
        color: var(--secondary-text-color);
    }
    
    .message-actions {
        display: flex;
        gap: 8px;
        align-items: center;
    }
    
    .action-btn {
        background: none;
        border: none;
        cursor: pointer;
        padding: 4px 8px;
        border-radius: 4px;
        color: var(--secondary-text-color);
        font-size: 12px;
        transition: background-color 0.2s;
    }
    
    .action-btn:hover {
        background-color: var(--hover-color);
    }
    
    .message-avatar {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
        vertical-align: middle;
    }
    
    .user-avatar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 12px;
        font-weight: bold;
    }
    
    .ai-avatar {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 12px;
        font-weight: bold;
    }
    
    .typing-animation {
        display: inline-block;
    }
    
    .typing-dot {
        display: inline-block;
        width: 4px;
        height: 4px;
        border-radius: 50%;
        background-color: var(--secondary-text-color);
        margin: 0 1px;
        animation: typing 1.4s infinite ease-in-out;
    }
    
    .typing-dot:nth-child(1) { animation-delay: -0.32s; }
    .typing-dot:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes typing {
        0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
        40% { transform: scale(1.2); opacity: 1; }
    }
    
    .model-selector {
        margin: 15px 0;
        padding: 10px;
        border-radius: 8px;
        background-color: var(--background-color-secondary);
        border: 1px solid var(--border-color);
    }
    
    .chat-item {
        padding: 12px;
        border-radius: 6px;
        cursor: pointer;
        margin-bottom: 4px;
        border: 1px solid transparent;
        background-color: var(--background-color);
        color: var(--text-color);
    }
    
    .chat-item:hover {
        background-color: var(--hover-color);
    }
    
    .chat-item.active {
        background-color: var(--background-color-secondary);
        border-color: #3b82f6;
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

# Fungsi untuk streaming response
def stream_response(text, placeholder):
    """Simulasi streaming text seperti Claude"""
    words = text.split()
    displayed_text = ""
    
    for i, word in enumerate(words):
        displayed_text += word + " "
        
        # Update placeholder dengan animasi typing
        if i < len(words) - 1:
            typing_animation = '<span class="typing-animation"><span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span></span>'
            placeholder.markdown(f"""
            <div class="assistant-message">
                <div class="message-header">
                    <span><div class="ai-avatar message-avatar">AI</div><strong>AI Assistant</strong> • {datetime.now().strftime('%H:%M')}</span>
                </div>
                <div>{displayed_text}{typing_animation}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Final message tanpa typing animation
            placeholder.markdown(f"""
            <div class="assistant-message">
                <div class="message-header">
                    <span><div class="ai-avatar message-avatar">AI</div><strong>AI Assistant</strong> • {datetime.now().strftime('%H:%M')}</span>
                    <div class="message-actions">
                        <button class="action-btn" onclick="navigator.clipboard.writeText('{text.replace("'", "\\'")}')">📋 Copy</button>
                        <button class="action-btn" onclick="location.reload()">🔄 Regenerate</button>
                    </div>
                </div>
                <div>{displayed_text.strip()}</div>
            </div>
            """, unsafe_allow_html=True)
        
        time.sleep(0.05)  # Delay untuk efek mengetik

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

# Add JavaScript for regenerate functionality
st.markdown("""
<script>
function regenerateResponse(messageIndex) {
    // This will be handled by Streamlit's rerun mechanism
    window.location.reload();
}
</script>
""", unsafe_allow_html=True)

with chat_container:
    # Tampilkan riwayat chat
    for i, message in enumerate(current_chat["messages"]):
        timestamp = message.get("timestamp", datetime.now()).strftime("%H:%M")
        
        if message["role"] == "user":
            st.markdown(f"""
            <div class="user-message">
                <div class="message-header">
                    <span><div class="user-avatar message-avatar">You</div><strong>Anda</strong> • {timestamp}</span>
                    <div class="message-actions">
                        <button class="action-btn" onclick="navigator.clipboard.writeText('{message['content'].replace("'", "\\'")}')">📋 Copy</button>
                    </div>
                </div>
                <div>{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Tambahkan tombol regenerate hanya untuk pesan AI terakhir
            is_last_ai_message = (i == len(current_chat["messages"]) - 1 and 
                                message["role"] == "assistant")
            
            regenerate_btn = ""
            if is_last_ai_message:
                regenerate_btn = f'<button class="action-btn" onclick="document.getElementById(\'regenerate_{i}\').click()">🔄 Regenerate</button>'
            
            st.markdown(f"""
            <div class="assistant-message">
                <div class="message-header">
                    <span><div class="ai-avatar message-avatar">AI</div><strong>AI Assistant</strong> • {timestamp}</span>
                    <div class="message-actions">
                        <button class="action-btn" onclick="navigator.clipboard.writeText('{message['content'].replace("'", "\\'")}')">📋 Copy</button>
                        {regenerate_btn}
                    </div>
                </div>
                <div>{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Hidden button untuk regenerate
            if is_last_ai_message:
                if st.button("Regenerate", key=f"regenerate_{i}", type="primary", 
                           help="Generate ulang respons terakhir"):
                    # Hapus pesan AI terakhir dan regenerate
                    if current_chat["messages"] and current_chat["messages"][-1]["role"] == "assistant":
                        current_chat["messages"].pop()
                        
                        # Ambil pesan user terakhir
                        last_user_message = None
                        for msg in reversed(current_chat["messages"]):
                            if msg["role"] == "user":
                                last_user_message = msg["content"]
                                break
                        
                        if last_user_message:
                            # Regenerate response
                            with st.spinner("Regenerating response..."):
                                try:
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
                                
                                # Tambahkan respons baru
                                ai_message = {
                                    "role": "assistant",
                                    "content": bot_reply,
                                    "timestamp": datetime.now()
                                }
                                current_chat["messages"].append(ai_message)
                                st.rerun()

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
                <span><div class="user-avatar message-avatar">You</div><strong>Anda</strong> • {timestamp}</span>
                <div class="message-actions">
                    <button class="action-btn" onclick="navigator.clipboard.writeText('{user_input.replace("'", "\\'")}')">📋 Copy</button>
                </div>
            </div>
            <div>{user_input}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Dapatkan respons dari AI dengan streaming
    response_placeholder = st.empty()
    
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
    
    # Stream response
    stream_response(bot_reply, response_placeholder)
    
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
