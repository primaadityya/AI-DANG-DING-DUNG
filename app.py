# ===========================================
# IMPORT LIBRARY YANG DIPERLUKAN
# ===========================================
import streamlit as st
import requests
import uuid
from datetime import datetime
import json

# ===========================================
# KONFIGURASI HALAMAN STREAMLIT
# ===========================================
st.set_page_config(
    page_title="PouringGPT",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===========================================
# CUSTOM CSS UNTUK STYLING TAMPILAN
# ===========================================
st.markdown("""
<style>
    /* Container utama untuk membatasi lebar konten */
    .main-content {
        max-width: 800px;
        margin: 0 auto;
        padding: 0 20px;
    }
    
    /* Styling untuk pesan dari user */
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
    
    /* Styling untuk pesan dari AI assistant */
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

    /* Variabel CSS untuk tema terang */
    :root {
        --background-color: #ffffff;
        --background-color-secondary: #f0f2f6;
        --text-color: #262730;
        --border-color: #e1e5e9;
        --secondary-text-color: #6b7280;
        --hover-color: #f3f4f6;
    }

    /* Variabel CSS untuk tema gelap (deteksi otomatis) */
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

    /* Override untuk tema gelap Streamlit */
    .stApp[data-theme="dark"] {
        --background-color: #0e1117;
        --background-color-secondary: #262730;
        --text-color: #fafafa;
        --border-color: #30363d;
        --secondary-text-color: #8b949e;
        --hover-color: #21262d;
    }

    /* Force override untuk tema gelap */
    [data-testid="stApp"] {
        --background-color: #0e1117;
        --background-color-secondary: #262730;
        --text-color: #fafafa;
        --border-color: #30363d;
        --secondary-text-color: #8b949e;
        --hover-color: #21262d;
    }

    /* Override untuk tema terang */
    [data-testid="stApp"][data-theme="light"] {
        --background-color: #ffffff;
        --background-color-secondary: #f0f2f6;
        --text-color: #262730;
        --border-color: #e1e5e9;
        --secondary-text-color: #6b7280;
        --hover-color: #f3f4f6;
    }
    
    /* Header untuk setiap pesan (waktu, nama) */
    .message-header {
        display: flex;
        justify-content: flex-start;
        align-items: center;
        margin-bottom: 8px;
        font-size: 12px;
        color: var(--secondary-text-color);
    }
    
    /* Container untuk tombol aksi (dihapus karena tidak ada fitur copy) */
    
    /* Avatar lingkaran untuk pengguna dan AI */
    .message-avatar {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
        vertical-align: middle;
    }
    
    /* Avatar khusus untuk user */
    .user-avatar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 10px;
        font-weight: bold;
    }
    
    /* Avatar khusus untuk AI */
    .ai-avatar {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 10px;
        font-weight: bold;
    }
    
    /* Container untuk pemilihan model */
    .model-selector {
        margin: 15px 0;
        padding: 10px;
        border-radius: 8px;
        background-color: var(--background-color-secondary);
        border: 1px solid var(--border-color);
    }
    
    /* Item chat di sidebar */
    .chat-item {
        padding: 12px;
        border-radius: 6px;
        cursor: pointer;
        margin-bottom: 4px;
        border: 1px solid transparent;
        background-color: var(--background-color);
        color: var(--text-color);
    }
    
    /* Efek hover untuk item chat */
    .chat-item:hover {
        background-color: var(--hover-color);
    }
    
    /* Chat yang sedang aktif */
    .chat-item.active {
        background-color: var(--background-color-secondary);
        border-color: #3b82f6;
    }
</style>
""", unsafe_allow_html=True)

# ===========================================
# DEFINISI MODEL AI YANG TERSEDIA
# ===========================================
AVAILABLE_MODELS = {
    "Deepseek v3": "deepseek/deepseek-chat-v3-0324",
    "Llama 4": "meta-llama/llama-4-maverick:free", 
    "Gemini 2.0": "google/gemini-2.0-flash-exp:free",
    "Mistral Nemo": "mistralai/mistral-nemo:free"
}

# ===========================================
# KONFIGURASI API OPENROUTER
# ===========================================
# Ambil API key dari Streamlit secrets
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
# Header untuk autentikasi API
HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "https://ai-dang-ding-dung.streamlit.app/",
    "X-Title": "AI Chatbot Streamlit"
}
# URL endpoint API OpenRouter
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# ===========================================
# INISIALISASI SESSION STATE
# ===========================================
# Inisialisasi dictionary untuk menyimpan semua chat
if "chats" not in st.session_state:
    st.session_state.chats = {}
    
# Inisialisasi chat ID yang sedang aktif
if "current_chat_id" not in st.session_state:
    chat_id = str(uuid.uuid4())
    st.session_state.current_chat_id = chat_id
    st.session_state.chats[chat_id] = {
        "title": "Chat Baru",
        "messages": [],
        "created_at": datetime.now()
    }

# Inisialisasi model yang dipilih
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "Deepseek v3"

# Flag untuk regenerate response terakhir
if "regenerate_last" not in st.session_state:
    st.session_state.regenerate_last = False

