import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. API VE MODEL AYARLARI
# ==========================================
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    # Hızlı ve stabil yanıtlar için ideal model
    model = genai.GenerativeModel('gemini-3-flash-preview')
except Exception as e:
    st.error("⚠️ Sistem Başlatılamadı: API Anahtarı eksik veya hatalı.")

# ==========================================
# 2. SAYFA VE ARAYÜZ (UI) YAPILANDIRMASI
# ==========================================
st.set_page_config(
    page_title="Siber Hukuk Asistanı | V3.0", 
    page_icon="⚖️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- İleri Düzey CSS Enjeksiyonu (ChatGPT Tarzı) ---
st.markdown("""
    <style>
    /* 1. Temel Arkaplan ve Fontlar (Tam ChatGPT Koyu Teması) */
    .stApp {
        background-color: #212121;
        color: #ECECEC;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* 2. Streamlit'in Kendi Menülerini Gizle (Temiz Görünüm) */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}

    /* 3. Ana Sohbet Alanını Ortala ve Genişliğini Sınırla */
    .block-container {
        max-width: 800px;
        padding-top: 3rem;
        padding-bottom: 8rem; /* Alttaki giriş kutusu için boşluk */
    }

    /* 4. Başlık Tasarımı */
    .hero-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 0.2rem;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        text-align: center;
        font-size: 1.1rem;
        color: #8E8EA0;
        margin-bottom: 3rem;
        font-weight: 400;
    }

    /* 5. Mesaj Balonları Özelleştirmesi */
    [data-testid="stChatMessage"] {
        padding: 1.5rem 1rem;
        border-radius: 0.5rem;
        background-color: transparent;
    }
    
    /* Kullanıcı Mesajı Arkaplanı */
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #2F2F2F;
    }

    /* 6. Sohbet Giriş Kutusu (Input Box) */
    .stChatInputContainer {
        padding-bottom: 2rem;
    }
    .stChatInputContainer > div {
        background-color: #2F2F2F !important;
        border: 1px solid #404040 !important;
        border-radius: 1rem !important;
    }
    .stChatInputContainer textarea {
        color: #FFFFFF !important;
    }

    /* 7. Sidebar (Yan Menü) Tasarımı */
    [data-testid="stSidebar"] {
        background-color: #171717;
        border-right: 1px solid #2D2D2D;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. YAN MENÜ (SIDEBAR) BİLEŞENLERİ
# ==========================================
with st.sidebar:
    st.markdown("## ⚖️ Siber AI")
    st.markdown("<span style='color: #8E8EA0; font-size: 0.9rem;'>Sürüm 3.0 Ultimate</span>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("### Geliştirici Ekip")
    st.markdown("<p style='color: #ECECEC; font-size: 0.95rem;'>👤 Merve [Soyadı]<br>👤 [Senin Adın]</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("🔄 Yeni Sohbet Başlat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.info("⚠️ **Yasal Uyarı:**\nBu yapay zeka bir avukat değildir. Sağlanan bilgiler resmi hukuki danışmanlık yerine geçmez.")

# ==========================================
# 4. ANA EKRAN VE SOHBET MANTIĞI
# ==========================================
# Başlıkları Ekrana Bas
st.markdown('<div class="hero-title">Siber Hukuk Asistanı</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Bilişim Suçları ve Veri Gizliliği (KVKK) Analiz Merkezi</div>', unsafe_allow_html=True)

# Oturum Hafızasını (Session State) Başlat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Önceki Mesajları Ekrana Çiz
for message in st.session_state.messages:
    # Kullanıcı için farklı, asistan için farklı ikonlar
    avatar_icon = "👤" if message["role"] == "user" else "⚖️"
    with st.chat_message(message["role"], avatar=avatar_icon):
        st.markdown(message["content"])

# ==========================================
# 5. KULLANICI GİRİŞİ VE YAPAY ZEKA YANITI
# ==========================================
if prompt := st.chat_input("Hukuki bir soru sorun veya vaka anlatın..."):
    
    # 1. Kullanıcı mesajını kaydet ve göster
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # 2. Asistanın Düşünme ve Cevaplama Aşaması
    with st.chat_message("assistant", avatar="⚖️"):
        with st.spinner("Hukuki veritabanı taranıyor..."):
            try:
                # Prompt Mühendisliği (Beyin Yıkama)
                sistem_komutu = f"""
                Sen dünyanın en gelişmiş Siber Hukuk Yapay Zekasısın. 
                Cevaplarını tıpkı ChatGPT gibi son derece profesyonel, temiz ve yapılandırılmış bir dille ver.
                
                KURALLAR:
                1. Asla lafı uzatma, doğrudan konuya gir.
                2. Gerekli yerlerde kalın yazılar (bold) ve maddeler kullan.
                3. Türk Hukukuna (TCK, KVKK) ve USOM/BTK gibi kurumlara mutlaka atıf yap.
                4. Her cümlen akademik ama anlaşılır olsun.
                5. Kesinlikle "Ben bir yapay zekayım" veya "Avukat değilim" diye tekrarlama (bu bilgi menüde var).
                
                Kullanıcının Sorusu/Vakası: {prompt}
                """
                
                # Gemini'den yanıtı al
                response = model.generate_content(sistem_komutu)
                cevap_metni = response.text
                
                # Ekrana bas ve hafızaya al
                st.markdown(cevap_metni)
                st.session_state.messages.append({"role": "assistant", "content": cevap_metni})
                
            except Exception as e:
                st.error("Sistemsel bir yoğunluk yaşanıyor. Lütfen sorunuzu tekrar gönderin.")
