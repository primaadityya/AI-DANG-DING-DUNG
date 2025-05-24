# ===========================================
# IMPORT LIBRARY YANG DIPERLUKAN
# ===========================================
import streamlit as st
import requests
import uuid

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
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 15px 20px;
        border-radius: 18px;
        margin: 10px 0;
        margin-left: 20%;
        position: relative;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #bbdefb;
    }
    
    /* Styling untuk pesan dari AI assistant */
    .assistant-message {
        background-color: #f5f5f5;
        color: #424242;
        padding: 15px 20px;
        border-radius: 18px;
        margin: 10px 0;
        margin-right: 20%;
        position: relative;
        border: 1px solid #e0e0e0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    /* Tema gelap - override untuk pesan user */
    [data-testid="stApp"] .user-message {
        background-color: #1e3a8a;
        color: #dbeafe;
        border-color: #3b82f6;
    }
    
    /* Tema gelap - override untuk pesan AI */
    [data-testid="stApp"] .assistant-message {
        background-color: #374151;
        color: #f9fafb;
        border-color: #4b5563;
    }

    /* Deteksi tema gelap sistem */
    @media (prefers-color-scheme: dark) {
        .user-message {
            background-color: #1e3a8a !important;
            color: #dbeafe !important;
            border-color: #3b82f6 !important;
        }
        
        .assistant-message {
            background-color: #374151 !important;
            color: #f9fafb !important;
            border-color: #4b5563 !important;
        }
    }

    /* Variabel CSS untuk tema */
    :root {
        --text-color: #262730;
        --secondary-text-color: #6b7280;
        --background-color-secondary: #f0f2f6;
        --border-color: #e1e5e9;
        --hover-color: #f3f4f6;
    }

    /* Tema gelap */
    [data-testid="stApp"] {
        --text-color: #fafafa;
        --secondary-text-color: #8b949e;
        --background-color-secondary: #262730;
        --border-color: #30363d;
        --hover-color: #21262d;
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --text-color: #fafafa;
            --secondary-text-color: #8b949e;
            --background-color-secondary: #262730;
            --border-color: #30363d;
            --hover-color: #21262d;
        }
    }
    
    /* Header untuk setiap pesan (nama) */
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
    
    /* Nama di samping avatar */
    .message-name {
        font-weight: bold;
        color: var(--text-color);
        font-size: 14px;
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
        background-color: #fff3cd;
        color: #856404;
        padding: 15px 20px;
        border-radius: 18px;
        margin: 10px 0;
        margin-right: 20%;
        position: relative;
        border: 1px solid #ffeaa7;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        font-style: italic;
    }

    /* Tema gelap untuk loading message */
    [data-testid="stApp"] .loading-message {
        background-color: #92400e;
        color: #fef3c7;
        border-color: #d97706;
    }

    @media (prefers-color-scheme: dark) {
        .loading-message {
            background-color: #92400e !important;
            color: #fef3c7 !important;
            border-color: #d97706 !important;
        }
    }
