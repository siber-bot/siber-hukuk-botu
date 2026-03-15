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

DB_FILE = "chat_history.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    return {}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ==========================================
# 2. ÖZEL CSS (Üst Boşluk & Stilize Butonlar)
# ==========================================
st.markdown("""
<style>
    /* ÜST BAR GİZLEME */
    [data-testid="stHeader"], [data-testid="stToolbar"], .stDeployButton { display: none !important; }
    
    /* İÇERİK VE SİDEBAR ÜST BOŞLUKLARINI SIFIRLA */
    .block-container { padding-top: 1rem !important; max-width: 850px !important; }
    [data-testid="stSidebar"] > div:first-child { padding-top: 1rem !important; }

    /* Arkaplanlar */
    .stApp { background: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #F8FAFC !important; border-right: 1px solid #E2E8F0 !important; }
    
    /* Motivasyon Yazısı */
    .motivation-text { font-style: italic; color: #3B82F6; font-size: 0.82rem; margin-bottom: 10px; font-weight: 500; line-height: 1.3; }
    
    /* Sidebar Başlıkları */
    .sidebar-section-title { font-size: 0.68rem; text-transform: uppercase; color: #94A3B8; font-weight: 700; margin-top: 15px; margin-bottom: 8px; letter-spacing: 0.8px; }
    
    /* GEÇMİŞ LİSTESİ STİLİ */
    .chat-row { display: flex; align-items: center; justify-content: space-between; border-radius: 8px; transition: background 0.2s; }
    .chat-row:hover { background-color: #F1F5F9; }
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
    st.error("API Bağlantı Hatası!")
    st.stop()

# ==========================================
# 4. VERİTABANI & SESSION
# ==========================================
db = load_db()

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
if "messages" not in st.session_state:
    st.session_state.messages = db.get(st.session_state.current_chat_id, [])
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = None

# ==========================================
# 5. SOL MENÜ (YÖNETİLEBİLİR GEÇMİŞ)
# ==========================================
with st.sidebar:
    st.markdown("<h3 style='color:#0F172A; margin:0;'>⚖️ Siber Asistan</h3>", unsafe_allow_html=True)
    st.markdown('<p class="motivation-text">"Dijital dünyada adaletin rehberi, siber güvenliğin sesi."</p>', unsafe_allow_html=True)
    
    st.markdown('<p class="sidebar-section-title">PROJE SAHİBİ</p>', unsafe_allow_html=True)
    st.markdown("👤 **Merve [Soyadı]**")
    
    st.divider()
    
    if st.button("➕ Yeni Sohbet Başlat", use_container_width=True):
        st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.messages = []
        st.session_state.chat_session = model.start_chat(history=[])
        st.rerun()

    st.markdown('<p class="sidebar-section-title">GEÇMİŞ SOHBETLER</p>', unsafe_allow_html=True)
    
    # Sohbetleri Listele ve Yönet
    temp_db = db.copy()
    for chat_id in sorted(temp_db.keys(), reverse=True):
        col_main, col_edit, col_del = st.columns([0.7, 0.15, 0.15])
        
        # Sohbet Başlığı
        with col_main:
            if st.session_state.edit_mode == chat_id:
                new_title = st.text_input("Başlık", value=temp_db[chat_id][0].get("title", temp_db[chat_id][0]["content"][:20]), key=f"in_{chat_id}", label_visibility="collapsed")
                if st.button("✅", key=f"save_{chat_id}"):
                    # Sadece ilk mesajda başlık bilgisini saklıyoruz
                    temp_db[chat_id][0]["title"] = new_title
                    save_db(temp_db)
                    st.session_state.edit_mode = None
                    st.rerun()
            else:
                current_title = temp_db[chat_id][0].get("title", temp_db[chat_id][0]["content"][:22] + "...")
                if st.button(f"💬 {current_title}", key=f"chat_{chat_id}", use_container_width=True):
                    st.session_state.current_chat_id = chat_id
                    st.session_state.messages = temp_db[chat_id]
                    st.rerun()
        
        # Düzenle Butonu
        with col_edit:
            if st.button("✏️", key=f"ed_{chat_id}", help="Başlığı Düzenle"):
                st.session_state.edit_mode = chat_id
                st.rerun()
        
        # Silme Butonu
        with col_del:
            if st.button("🗑️", key=f"del_{chat_id}", help="Sohbeti Sil"):
                del temp_db[chat_id]
                save_db(temp_db)
                if st.session_state.current_chat_id == chat_id:
                    st.session_state.messages = []
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
# 7. SOHBET AKIŞI
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
                message_placeholder.markdown(full_response + "▌")
                time.sleep(0.01)
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # Veritabanına kaydet
            db[st.session_state.current_chat_id] = st.session_state.messages
            save_db(db)
            
        except Exception as e:
            status_info.empty()
            st.error(f"Hata: {str(e)}")