# ===========================================
# SIDEBAR - RIWAYAT CHAT & PENGATURAN
# ===========================================
with st.sidebar:
    st.title("🤖 PouringGPT")
    st.title("💬 Chat History")
    
    # Tombol untuk membuat chat baru
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
    
    # Tampilkan daftar semua chat yang ada
    for chat_id, chat_data in sorted(st.session_state.chats.items(), 
                                   key=lambda x: x[1]["created_at"], reverse=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            # Buat preview dari pesan pertama user sebagai judul
            title = chat_data["title"]
            if chat_data["messages"] and len(chat_data["messages"]) > 0:
                first_user_msg = next((msg["content"] for msg in chat_data["messages"] 
                                     if msg["role"] == "user"), "Chat Baru")
                if len(first_user_msg) > 30:
                    title = first_user_msg[:30] + "..."
                else:
                    title = first_user_msg
            
            is_active = chat_id == st.session_state.current_chat_id
            
            # Tombol untuk memilih chat
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
            # Tombol untuk menghapus chat
            if st.button("🗑️", key=f"delete_{chat_id}", help="Hapus chat"):
                del st.session_state.chats[chat_id]
                if chat_id == st.session_state.current_chat_id:
                    # Jika ada chat lain, pilih yang pertama. Jika tidak, buat chat baru
                    if st.session_state.chats:
                        st.session_state.current_chat_id = list(st.session_state.chats.keys())[0]
                    else:
                        # Buat chat baru jika semua chat telah dihapus
                        new_chat_id = str(uuid.uuid4())
                        st.session_state.current_chat_id = new_chat_id
                        st.session_state.chats[new_chat_id] = {
                            "title": "Chat Baru",
                            "messages": [],
                            "created_at": datetime.now()
                        }
                st.rerun()

    st.markdown("---")
    
    # Pemilihan model AI
    st.subheader("🤖 Pilih Model")
    selected_model = st.selectbox(
        "Model AI:",
        options=list(AVAILABLE_MODELS.keys()),
        index=list(AVAILABLE_MODELS.keys()).index(st.session_state.selected_model),
        key="model_selector"
    )
    
    # Update model jika ada perubahan
    if selected_model != st.session_state.selected_model:
        st.session_state.selected_model = selected_model
        st.rerun()

# ===========================================
# KONTEN UTAMA - AREA CHAT
# ===========================================
# Ambil data chat yang sedang aktif
current_chat = st.session_state.chats[st.session_state.current_chat_id]
current_model = AVAILABLE_MODELS[st.session_state.selected_model]

# Header halaman utama
st.markdown(f"<small>**Model:** {st.session_state.selected_model} | **Provider:** OpenRouter</small>", unsafe_allow_html=True)

# Container untuk menampilkan percakapan
chat_container = st.container()

with chat_container:
    # Jika belum ada pesan, tampilkan pesan selamat datang
    if not current_chat["messages"]:
        st.markdown("""
        <div style='text-align: center; margin: 50px 0; color: var(--secondary-text-color);'>
            <h3>Ada yang bisa Pouring bantu?</h3>
        </div>
        """, unsafe_allow_html=True)
    
    # Tampilkan semua pesan dalam chat yang aktif
    for i, message in enumerate(current_chat["messages"]):
        timestamp = message.get("timestamp", datetime.now()).strftime("%H:%M")
        
        # Tampilkan pesan dari user
        if message["role"] == "user":
            st.markdown(f"""
            <div class="user-message">
                <div class="message-header">
                    <span><div class="user-avatar message-avatar">YOU</div><strong>Anda</strong> • {timestamp}</span>
                </div>
                <div>{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        # Tampilkan pesan dari AI
        else:
            st.markdown(f"""
            <div class="assistant-message">
                <div class="message-header">
                    <span><div class="ai-avatar message-avatar">AI</div><strong>AI Assistant</strong> • {timestamp}</span>
                </div>
                <div>{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)

# ===========================================
# TOMBOL REGENERATE RESPONSE
# ===========================================
# Tampilkan tombol regenerate jika pesan terakhir dari AI
if (current_chat["messages"] and 
    current_chat["messages"][-1]["role"] == "assistant"):
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Regenerate Response", key="regenerate_btn", 
                   help="Generate ulang respons terakhir", use_container_width=True):
            st.session_state.regenerate_last = True
            st.rerun()

# ===========================================
# INPUT CHAT DARI USER
# ===========================================
user_input = st.chat_input("Ketik pesan Anda di sini...")

# ===========================================
# PROSES REGENERATE RESPONSE
# ===========================================
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

# ===========================================
# PROSES INPUT USER & PANGGIL API
# ===========================================
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
    
    # Tampilkan loading spinner saat menunggu response
    with st.spinner("AI sedang memikirkan jawaban..."):
        try:
            # Siapkan format pesan untuk API OpenRouter
            messages_for_api = [{"role": "system", "content": "You are a helpful assistant."}]
            for msg in current_chat["messages"]:
                messages_for_api.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Payload untuk API request
            payload = {
                "model": current_model,
                "messages": messages_for_api
            }
            
            # Kirim request ke OpenRouter API
            response = requests.post(API_URL, headers=HEADERS, json=payload)
            
            # Proses response dari API
            if response.status_code == 200:
                bot_reply = response.json()['choices'][0]['message']['content']
            else:
                bot_reply = f"⚠️ Error {response.status_code}: {response.text}"
                
        except Exception as e:
            bot_reply = f"⚠️ Terjadi kesalahan: {str(e)}"
    
    # Tambahkan respons AI ke riwayat chat
    ai_message = {
        "role": "assistant",
        "content": bot_reply,
        "timestamp": datetime.now()
    }
    current_chat["messages"].append(ai_message)
    
    # Refresh halaman untuk menampilkan pesan baru
    st.rerun()

# ===========================================
# FOOTER - INFORMASI STATUS
# ===========================================
st.markdown(
    "<div style='text-align: center; color: var(--secondary-text-color); font-size: 12px; margin-top: 20px;'>"
    f"Powered by {st.session_state.selected_model} via OpenRouter • "
    f"Total Chats: {len(st.session_state.chats)} • "
    f"Messages in current chat: {len(current_chat['messages'])}"
    "</div>",
    unsafe_allow_html=True
)
