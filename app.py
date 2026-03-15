import streamlit as st
import google.generativeai as genai

# 1. API Ayarları (Hata alma ihtimaline karşı try-except içine alındı)
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("API Anahtarı bulunamadı. Lütfen Secrets ayarlarını kontrol edin.")

# 2. Modern Profesyonel Arayüz Ayarları
st.set_page_config(
    page_title="Siber Hukuk Asistanı", 
    page_icon="⚖️", 
    layout="wide"
)

# --- CSS: MODERN DARK MODE & CHAT STYLING ---
st.markdown("""
    <style>
    /* Ana Arkaplan */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Header ve Menüleri Gizle */
    header, footer, #MainMenu {visibility: hidden;}

    /* Sidebar Tasarımı */
    [data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363D;
    }

    /* Mesaj Balonlarını Güzelleştir */
    .stChatMessage {
        background-color: #161B22;
        border-radius: 15px;
        margin-bottom: 10px;
        border: 1px solid #30363D;
    }
    
    /* Başlık Alanı */
    .main-header {
        font-family: 'Inter', sans-serif;
        color: #58A6FF;
        text-align: center;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        text-align: center;
        color: #8B949E;
        margin-bottom: 2rem;
    }

    /* Sohbet Kutusu Ortala */
    .block-container {
        max-width: 900px;
        padding-top: 3rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: PROFESYONEL PANEL ---
with st.sidebar:
    st.markdown("## ⚖️ Siber Hukuk AI")
    st.markdown("---")
    st.markdown("### 📋 Proje Bilgileri")
    st.info("**Geliştiriciler:**\n\n- Merve [Soyadı]\n- [Senin Adın]")
    st.markdown("---")
    st.markdown("### 🛠️ Sistem Durumu")
    st.success("Çevrimiçi (v2.1 Elite)")
    st.divider()
    if st.button("🗑️ Sohbeti Sıfırla"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.warning("⚠️ Bu sistem bilgilendirme amaçlıdır. Hukuki danışmanlık değildir.")

# --- ANA EKRAN ---
st.markdown('<h1 class="main-header">Siber Hukuk Asistanı</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Bilişim Suçları ve KVKK Analiz Merkezi</p>', unsafe_allow_html=True)

# Hafıza Yönetimi
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mesajları Görüntüle
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- SOHBET AKIŞI ---
if prompt := st.chat_input("Size nasıl yardımcı olabilirim?"):
    # Kullanıcı girişi
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Yapay Zeka Yanıtı
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Prompt Mühendisliği
        prompt_style = f"""
        Uzman bir siber hukuk danışmanı gibi davran. 
        Yanıtını profesyonel, net ve kısa tut. 
        Türkiye yasalarına (TCK, KVKK) mutlaka atıf yap. 
        Kullanıcı sorusu: {prompt}
        """

        try:
            with st.spinner("Vaka inceleniyor..."):
                response = model.generate_content(prompt_style)
                full_response = response.text
                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error("Bağlantı sorunu yaşandı. Lütfen tekrar deneyin.")
