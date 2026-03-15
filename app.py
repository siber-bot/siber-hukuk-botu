import streamlit as st
import google.generativeai as genai
import time

# ==========================================
# 1. SAYFA AYARLARI
# ==========================================
st.set_page_config(
    page_title="Siber Hukuk Asistanı",
    page_icon="⚖️",
    layout="wide", # Daha geniş ve inovatif bir alan
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. İNOVATİF VE MODERN KURUMSAL CSS
# ==========================================
st.markdown("""
<style>
/* Temel Arkaplan */
.stApp { background: #FFFFFF; }

/* SOL MENÜ (SIDEBAR) ZORLAYICI VE ŞIK AYARLAR */
[data-testid="stSidebar"] { 
    background-color: #F8FAFC !important; 
    border-right: 1px solid #F1F5F9 !important;
    min-width: 280px !important;
}

/* Sidebar gizlendiğinde butonu sol üstte belirgin yap */
.st-emotion-cache-6qob1r { color: #3B82F6 !important; }

/* Ana İçerik Alanı */
.block-container {
    max-width: 900px !important;
    padding: 3rem 2rem !important;
    margin: 0 auto !important;
}

/* Başlık Tasarımı */
.main-header {
    font-family: 'Inter', sans-serif;
    font-size: 2.5rem;
    font-weight: 800;
    color: #0F172A;
    text-align: center;
    letter-spacing: -0.05em;
    margin-bottom: 0.5rem;
}
.sub-header {
    font-size: 1rem;
    color: #64748B;
    text-align: center;
    margin-bottom: 3rem;
}

/* Mesaj Balonları - Modern Shadow & Radius */
[data-testid="stChatMessage"] {
    background-color: transparent !important;
    padding: 1rem 0 !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown {
    background-color: #F1F5F9 !important;
    border-radius: 20px 20px 4px 20px !important;
    padding: 1rem 1.5rem !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.02) !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown {
    background-color: #FFFFFF !important;
    border: 1px solid #F1F5F9 !important;
    border-radius: 20px 20px 20px 4px !important;
    padding: 1rem 1.5rem !important;
    box-shadow: 0 10px 25px rgba(0,0,0,0.03) !important;
}

/* Chat Giriş Alanı */
[data-testid="stChatInput"] {
    border: 1px solid #E2E8F0 !important;
    border-radius: 15px !important;
    box-shadow: 0 -5px 25px rgba(0,0,0,0.02) !important;
}

/* Özel Bilgi Kartları (Sol Menü) */
.nav-card {
    background: #FFFFFF;
    border: 1px solid #F1F5F9;
    padding: 1.2rem;
    border-radius: 12px;
    margin-bottom: 1rem;
    box-shadow: 0 2px 5px rgba(0,0,0,0.01);
}
.nav-card b { color: #3B82F6; }

/* Gizli Yükleme Yazısı */
.loading-text {
    font-size: 0.85rem;
    color: #94A3B8;
    font-style: italic;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. KORUNAN API VE MODEL AYARLARI
# ==========================================
SISTEM_PROMPTU = """Sen uzman bir Siber Hukuk Asistanısın. Yanıtlarını resmi, akademik seviyede, TCK ve KVKK maddelerine dayalı olarak ver."""

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-3-flash-preview') 
except Exception as e:
    st.error(f"Sistem Hatası: {str(e)}")
    st.stop()

# ==========================================
# 4. SESSION STATE
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# ==========================================
# 5. SOL MENÜ (SIDEBAR) - PRESTİJLİ GÖRÜNÜM
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color:#0F172A;'>⚖️ Navigasyon</h2>", unsafe_allow_html=True)
    st.divider()
    
    st.markdown("""
    <div class="nav-card">
        <b>Geliştirici Ekip</b><br>
        Merve [Soyadı]<br>
        [Adın]
    </div>
    <div class="nav-card">
        <b>Sistem Durumu</b><br>
        Çevrimiçi (Gemini 3 Flash)
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("➕ Analizi Sıfırla", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_session = model.start_chat(history=[])
        st.rerun()
    
    st.divider()
    st.caption("© 2026 Siber Hukuk Teknolojileri")

# ==========================================
# 6. ANA EKRAN
# ==========================================
if not st.session_state.messages:
    st.markdown('<h1 class="main-header">Siber Hukuk Asistanı</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Bilişim Suçları Analiz ve Mevzuat Bilgilendirme Merkezi</p>', unsafe_allow_html=True)

for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "⚖️"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ==========================================
# 7. SOHBET VE SOFT ANİMASYON
# ==========================================
if prompt := st.chat_input("Vaka detaylarını buraya yazın..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚖️"):
        # st.status kaldırıldı, yerine daha zarif bir indicator geldi
        loading_placeholder = st.empty()
        loading_placeholder.markdown('<p class="loading-text">⚖️ Hukuki veritabanı analiz ediliyor...</p>', unsafe_allow_html=True)
        
        try:
            tam_prompt = f"SİSTEM TALİMATI: {SISTEM_PROMPTU}\n\nKULLANICI: {prompt}"
            response = st.session_state.chat_session.send_message(tam_prompt, stream=True)
            
            # Analiz yazısını sil ve yazmaya başla
            loading_placeholder.empty()
            
            full_response = ""
            message_placeholder = st.empty()
            
            for chunk in response:
                full_response += chunk.text
                message_placeholder.markdown(full_response + " ")
                time.sleep(0.01) # Soft akış hızı
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            loading_placeholder.empty()
            st.error(f"Bir hata oluştu: {str(e)}")
