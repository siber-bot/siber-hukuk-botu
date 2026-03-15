import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. API VE MODEL AYARLARI
# ==========================================
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    # Gelişmiş modelimiz
    model = genai.GenerativeModel('gemini-3-flash-preview')
except Exception as e:
    st.error("⚠️ Sistem Başlatılamadı: API Anahtarı eksik veya hatalı.")

# ==========================================
# 2. SAYFA VE ARAYÜZ YAPILANDIRMASI
# ==========================================
st.set_page_config(
    page_title="Siber Hukuk Asistanı", 
    page_icon="⚖️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- İYİLEŞTİRİLMİŞ, KUSURSUZ CSS ---
st.markdown("""
    <style>
    /* 1. Tam Karanlık Tema */
    .stApp {
        background-color: #212121 !important;
        color: #ECECEC;
    }
    
    /* 2. HEADER DÜZELTMESİ (Menü tuşunu geri getiren sihir) */
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }
    /* Sadece sağ üstteki gereksiz 'Deploy' vs. menüsünü gizle */
    .stApp > header > div:not(:first-child) {
        display: none !important;
    }
    footer {visibility: hidden !important;}

    /* 3. ÖLÜ BOŞLUKLARI TEMİZLEME */
    .block-container {
        max-width: 800px;
        padding-top: 1.5rem !important; /* Üstteki o dev siyahlığı yok ettik */
        padding-bottom: 6rem !important;
    }

    /* 4. CHAT GİRİŞ KUTUSU (Gömülü ve Şık) */
    [data-testid="stChatFloatingInputContainer"] {
        background-color: #212121 !important;
    }
    [data-testid="stChatInput"] {
        background-color: #2F2F2F !important;
        border: 1px solid #404040 !important;
        border-radius: 12px !important;
    }
    textarea {
        color: #FFFFFF !important;
    }

    /* 5. MESAJ BALONLARI */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        padding: 1.5rem 1rem;
        border: none !important;
    }
    /* Kullanıcı mesajlarını çok hafif gri yaparak ayrıştır */
    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: #2A2A2A !important;
        border-radius: 10px;
    }

    /* 6. BAŞLIK TASARIMI */
    .hero-title {
        text-align: center; color: #ffffff; font-size: 2.8rem; font-weight: 700; margin-top: 2rem;
    }
    .hero-subtitle {
        text-align: center; color: #8E8EA0; font-size: 1.1rem; margin-bottom: 3rem;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. YAN MENÜ (SIDEBAR) 
# ==========================================
with st.sidebar:
    st.markdown("## ⚖️ Siber AI")
    st.markdown("<span style='color: #8E8EA0; font-size: 0.9rem;'>V3.1 Pro Sürümü</span>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("### 📋 Proje Ekibi")
    st.info("👤 Merve [Soyadı]\n\n👤 [Senin Adın]")
    
    st.markdown("---")
    if st.button("🔄 Yeni Analiz Başlat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.warning("⚠️ **Önemli:**\nBu asistan avukat değildir. Yasal danışmanlık içermez.")

# ==========================================
# 4. HAFIZA VE DİNAMİK EKRAN
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# DİNAMİK BAŞLIK: Sadece sohbet boşken başlıkları göster
if len(st.session_state.messages) == 0:
    st.markdown('<div class="hero-title">Siber Hukuk Asistanı</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Bilişim Suçları ve Veri Gizliliği (KVKK) Analiz Merkezi</div>', unsafe_allow_html=True)

# Önceki Mesajları Çiz
for message in st.session_state.messages:
    avatar_icon = "👤" if message["role"] == "user" else "⚖️"
    with st.chat_message(message["role"], avatar=avatar_icon):
        st.markdown(message["content"])

# ==========================================
# 5. SOHBET AKIŞI
# ==========================================
if prompt := st.chat_input("Hukuki bir soru sorun veya vaka anlatın..."):
    
    # Kullanıcı mesajını ekle
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Asistan Yanıtı
    with st.chat_message("assistant", avatar="⚖️"):
        with st.spinner("Vaka analizi yapılıyor..."):
            try:
                # Prompt Mühendisliği
                sistem_komutu = f"""
                Sen dünyanın en gelişmiş Siber Hukuk Yapay Zekasısın. 
                Cevaplarını son derece profesyonel, net ve yapılandırılmış bir dille ver.
                Lafı uzatma, doğrudan konuya gir.
                Türk Hukukuna (TCK, KVKK) ve USOM/BTK gibi kurumlara atıf yap.
                Maddeleme ve kalın (bold) yazılar kullanarak okunabilirliği artır.
                Soru: {prompt}
                """
                
                response = model.generate_content(sistem_komutu)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
                # Başlıkların kaybolması için sayfayı hafifçe yeniden yükle
                if len(st.session_state.messages) == 2:
                    st.rerun()
                    
            except Exception as e:
                st.error("Sunucularımızda anlık bir yoğunluk var. Lütfen tekrar deneyin.")
