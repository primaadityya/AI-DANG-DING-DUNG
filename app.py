# ===========================================
# IMPORT LIBRARY YANG DIPERLUKAN
# ===========================================
import streamlit as st
import requests
import uuid
from datetime import datetime
import hashlib
import time

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
# FUNGSI UNTUK GENERATE USER SESSION ID UNIK
# ===========================================
def get_user_session_id():
    """Generate unique session ID per user/browser"""
    if "user_session_id" not in st.session_state:
        # Buat ID unik berdasarkan timestamp dan random UUID
        timestamp = str(time.time())
        random_id = str(uuid.uuid4())
        session_string = f"{timestamp}_{random_id}"
        st.session_state.user_session_id = hashlib.md5(session_string.encode()).hexdigest()[:16]
    return st.session_state.user_session_id

# ===========================================
# FUNGSI UNTUK MANAGE DATA PER USER
# ===========================================
def get_user_key(key_name):
    """Get user-specific key for session state"""
    session_id = get_user_session_id()
    return f"{session_id}_{key_name}"

def get_user_data(key_name, default_value=None):
    """Get user-specific data from session state"""
    user_key = get_user_key(key_name)
    return st.session_state.get(user_key, default_value)

def set_user_data(key_name, value):
    """Set user-specific data to session state"""
    user_key = get_user_key(key_name)
    st.session_state[user_key] = value

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
        align-items: center;
        margin-bottom: 8px;
        font-size: 13px;
        color: var(--secondary-text-color);
    }
    
    /* Avatar untuk pengguna dan AI */
    .message-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        margin-right: 10px;
        object-fit: cover;
    }
    
    /* Avatar khusus untuk user */
    .user-avatar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 14px;
        font-weight: bold;
    }
    
    /* Avatar khusus untuk AI */
    .ai-avatar {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 14px;
        font-weight: bold;
    }
    
    /* Nama dan waktu di samping avatar */
    .message-info {
        display: flex;
        flex-direction: column;
    }
    
    .message-name {
        font-weight: bold;
        color: var(--text-color);
        font-size: 14px;
    }
    
    .message-time {
        font-size: 11px;
        color: var(--secondary-text-color);
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

    /* Styling untuk welcome section */
    .welcome-container {
        max-width: 600px;
        margin: 0 auto;
        padding: 20px;
    }

    /* Styling untuk loading message */
    .loading-message {
        background-color: var(--background-color);
        color: var(--secondary-text-color);
        padding: 15px 20px;
        border-radius: 18px;
        margin: 10px 0;
        margin-right: 20%;
        position: relative;
        border: 1px solid var(--border-color);
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        font-style: italic;
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
# FUNGSI UTILITAS UNTUK TIMESTAMP
# ===========================================
def get_current_time():
    """Mendapatkan waktu sekarang dalam format datetime"""
    return datetime.now()

def format_time(dt):
    """Format waktu menjadi HH:MM"""
    if isinstance(dt, str):
        # Jika string, parse dulu
        try:
            dt = datetime.fromisoformat(dt)
        except:
            return datetime.now().strftime("%H:%M")
    return dt.strftime("%H:%M")

# ===========================================
# INISIALISASI DATA USER DENGAN SESSION ID
# ===========================================
# Generate unique session ID untuk user ini
session_id = get_user_session_id()

# Inisialisasi nama user (per session ID)
if get_user_data("user_name") is None:
    set_user_data("user_name", "")

# Inisialisasi dictionary untuk menyimpan semua chat (per session ID)
if get_user_data("chats") is None:
    set_user_data("chats", {})
    
# Inisialisasi chat ID yang sedang aktif (per session ID)
user_chats = get_user_data("chats", {})
current_chat_id = get_user_data("current_chat_id")

if current_chat_id is None or current_chat_id not in user_chats:
    chat_id = str(uuid.uuid4())
    set_user_data("current_chat_id", chat_id)
    user_chats[chat_id] = {
        "title": "Chat Baru",
        "messages": [],
        "created_at": get_current_time()
    }
    set_user_data("chats", user_chats)

# Inisialisasi model yang dipilih (per session ID)
if get_user_data("selected_model") is None:
    set_user_data("selected_model", "Deepseek v3")

# Flag untuk regenerate response terakhir (per session ID)
if get_user_data("regenerate_last") is None:
    set_user_data("regenerate_last", False)

# Flag untuk menampilkan loading (per session ID)
if get_user_data("is_loading") is None:
    set_user_data("is_loading", False)

# ===========================================
# MODAL INPUT NAMA USER
# ===========================================
user_name = get_user_data("user_name", "")
if not user_name:
    # Container untuk input nama tanpa modal overlay
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Header dengan styling yang menarik
    st.markdown("""
    <div style='text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 15px; margin-bottom: 30px; color: white; box-shadow: 0 10px 25px rgba(0,0,0,0.1);'>
        <h1>🤖 Selamat datang di PouringGPT!</h1>
        <p style='font-size: 18px; margin: 0;'>AI Assistant yang siap membantu Kamu</p>
        <p style='font-size: 14px; margin: 0;'>Created by : dangdingdung</p>        
    </div>
    """, unsafe_allow_html=True)
    
    # Container untuk input nama
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style='background-color: var(--background-color-secondary); padding: 25px; border-radius: 10px; 
                    border: 1px solid var(--border-color); text-align: center; margin-bottom: 20px;'>
            <h3 style='margin-top: 0; color: var(--text-color);'>👋 Perkenalkan diri Kamu</h3>
            <p style='color: var(--secondary-text-color); margin-bottom: 20px;'>
                Masukkan nama Kamu untuk pengalaman chat yang lebih personal
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        user_name_input = st.text_input(
            "Nama Anda:",
            placeholder="Ketik nama Nama disini...",
            key=f"name_input_{session_id}",
            help="Nama ini akan digunakan untuk mempersonalisasi percakapan dengan Pouring"
        )
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🚀 Mulai Chat", key=f"start_chat_{session_id}", use_container_width=True, type="primary"):
                if user_name_input.strip():
                    set_user_data("user_name", user_name_input.strip())
                    st.rerun()
                else:
                    st.error("Silakan masukkan nama Anda terlebih dahulu!")
        
        with col_btn2:
            if st.button("⏭️ Lewati", key=f"skip_name_{session_id}", use_container_width=True, help="Chat tanpa nama personal"):
                set_user_data("user_name", "Pengguna")
                st.rerun()
        
        st.markdown("""
        <div style='text-align: center; margin-top: 20px; color: var(--secondary-text-color); font-size: 14px;'>
            <p>💡 Tips: Dengan memasukkan nama, Pouring akan dapat menyapa Anda secara personal!</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.stop()

# ===========================================
# SIDEBAR - RIWAYAT CHAT & PENGATURAN
# ===========================================
with st.sidebar:
    st.title("🤖 PouringGPT")
    selected_model = get_user_data("selected_model", "Deepseek v3")
    st.markdown(f"<small>**Model:** {selected_model}</small>", unsafe_allow_html=True)
    st.markdown(f"<small>**Provider:** OpenRouter</small>", unsafe_allow_html=True)
    
    # Tombol untuk mengubah nama
    if st.button("✏️ Ubah Nama", key=f"change_name_{session_id}", help="Ubah nama pengguna", use_container_width=True):
        set_user_data("user_name", "")
        st.rerun()

    st.markdown("---")
    
    # Tombol untuk membuat chat baru
    if st.button("➕ Chat Baru", key=f"new_chat_{session_id}", help="Mulai percakapan baru", use_container_width=True):
        chat_id = str(uuid.uuid4())
        set_user_data("current_chat_id", chat_id)
        user_chats = get_user_data("chats", {})
        user_chats[chat_id] = {
            "title": "Chat Baru",
            "messages": [],
            "created_at": get_current_time()
        }
        set_user_data("chats", user_chats)
        st.rerun()
    
    # Tampilkan daftar semua chat yang ada
    user_chats = get_user_data("chats", {})
    current_chat_id = get_user_data("current_chat_id")
    
    for chat_id, chat_data in sorted(user_chats.items(), 
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
            
            is_active = chat_id == current_chat_id
            
            # Tombol untuk memilih chat
            if st.button(
                title,
                key=f"chat_{chat_id}_{session_id}",
                help=f"Buka chat - {chat_data['created_at'].strftime('%d/%m/%Y %H:%M')}",
                type="primary" if is_active else "secondary",
                use_container_width=True
            ):
                set_user_data("current_chat_id", chat_id)
                st.rerun()
        
        with col2:
            # Tombol untuk menghapus chat
            if st.button("🗑️", key=f"delete_{chat_id}_{session_id}", help="Hapus chat"):
                user_chats = get_user_data("chats", {})
                del user_chats[chat_id]
                set_user_data("chats", user_chats)
                
                if chat_id == current_chat_id:
                    # Jika ada chat lain, pilih yang pertama. Jika tidak, buat chat baru
                    if user_chats:
                        set_user_data("current_chat_id", list(user_chats.keys())[0])
                    else:
                        # Buat chat baru jika semua chat telah dihapus
                        new_chat_id = str(uuid.uuid4())
                        set_user_data("current_chat_id", new_chat_id)
                        user_chats[new_chat_id] = {
                            "title": "Chat Baru",
                            "messages": [],
                            "created_at": get_current_time()
                        }
                        set_user_data("chats", user_chats)
                st.rerun()

    st.markdown("---")
    
    # Pemilihan model AI
    st.subheader("🌟 Pilih Model")
    selected_model_new = st.selectbox(
        "Model AI:",
        options=list(AVAILABLE_MODELS.keys()),
        index=list(AVAILABLE_MODELS.keys()).index(selected_model),
        key=f"model_selector_{session_id}"
    )
    
    # Update model jika ada perubahan
    if selected_model_new != selected_model:
        set_user_data("selected_model", selected_model_new)
        st.rerun()

# ===========================================
# KONTEN UTAMA - AREA CHAT
# ===========================================
# Ambil data chat yang sedang aktif
user_chats = get_user_data("chats", {})
current_chat_id = get_user_data("current_chat_id")
current_chat = user_chats[current_chat_id]
selected_model = get_user_data("selected_model", "Deepseek v3")
current_model = AVAILABLE_MODELS[selected_model]
user_name = get_user_data("user_name", "Pengguna")

# Container untuk menampilkan percakapan
chat_container = st.container()

with chat_container:
    # Jika belum ada pesan, tampilkan pesan selamat datang yang dipersonalisasi
    if not current_chat["messages"]:
        st.markdown(f"""
        <div style='text-align: center; margin: 50px 0; color: var(--secondary-text-color);'>
            <h3>Hai {user_name}, Apa yang bisa Pouring bantu?</h3>
        </div>
        """, unsafe_allow_html=True)
    
    # Tampilkan semua pesan dalam chat yang aktif
    for i, message in enumerate(current_chat["messages"]):
        timestamp = format_time(message.get("timestamp", get_current_time()))
        
        # Tampilkan pesan dari user dengan nama yang dipersonalisasi
        if message["role"] == "user":
            st.markdown(f"""
            <div class="user-message">
                <div class="message-header">
                    <div class="user-avatar message-avatar">👤</div>
                    <div class="message-info">
                        <div class="message-name">{user_name}</div>
                        <div class="message-time">{timestamp}</div>
                    </div>
                </div>
                <div>{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        # Tampilkan pesan dari AI
        else:
            st.markdown(f"""
            <div class="assistant-message">
                <div class="message-header">
                    <div class="ai-avatar message-avatar">🤖</div>
                    <div class="message-info">
                        <div class="message-name">Pouring</div>
                        <div class="message-time">{timestamp}</div>
                    </div>
                </div>
                <div>{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Tampilkan loading message jika sedang memproses
    is_loading = get_user_data("is_loading", False)
    if is_loading:
        current_time = format_time(get_current_time())
        st.markdown(f"""
        <div class="loading-message">
            <div class="message-header">
                <div class="ai-avatar message-avatar">🤖</div>
                <div class="message-info">
                    <div class="message-name">Pouring</div>
                    <div class="message-time">{current_time}</div>
                </div>
            </div>
            <div>Pouring sedang mengetik...</div>
        </div>
        """, unsafe_allow_html=True)

# ===========================================
# TOMBOL REGENERATE RESPONSE
# ===========================================
# Tampilkan tombol regenerate jika pesan terakhir dari AI
if (current_chat["messages"] and 
    current_chat["messages"][-1]["role"] == "assistant" and
    not is_loading):
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Regenerate Response", key=f"regenerate_btn_{session_id}", 
                   help="Generate ulang respons terakhir", use_container_width=True):
            set_user_data("regenerate_last", True)
            st.rerun()

# ===========================================
# INPUT CHAT DARI USER
# ===========================================
user_input = st.chat_input(f"Ketik pesan {user_name} disini...")

# ===========================================
# PROSES REGENERATE RESPONSE
# ===========================================
regenerate_last = get_user_data("regenerate_last", False)
if regenerate_last:
    set_user_data("regenerate_last", False)
    
    # Hapus pesan AI terakhir
    if current_chat["messages"] and current_chat["messages"][-1]["role"] == "assistant":
        current_chat["messages"].pop()
        
        # Update data chat
        user_chats[current_chat_id] = current_chat
        set_user_data("chats", user_chats)
        
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
    if not regenerate_last:
        user_message = {
            "role": "user", 
            "content": user_input,
            "timestamp": get_current_time()
        }
        current_chat["messages"].append(user_message)
        
        # Update title chat jika ini pesan pertama
        if len([msg for msg in current_chat["messages"] if msg["role"] == "user"]) == 1:
            if len(user_input) > 30:
                current_chat["title"] = user_input[:30] + "..."
            else:
                current_chat["title"] = user_input
        
        # Update data chat
        user_chats[current_chat_id] = current_chat
        set_user_data("chats", user_chats)
    
    # Set loading state
    set_user_data("is_loading", True)
    st.rerun()

# ===========================================
# PROSES API CALL (ASYNC HANDLING)
# ===========================================
if is_loading:
    try:
        # Siapkan format pesan untuk API OpenRouter dengan personalisasi
        messages_for_api = [{"role": "system", "content": f"You are Pouring, a helpful AI assistant. The user's name is {user_name}. Please address them by their name when appropriate and be friendly and helpful."}]
        for msg in current_chat["messages"]:
            if msg["role"] != "loading":  # Skip loading messages
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
        "timestamp": get_current_time()
    }
    current_chat["messages"].append(ai_message)
    
    # Update data chat
    user_chats[current_chat_id] = current_chat
    set_user_data("chats", user_chats)
    
    # Reset loading state
    set_user_data("is_loading", False)
    
    # Refresh halaman untuk menampilkan pesan baru
    st.rerun()
