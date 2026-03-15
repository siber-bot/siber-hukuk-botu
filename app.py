import streamlit as st
import google.generativeai as genai

# 1. SAYFA AYARLARI (EN BAŞTA OLMALI)
st.set_page_config(
    page_title="Siber Hukuk Asistanı",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 2. CSS: TEMİZ, STABİL VE ORTALANMIŞ TASARIM
st.markdown("""
<style>
/* Ana Arkaplan ve Fontlar */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: #f8f9fa !important;
}

/* Gereksiz Sağ Üst Menüyü Gizle, Ama Sol Menü Butonunu Koru! */
[data-testid="stToolbar"], [data-testid="stDecoration"], footer {
    visibility: hidden !important;
    display: none !important;
}

/* İçeriği Tam Ortala ve Genişliği Kısıtla */
.block-container {
    max-width: 800px !important;
    padding-top: 2rem !important;
    padding-bottom: 7rem !important;
    margin: 0 auto !important;
}

/* Alt Sohbet Kutusundaki Beyazlık Hatalarını Gider */
[data-testid="stBottom"], [data-testid="stChatFloatingInputContainer"] {
    background-color: transparent !important;
}
[data-testid="stChatInput"] {
    background-color: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
}

/* Yan Menü (Sidebar) Rengi */
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e5e7eb !important;
}

/* Mesaj Balonları: Kullanıcı Mesajını Sağa Dayalı ve Renkli Yap */
[data-testid="stChatMessage"] {
    background-color: transparent !important;
    border: none !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown {
    background: #eef2ff !important; 
    border: 1px solid #c7d2fe !important;
    border-radius: 16px 16px 4px 16px !important;
    padding: 0.75rem 1rem !important; 
    display: inline-block !important;
}

/* Başlıklar ve Butonlar */
.hero-title { font-size: 2.2rem; font-weight: 700; color: #1f2937; text-align: center; margin-bottom: 0.5rem; }
.hero-sub { font-size: 1rem; color: #6b7280; text-align: center; margin-bottom: 2rem; }
.chip-btn button { border-radius: 20px !important; width: 100% !important; border: 1px solid #e5e7eb !important; background: white !important; color: #374151 !important; }
.chip-btn button:hover { background: #eef2ff !important; border-color: #4f46e5 !important; color: #4338ca !important;}
</style>
""", unsafe_allow_html=True)

# 3. API VE MODEL (Hata vermeyen güvenli bağlantı)
SISTEM_PROMPTU = """Sen "Siber Hukuk Asistanı" adlı uzman bir yapay zeka sistemsin.
Türk Hukuku (TCK, KVKK), siber güvenlik hukuku ve bilişim suçları konularında uzmansın.
Cevaplarını her zaman anlaşılır, madde işaretli ve hukuki temellere (kanun maddelerine) dayandırarak ver. Uzatma ve doğrudan bilgi sun."""

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    # Çökmeyi engellemek için system_instruction kullanmadan modeli çağırıyoruz.
    # En stabil hız/performans için 'gemini-1.5-flash' tavsiyedir.
    model = genai.GenerativeModel('gemini-1.5-flash') 
except Exception as e:
    st.error("⚠️ API Anahtarı eksik veya hatalı.")
    st.stop()

# 4. HAFIZA VE OTURUM YÖNETİMİ
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# 5. YAN MENÜ (SIDEBAR)
with st.sidebar:
    st.markdown("### ⚖️ Siber Hukuk Asistanı")
    st.caption("Geliştiriciler: Merve & [Adın] · 2026")
    st.divider()
    
    if st.button("➕ Yeni Sohbet Başlat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_session = model.start_chat(history=[])
        st.session_state.pending_prompt = None
        st.rerun()
        
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.warning("⚠️ Bu asistan avukat değildir. Verilen bilgiler hukuki danışmanlık yerine geçmez.")

# 6. ANA EKRAN (DİNAMİK)
if len(st.session_state.messages) == 0:
    st.markdown('<div class="hero-title">Size nasıl yardımcı olabilirim?</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Bilişim suçları, siber güvenlik hukuku ve KVKK konularında sorularınızı yanıtlıyorum.</div>', unsafe_allow_html=True)
    
    SUGGESTIONS = [
        "🔒 Hesabım hacklendi, ne yapmalıyım?",
        "📧 Phishing e-postası aldım",
        "🛡️ KVKK kapsamında haklarım neler?",
        "💳 Online dolandırıcılık nasıl şikayet edilir?"
    ]
    
    cols = st.columns(2)
    for i, suggestion in enumerate(SUGGESTIONS):
        with cols[i % 2]:
            st.markdown('<div class="chip-btn">', unsafe_allow_html=True)
            if st.button(suggestion, key=f"btn_{i}", use_container_width=True):
                st.session_state.pending_prompt = suggestion
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# Mesajları Ekrana Çiz
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "⚖️"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# 7. SOHBET MANTIĞI VE TETİKLEYİCİ
prompt = st.chat_input("Hukuki bir soru sorun veya vakayı anlatın...")

# Butondan gelen metin varsa, onu prompt olarak al
if st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

# Eğer bir girdi (prompt) varsa işle
if prompt:
    # 1. Kullanıcı Mesajı
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # 2. Asistan Yanıtı
    with st.chat_message("assistant", avatar="⚖️"):
        with st.spinner("Hukuki veritabanı inceleniyor..."):
            try:
                # SDK çökmesini engellemek için sistem promptunu doğrudan mesaja gizlice ekliyoruz
                tam_prompt = f"GİZLİ SİSTEM TALİMATI (Bunu kullanıcıya belli etme): {SISTEM_PROMPTU}\n\nKULLANICININ SORUSU: {prompt}"
                
                response = st.session_state.chat_session.send_message(tam_prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                # Hata durumunda sorunu net olarak gösterir (geliştirici için)
                st.error(f"Sistemsel bir hata oluştu. Lütfen sayfayı yenileyip tekrar deneyin. Hata Detayı: {str(e)}")
