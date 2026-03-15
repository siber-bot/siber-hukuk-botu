import streamlit as st
import google.generativeai as genai
import time
import json
import os
from datetime import datetime

# ==========================================
# 1. SAYFA AYARLARI
# ==========================================
st.set_page_config(
    page_title="Siber Hukuk Asistanı",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sohbet kayıt dosyası
DB_FILE = "chat_history.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    return {}

def save_db(data):
    # Son 10 sohbet limiti
    if len(data) > 10:
        sorted_keys = sorted(data.keys(), reverse=True)[:10]
        data = {k: data[k] for k in sorted_keys}
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ==========================================
# 2. ÖZEL CSS (Üst Barı Gizleme & Şık Geçmiş)
# ==========================================
st.markdown("""
<style>
    /* ÜST BARDAKİ İKONLARI VE MENÜYÜ TAMAMEN GİZLE */
    [data-testid="stHeader"], [data-testid="stToolbar"], .stDeployButton {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Sayfanın en üstündeki boşluğu ayarla */
    .block-container { padding-top: 2rem !important; max-width: 850px !important; }

    /* Arkaplan ve Sidebar */
    .stApp { background: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #F8FAFC !important; border-right: 1px solid #E2E8F0 !important; }
    
    /* Motivasyon Yazısı */
    .motivation-text { font-style: italic; color: #3B82F6; font-size: 0.85rem; margin-bottom: 15px; font-weight: 500; line-height: 1.4; }
    
    /* Sidebar Başlıkları */
    .sidebar-section-title { font-size: 0.7rem; text-transform: uppercase; color: #94A3B8; font-weight: 700; margin-top: 25px; margin-bottom: 10px; letter-spacing: 1px; }
    
    /* STİLİZE GEÇMİŞ SOHBET BUTONLARI */
    .stButton > button {
        width: 100%;
        border: none !important;
        background-color: transparent !important;
        color: #475569 !important;
        text-align: left !important;
        padding: 10px 15px !important;
        border-radius: 8px !important;
        font-size: 0.85rem !important;
        transition: all 0.2s ease !important;
        display: block !important;
    }
    .stButton > button:hover {
        background-color: #F1F5F9 !important;
        color: #1E293B !important;
    }
    
    /* Mesaj Balonları */
    [data-testid="stChatMessage"] { padding: 0.8rem 0 !important; }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown {
        background-color: #F1F5F9 !important; border-radius: 18px 18px 0 18px !important; padding: 12px 18px !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown {
        background-color: #FFFFFF !important; border: 1px solid #F1F5F9 !important; border-radius: 18px 18px 18px 0 !important; padding: 12px 18px !important; box-shadow: 0 4px 15px rgba(0,0,0,0.03) !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. API VE MODEL
# ==========================================
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-3-flash-preview') 
except Exception as e:
    st.error(f"API Bağlantı Hatası: {str(e)}")
    st.stop()

# ==========================================
# 4. VERİTABANI & SESSION YÖNETİMİ
# ==========================================
db = load_db()

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")

if "messages" not in st.session_state:
    if st.session_state.current_chat_id in db:
        st.session_state.messages = db[st.session_state.current_chat_id]
    else:
        st.session_state.messages = []

if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# ==========================================
# 5. SOL MENÜ (TEMİZ VE STİLİZE)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color:#0F172A; margin-bottom:5px;'>⚖️ Siber Asistan</h2>", unsafe_allow_html=True)
    st.markdown('<p class="motivation-text">"Dijital dünyada adaletin rehberi, siber güvenliğin sesi."</p>', unsafe_allow_html=True)
    
    st.markdown('<p class="sidebar-section-title">PROJE SAHİBİ</p>', unsafe_allow_html=True)
    st.markdown("👤 **Merve [Soyadı]**")
    
    st.divider()
    
    # Yeni Sohbet Butonu (Daha belirgin)
    if st.button("➕ Yeni Sohbet Başlat", use_container_width=True):
        st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.messages = []
        st.session_state.chat_session = model.start_chat(history=[])
        st.rerun()

    st.markdown('<p class="sidebar-section-title">GEÇMİŞ SOHBETLER</p>', unsafe_allow_html=True)
    
    # Geçmiş Sohbetlerin Listelenmesi (Hover efektli tam satır)
    for chat_id in sorted(db.keys(), reverse=True):
        if db[chat_id]:
            label = "💬 " + (db[chat_id][0]["content"][:22] + "..." if len(db[chat_id][0]["content"]) > 22 else db[chat_id][0]["content"])
            if st.button(label, key=f"btn_{chat_id}"):
                st.session_state.current_chat_id = chat_id
                st.session_state.messages = db[chat_id]
                st.rerun()

# ==========================================
# 6. ANA EKRAN
# ==========================================
if not st.session_state.messages:
    st.markdown('<h1 style="text-align:center; color:#0F172A; font-size: 2.2rem;">Siber Hukuk Analizi</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#64748B;">Lütfen vaka detaylarını girin veya hukuki bir soru sorun.</p>', unsafe_allow_html=True)

for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "⚖️"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ==========================================
# 7. SOHBET & SOFT YAZMA
# ==========================================
if prompt := st.chat_input("Hukuki bir soru sorun..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚖️"):
        status_info = st.empty()
        status_info.markdown('<p style="color:#94A3B8; font-style:italic; font-size: 0.85rem;">⚖️ Analiz ediliyor...</p>', unsafe_allow_html=True)
        
        try:
            response = st.session_state.chat_session.send_message(prompt, stream=True)
            status_info.empty()
            
            full_response = ""
            message_placeholder = st.empty()
            
            for chunk in response:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌") # İmleç efekti eklendi
                time.sleep(0.01)
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # Veritabanını güncelle
            db[st.session_state.current_chat_id] = st.session_state.messages
            save_db(db)
            
        except Exception as e:
            status_info.empty()
            st.error(f"Bir hata oluştu: {str(e)}")
