import streamlit as st
import google.generativeai as genai
import time
import json
import os
from datetime import datetime

# ==========================================
# 1. SAYFA AYARLARI VE YAPILANDIRMA
# ==========================================
st.set_page_config(
    page_title="Siber Hukuk Asistanı",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sohbetleri kaydetmek için dosya yolu
DB_FILE = "chat_history.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_db(data):
    # Performans için son 10 sohbeti tut
    if len(data) > 10:
        sorted_keys = sorted(data.keys(), reverse=True)[:10]
        data = {k: data[k] for k in sorted_keys}
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ==========================================
# 2. MODERN KURUMSAL CSS
# ==========================================
st.markdown("""
<style>
    .stApp { background: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #F8FAFC !important; border-right: 1px solid #E2E8F0 !important; }
    .block-container { max-width: 850px !important; padding-top: 2rem !important; }
    
    /* Motivasyon Yazısı */
    .motivation-text { font-style: italic; color: #3B82F6; font-size: 0.9rem; margin-bottom: 15px; font-weight: 500; }
    
    /* Sidebar Section */
    .sidebar-section-title { font-size: 0.75rem; text-transform: uppercase; color: #94A3B8; font-weight: 700; margin-top: 20px; margin-bottom: 10px; letter-spacing: 1px; }
    
    /* Mesaj Balonları */
    [data-testid="stChatMessage"] { padding: 1rem 0 !important; }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown {
        background-color: #F1F5F9 !important; border-radius: 15px 15px 0 15px !important; padding: 12px 18px !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown {
        background-color: #FFFFFF !important; border: 1px solid #F1F5F9 !important; border-radius: 15px 15px 15px 0 !important; padding: 12px 18px !important; box-shadow: 0 4px 12px rgba(0,0,0,0.03) !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. API VE MODEL (KORUNAN ALAN)
# ==========================================
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-3-flash-preview') 
except Exception as e:
    st.error(f"API Hatası: {str(e)}")
    st.stop()

# ==========================================
# 4. HAFIZA VE VERİ TABANI YÖNETİMİ
# ==========================================
db = load_db()

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")

if "messages" not in st.session_state:
    # Eğer bu ID'ye ait bir kayıt varsa yükle
    if st.session_state.current_chat_id in db:
        st.session_state.messages = db[st.session_state.current_chat_id]
    else:
        st.session_state.messages = []

if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# ==========================================
# 5. SOL MENÜ (KALICI VE DÜZENLİ)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color:#0F172A; margin-bottom:0;'>⚖️ Siber Asistan</h2>", unsafe_allow_html=True)
    st.markdown('<p class="motivation-text">"Dijital dünyada adaletin rehberi, siber güvenliğin sesi."</p>', unsafe_allow_html=True)
    
    st.markdown('<p class="sidebar-section-title">PROJE SAHİBİ</p>', unsafe_allow_html=True)
    st.markdown("👤 **Merve [Soyadı]**")
    
    st.divider()
    
    st.markdown('<p class="sidebar-section-title">GEÇMİŞ SOHBETLER</p>', unsafe_allow_html=True)
    
    # Yeni Sohbet Butonu
    if st.button("➕ Yeni Sohbet Başlat", use_container_width=True):
        st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.messages = []
        st.session_state.chat_session = model.start_chat(history=[])
        st.rerun()

    # Kayıtlı Sohbetleri Listele
    for chat_id in sorted(db.keys(), reverse=True):
        # İlk mesajın bir kısmını başlık olarak kullan
        label = db[chat_id][0]["content"][:25] + "..." if db[chat_id] else f"Sohbet {chat_id}"
        if st.button(label, key=chat_id, use_container_width=True):
            st.session_state.current_chat_id = chat_id
            st.session_state.messages = db[chat_id]
            st.rerun()

# ==========================================
# 6. ANA EKRAN
# ==========================================
if not st.session_state.messages:
    st.markdown('<h1 style="text-align:center; color:#0F172A;">Siber Hukuk Analiz Sistemi</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#64748B;">Vakanızı yazın, TCK ve KVKK kapsamında analiz edelim.</p>', unsafe_allow_html=True)

for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "⚖️"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ==========================================
# 7. SOHBET VE YAZMA ANİMASYONU
# ==========================================
if prompt := st.chat_input("Hukuki bir soru sorun..."):
    
    # Kullanıcı mesajını ekle
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Yanıt üret
    with st.chat_message("assistant", avatar="⚖️"):
        status_text = st.empty()
        status_text.markdown('<p style="color:#94A3B8; font-style:italic;">⚖️ Mevzuat taranıyor...</p>', unsafe_allow_html=True)
        
        try:
            response = st.session_state.chat_session.send_message(prompt, stream=True)
            status_text.empty()
            
            full_response = ""
            message_placeholder = st.empty()
            
            for chunk in response:
                full_response += chunk.text
                message_placeholder.markdown(full_response + " ")
                time.sleep(0.01)
            
            # Yanıtı kaydet
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # VERİTABANINA YAZ
            db[st.session_state.current_chat_id] = st.session_state.messages
            save_db(db)
            
        except Exception as e:
            status_text.empty()
            st.error(f"Hata: {str(e)}")
