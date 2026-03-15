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
# 2. ÖZEL CSS: MENÜ BUTONU VE İNOVATİF UI
# ==========================================
st.markdown("""
<style>
    /* ÜST BARI VE STANDART MENÜYÜ GİZLE */
    [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }

    /* MENÜ KAPALIYKEN SOL ÜSTTE DURAN ÖZEL AÇMA BUTONU (HER ZAMAN GÖRÜNÜR) */
    .menu-trigger {
        position: fixed;
        top: 15px;
        left: 15px;
        z-index: 999999;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 5px 10px;
        cursor: pointer;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        color: #3B82F6;
        font-weight: bold;
    }

    /* ANA KONTEYNER */
    .block-container { padding-top: 1rem !important; max-width: 850px !important; }
    [data-testid="stSidebar"] { 
        background-color: #F8FAFC !important; 
        border-right: 1px solid #E2E8F0 !important;
    }

    /* İNOVATİF SOHBET LİSTESİ TASARIMI */
    .stButton > button {
        border: none !important;
        background: transparent !important;
        transition: all 0.2s ease-in-out !important;
    }
    
    /* Yan menüdeki sohbet butonları: Resmi ve İnovatif */
    div[data-testid="stVerticalBlock"] div.stButton > button {
        text-align: left !important;
        width: 100% !important;
        padding: 8px 12px !important;
        color: #475569 !important;
        font-size: 0.9rem !important;
        border-radius: 10px !important;
    }

    div[data-testid="stVerticalBlock"] div.stButton > button:hover {
        background-color: #F1F5F9 !important;
        color: #1E293B !important;
        transform: translateX(3px);
    }

    /* YENİ ANALİZ BUTONU (Resmi Mavi) */
    .stButton > button[kind="primary"] {
        background: #1E293B !important; /* Koyu Lacivert/Resmi */
        color: #FFFFFF !important;
        border-radius: 12px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
    }

    /* MESAJ BALONLARI */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown {
        background-color: #F1F5F9 !important;
        border-radius: 18px 18px 0 18px !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown {
        background-color: #FFFFFF !important;
        border: 1px solid #F1F5F9 !important;
        border-radius: 18px 18px 18px 0 !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.02) !important;
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
except:
    st.error("Bağlantı Hatası!")
    st.stop()

# ==========================================
# 4. DATA & SESSION
# ==========================================
db = load_db()

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
if "messages" not in st.session_state:
    st.session_state.messages = db.get(st.session_state.current_chat_id, [])
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
if "edit_target" not in st.session_state:
    st.session_state.edit_target = None

# ==========================================
# 5. SOL MENÜ (İNOVATİF VE RESMİ)
# ==========================================
with st.sidebar:
    st.markdown("<h3 style='color:#0F172A; margin-top:0;'>⚖️ Siber Asistan</h3>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.8rem; color:#3B82F6; font-style:italic;'>Dijital dünyada adaletin rehberi.</p>", unsafe_allow_html=True)
    
    st.markdown("<p style='font-size:0.65rem; color:#94A3B8; font-weight:700; margin-top:20px; margin-bottom:5px;'>PROJE SAHİBİ</p>", unsafe_allow_html=True)
    st.markdown("👤 **Merve [Soyadı]**")
    
    st.divider()
    
    if st.button("➕ Yeni Analiz Başlat", type="primary", use_container_width=True):
        st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.messages = []
        st.session_state.chat_session = model.start_chat(history=[])
        st.rerun()

    st.markdown("<p style='font-size:0.65rem; color:#94A3B8; font-weight:700; margin-top:20px; margin-bottom:10px;'>GEÇMİŞ ANALİZLER</p>", unsafe_allow_html=True)
    
    temp_db = db.copy()
    for cid in sorted(temp_db.keys(), reverse=True):
        with st.container():
            if st.session_state.edit_target == cid:
                new_t = st.text_input("Başlık", value=temp_db[cid][0].get("title", temp_db[cid][0]["content"][:15]), key=f"rename_{cid}", label_visibility="collapsed")
                if st.button("💾", key=f"save_{cid}"):
                    temp_db[cid][0]["title"] = new_t
                    save_db(temp_db)
                    st.session_state.edit_target = None
                    st.rerun()
            else:
                c1, c2, c3 = st.columns([0.76, 0.12, 0.12])
                with c1:
                    title = temp_db[cid][0].get("title", temp_db[cid][0]["content"][:20] + "...")
                    if st.button(f"💬 {title}", key=f"btn_{cid}", use_container_width=True):
                        st.session_state.current_chat_id = cid
                        st.session_state.messages = temp_db[cid]
                        st.rerun()
                with c2:
                    if st.button("✏️", key=f"ed_{cid}"):
                        st.session_state.edit_target = cid
                        st.rerun()
                with c3:
                    if st.button("🗑️", key=f"del_{cid}"):
                        del temp_db[cid]
                        save_db(temp_db)
                        if st.session_state.current_chat_id == cid: st.session_state.messages = []
                        st.rerun()

# ==========================================
# 6. ANA EKRAN
# ==========================================
# MENÜ KAPALIYKEN ÇIKACAK ÖZEL BUTON (SİDEBAR DIŞINDA)
st.markdown('<div class="menu-trigger">☰ Menü</div>', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown('<h2 style="text-align:center; color:#0F172A; margin-top:3rem; font-weight:800;">Siber Hukuk Portalı</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#64748B;">Hukuki vakaları analiz etmek için bir mesaj gönderin.</p>', unsafe_allow_html=True)

for msg in st.session_state.messages:
    av = "👤" if msg["role"] == "user" else "⚖️"
    with st.chat_message(msg["role"], avatar=av):
        st.markdown(msg["content"])

# ==========================================
# 7. SOHBET AKIŞI
# ==========================================
if p := st.chat_input("Mesajınızı buraya yazın..."):
    st.session_state.messages.append({"role": "user", "content": p})
    with st.chat_message("user", avatar="👤"):
        st.markdown(p)

    with st.chat_message("assistant", avatar="⚖️"):
        status = st.empty()
        status.markdown('<p style="color:#94A3B8; font-style:italic; font-size:0.85rem;">⚖️ Mevzuat analiz ediliyor...</p>', unsafe_allow_html=True)
        
        try:
            res = st.session_state.chat_session.send_message(p, stream=True)
            status.empty()
            full_res = ""
            placeholder = st.empty()
            
            for chunk in res:
                full_res += chunk.text
                placeholder.markdown(full_res + "▌")
                time.sleep(0.01)
            
            placeholder.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            db[st.session_state.current_chat_id] = st.session_state.messages
            save_db(db)
        except:
            status.empty()
            st.error("Bir sorun oluştu.")
