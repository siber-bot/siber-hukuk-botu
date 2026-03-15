import streamlit as st
import google.generativeai as genai

# 1. API Ayarları
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. ChatGPT/Gemini Tarzı Sade Arayüz Ayarları
st.set_page_config(
    page_title="Siber Hukuk Asistanı", 
    page_icon="⚖️", 
    layout="wide" # Geniş ekran, daha modern durur
)

# --- CSS İLE ÖZEL MAKYAJ (Sadelik İçin) ---
st.markdown("""
    <style>
    /* Üstteki Streamlit menülerini gizle */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Mesaj alanını ortala ve genişliğini ayarla */
    .block-container {
        max-width: 800px;
        padding-top: 2rem;
    }
    
    /* Başlık stilini sadeleştir */
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
        color: #FFFFFF;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (Minimalist) ---
with st.sidebar:
    st.markdown("### ⚖️ Siber Hukuk Asistanı")
    st.caption("Versiyon 2.0 | Akademik Proje")
    st.divider()
    st.markdown("""
    **Geliştiriciler:**
    - Merve [Soyadı]
    - [Senin Adın]
    """)
    st.divider()
    st.warning("Hukuki danışmanlık değildir. Bilgilendirme amaçlıdır.")
    if st.button("Sohbeti Temizle"):
        st.session_state.messages = []
        st.rerun()

# --- ANA EKRAN ---
st.markdown('<p class="main-title">Siber Hukuk Asistanı</p>', unsafe_allow_html=True)

# Mesaj Geçmişi Başlatma
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mesajları Ekrana Basma (Avatar kullanarak daha şık görünüm)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- SOHBET GİRİŞİ ---
if prompt := st.chat_input("Nasıl yardımcı olabilirim?"):
    # Kullanıcı mesajı
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gemini Zekâ Komutları (Prompt Engineering)
    sistem_talimati = f"""
    Sen uzman bir Siber Hukuk Asistanısın. Cevaplarını ChatGPT/Gemini tarzında, 
    son derece sade, anlaşılır ve profesyonel ver. 
    - Gereksiz giriş-sonuç cümlelerini at.
    - Olayı Analiz, Riskler ve Öneriler şeklinde kısa maddelerle açıkla.
    - Türkiye hukukuna (TCK, KVKK) ve kurumlarına (USOM, BTK) odaklan.
    - Her mesajda yasal uyarı yapma (sidebar'da mevcut).
    
    Soru: {prompt}
    """

    # Asistan cevabı
    with st.chat_message("assistant"):
        with st.spinner(""): # Sade bir bekleme simgesi
            try:
                response = model.generate_content(sistem_talimati)
                full_response = response.text
                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error("Bir hata oluştu, lütfen tekrar deneyin.")
