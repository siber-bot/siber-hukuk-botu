import streamlit as st
import google.generativeai as genai

# --- 1. API VE MODEL AYARLARI ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    # Senin seçtiğin en gelişmiş model
    model = genai.GenerativeModel('gemini-3-flash-preview')
except Exception as e:
    st.error("API Anahtarı eksik veya hatalı!")

# --- 2. SAYFA AYARLARI ---
st.set_page_config(page_title="Siber Hukuk Asistanı", page_icon="⚖️", layout="wide")

# --- 3. AGRESİF CSS (TAM KARANLIK TEMA) ---
st.markdown("""
    <style>
    /* Genel Arka Plan */
    .stApp {
        background-color: #212121 !important;
    }

    /* O İNATÇI BEYAZ ALT ŞERİDİ YOK EDEN KISIM */
    div.stChatFloatingInputContainer {
        background-color: #212121 !important; 
        padding-bottom: 2rem !important;
    }
    
    /* Giriş Kutusunun Kendisi (Koyu Gri) */
    [data-testid="stChatInput"] {
        background-color: #2F2F2F !important;
        border: 1px solid #404040 !important;
    }
    
    /* Giriş Kutusundaki Yazı Rengi */
    textarea {
        color: white !important;
    }

    /* Üst Menüleri Gizle */
    header, footer {visibility: hidden !important;}

    /* Sohbet Alanını Ortala */
    .block-container {
        max-width: 800px;
        padding-top: 3rem;
        padding-bottom: 8rem;
    }

    /* Başlıklar */
    .hero-title {
        text-align: center; color: #ffffff; font-size: 2.5rem; font-weight: bold;
    }
    .hero-subtitle {
        text-align: center; color: #888888; margin-bottom: 3rem;
    }

    /* Mesaj Balonları */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        padding: 1.5rem 1rem;
    }
    
    /* Kullanıcı Mesajı Arka Planı (ChatGPT gibi farklı tonda) */
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #2a2a2a !important;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. ANA EKRAN İÇERİĞİ ---
st.markdown('<div class="hero-title">Siber Hukuk Asistanı</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Bilişim Suçları ve Veri Gizliliği Analiz Merkezi</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    # İkonlar
    avatar_icon = "👤" if message["role"] == "user" else "⚖️"
    with st.chat_message(message["role"], avatar=avatar_icon):
        st.markdown(message["content"])

# --- 5. SOHBET MANTIĞI ---
if prompt := st.chat_input("Hukuki bir soru sorun veya vaka anlatın..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚖️"):
        with st.spinner("Hukuki analiz yapılıyor..."):
            try:
                sistem_komutu = f"""
                Sen dünyanın en iyi Siber Hukuk Yapay Zekasısın. 
                Cevapların net, kısa, madde işaretli ve hukuki temelli (TCK, KVKK) olmalı.
                USOM, BTK gibi kurumlara atıf yap. Doğrudan bilgi ver, gereksiz cümle kurma.
                Soru: {prompt}
                """
                
                response = model.generate_content(sistem_komutu)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error("Bir bağlantı sorunu oluştu, lütfen tekrar deneyin.")