</style>""", unsafe_allow_html=True)

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
# INISIALISASI DATA SESSION STATE
# ===========================================
# Inisialisasi nama user
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

# Inisialisasi dictionary untuk menyimpan semua chat
if "chats" not in st.session_state:
    st.session_state.chats = {}
    
# Inisialisasi chat ID yang sedang aktif
if "current_chat_id" not in st.session_state or st.session_state.current_chat_id not in st.session_state.chats:
    chat_id = str(uuid.uuid4())
    st.session_state.current_chat_id = chat_id
    st.session_state.chats[chat_id] = {
        "title": "Chat Baru",
        "messages": []
    }

# Inisialisasi model yang dipilih
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "Deepseek v3"

# Flag untuk regenerate response terakhir
if "regenerate_last" not in st.session_state:
    st.session_state.regenerate_last = False

# Flag untuk menampilkan loading
if "is_loading" not in st.session_state:
    st.session_state.is_loading = False

# ===========================================
# MODAL INPUT NAMA USER
# ===========================================
if not st.session_state.user_name:
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
            key="name_input",
            help="Nama ini akan digunakan untuk mempersonalisasi percakapan dengan Pouring"
        )
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🚀 Mulai Chat", key="start_chat", use_container_width=True, type="primary"):
                if user_name_input.strip():
                    st.session_state.user_name = user_name_input.strip()
                    st.rerun()
                else:
                    st.error("Silakan masukkan nama Anda terlebih dahulu!")
        
        with col_btn2:
            if st.button("⏭️ Lewati", key="skip_name", use_container_width=True, help="Chat tanpa nama personal"):
                st.session_state.user_name = "Pengguna"
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
    st.markdown(f"<small>**Model:** {st.session_state.selected_model}</small>", unsafe_allow_html=True)
    st.markdown(f"<small>**Provider:** OpenRouter</small>", unsafe_allow_html=True)
    
    # Tombol untuk mengubah nama
    if st.button("✏️ Ubah Nama", key="change_name", help="Ubah nama pengguna", use_container_width=True):
        st.session_state.user_name = ""
        st.rerun()

    st.markdown("---")
    
    # Tombol untuk membuat chat baru
    if st.button("➕ Chat Baru", key="new_chat", help="Mulai percakapan baru", use_container_width=True):
        chat_id = str(uuid.uuid4())
        st.session_state.current_chat_id = chat_id
        st.session_state.chats[chat_id] = {
            "title": "Chat Baru",
            "messages": []
        }
        st.rerun()
    
    # Tampilkan daftar semua chat yang ada
    for chat_id, chat_data in st.session_state.chats.items():
        
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
                help="Buka chat",
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
                            "messages": []
                        }
                st.rerun()

    st.markdown("---")
    
    # Pemilihan model AI
    st.subheader("🌟 Pilih Model")
    selected_model_new = st.selectbox(
        "Model AI:",
        options=list(AVAILABLE_MODELS.keys()),
        index=list(AVAILABLE_MODELS.keys()).index(st.session_state.selected_model),
        key="model_selector"
    )
    
    # Update model jika ada perubahan
    if selected_model_new != st.session_state.selected_model:
        st.session_state.selected_model = selected_model_new
        st.rerun()

# ===========================================
# KONTEN UTAMA - AREA CHAT
# ===========================================
# Ambil data chat yang sedang aktif
current_chat = st.session_state.chats[st.session_state.current_chat_id]
current_model = AVAILABLE_MODELS[st.session_state.selected_model]

# Container untuk menampilkan percakapan
chat_container = st.container()

with chat_container:
    # Jika belum ada pesan, tampilkan pesan selamat datang yang dipersonalisasi
    if not current_chat["messages"]:
        st.markdown(f"""
        <div style='text-align: center; margin: 50px 0; color: var(--secondary-text-color);'>
            <h3>Hai {st.session_state.user_name}, Apa yang bisa Pouring bantu?</h3>
        </div>
        """, unsafe_allow_html=True)
    
    # Tampilkan semua pesan dalam chat yang aktif
    for i, message in enumerate(current_chat["messages"]):
        
        # Tampilkan pesan dari user dengan nama yang dipersonalisasi
        if message["role"] == "user":
            st.markdown(f"""
            <div class="user-message">
                <div class="message-header">
                    <div class="user-avatar message-avatar">👤</div>
                    <div class="message-name">{st.session_state.user_name}</div>
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
                    <div class="message-name">Pouring</div>
                </div>
                <div>{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Tampilkan loading message jika sedang memproses
    if st.session_state.is_loading:
        st.markdown(f"""
        <div class="loading-message">
            <div class="message-header">
                <div class="ai-avatar message-avatar">🤖</div>
                <div class="message-name">Pouring</div>
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
    not st.session_state.is_loading):
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Regenerate Response", key="regenerate_btn", 
                   help="Generate ulang respons terakhir", use_container_width=True):
            st.session_state.regenerate_last = True
            st.rerun()

# ===========================================
# INPUT CHAT DARI USER
# ===========================================
user_input = st.chat_input(f"Ketik pesan {st.session_state.user_name} disini...")

# ===========================================
# PROSES REGENERATE RESPONSE
# ===========================================
if st.session_state.regenerate_last:
    st.session_state.regenerate_last = False
    
    # Hapus pesan AI terakhir saja, tidak menambah pesan user baru
    if current_chat["messages"] and current_chat["messages"][-1]["role"] == "assistant":
        current_chat["messages"].pop()
        
    # Set loading state untuk regenerate
    st.session_state.is_loading = True
    st.rerun()

# ===========================================
# PROSES INPUT USER & PANGGIL API
# ===========================================
if user_input:
    # Tambahkan pesan user baru hanya jika ini bukan regenerate
    user_message = {
        "role": "user", 
        "content": user_input
    }
    current_chat["messages"].append(user_message)
    
    # Update title chat jika ini pesan pertama
    if len([msg for msg in current_chat["messages"] if msg["role"] == "user"]) == 1:
        if len(user_input) > 30:
            current_chat["title"] = user_input[:30] + "..."
        else:
            current_chat["title"] = user_input
    
    # Set loading state
    st.session_state.is_loading = True
    st.rerun()

# ===========================================
# PROSES API CALL (ASYNC HANDLING)
# ===========================================
if st.session_state.is_loading:
    try:
        # Siapkan format pesan untuk API OpenRouter dengan personalisasi
        messages_for_api = [{"role": "system", "content": f"You are Pouring, a helpful AI assistant. The user's name is {st.session_state.user_name}. Please address them by their name when appropriate and be friendly and helpful."}]
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
        "content": bot_reply
    }
    current_chat["messages"].append(ai_message)
    
    # Reset loading state
    st.session_state.is_loading = False
    
    # Refresh halaman untuk menampilkan pesan baru
    st.rerun()
