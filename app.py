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
    @media (prefers-color-scheme: light) {
        :root {
            --background-color: #ffffff;
            --background-color-secondary: #f0f2f6;
            --text-color: #262730;
            --border-color: #e1e5e9;
            --secondary-text-color: #6b7280;
            --hover-color: #f3f4f6;
        }
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
    /* Styling untuk welcome section */
    .welcome-container {
        max-width: 600px;
        margin: 0 auto;
        padding: 20px;
    }
</style>
""", unsafe_allow_html=True)
