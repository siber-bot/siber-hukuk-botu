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

# ==========================================
# 2. VERİTABANI YÖNETİMİ
# ==========================================
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
# 3. ÖZEL CSS (MENÜYÜ ZORLA GÖRÜNÜR YAPAN FİX)
# ==========================================
st.markdown("""
<style>
    /* ANA UYGULAMA TEMA AYARLARI */
    .stApp, .main { background-color: #FFFFFF !important; }
    header[data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }

    /* --- SİHİRLİ DOKUNUŞ: SİDEBAR'I ZORLA AÇIK TUT --- */
    section[data-testid="stSidebar"] { 
        background-color: #F1F5F9 !important; /* Arka plan hafif gri */
        border-right: 1px solid #E2E8F0 !important;
        min-width: 320px !important;
        max-width: 320px !important;
        transform: none !important; /* GİZLENMESİNİ KESİNLİKLE ENGELLER */
        visibility: visible !important; /* GÖRÜNÜRLÜĞÜ ZORUNLU KILAR */
        display: block !important;
    }
    
    /* Streamlit'in içteki beyaz maskesini şeffaf yap */
    section[data-testid="stSidebar"] > div:first-child {
        background-color: transparent !important; 
    }

    /* AÇ/KAPAT BUTONLARINI TAMAMEN SİL */
    button[data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"] { 
        display: none !important; 
    }

    /* ANA İÇERİK HİZALAMASI (Menünün genişliğine göre) */
    .block-container { 
        padding-top: 2.5rem !important; 
        max-width: 850px !important; 
        margin: 0 auto !important; 
    }

    .portal-title {
        text-align: center;
        font-weight: 800;
        font-size: 2.2rem;
        color: #0F172A;
        margin-top: 0;
    }

    /* GEÇMİŞ SOHBET BUTONLARI (Gri zemin üstünde beyaz kartlar) */
    div[data-testid="stVerticalBlock"] div.stButton > button {
        text-align: left !important;
        width: 100% !important;
        border: 1px solid #E2E8F0 !important;
        background: #FFFFFF !important; 
        padding: 10px 14px !important;
        border-radius: 8px !important;
        color: #334155 !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important;
    }
    div[data-testid="stVerticalBlock"] div.stButton > button:hover {
        border-color: #CBD5E1 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        transform: translateY(-1px);
        color: #0F172A !important;
    }
    
    hr {
        margin: 1.5rem 0 !important;
        border-bottom: 1px solid #CBD5E1 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. API VE MODEL
# ==========================================
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-3-flash') 
except:
    st.error("API Secret Hatası! Lütfen Streamlit ayarlarını kontrol edin.")
    st.stop()

# ==========================================
# 5. DATA & SESSION STATE
# ==========================================
db = load_db()

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
if "messages" not in st.session_state:
    st.session_state.messages = db.get(st.session_state.current_chat_id, [])
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

# ==========================================
# 6. SOL MENÜ (KUSURSUZ SABİT SİDEBAR)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color:#0F172A; margin-top:0px; margin-bottom:5px; font-weight:800;'>⚖️ Siber Asistan</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.85rem; color:#3B82F6; font-style:italic; margin-bottom:25px;'>Dijital dünyada adaletin rehberi.</p>", unsafe_allow_html=True)
    
    st.markdown("<p style='font-size:0.75rem; color:#64748B; font-weight:700; margin-bottom:5px; letter-spacing: 0.5px;'>PROJE SAHİBİ</p>", unsafe_allow_html=True)
    st.markdown("👤 **Merve Soyadı**")
    
    st.divider()
    
    if st.button("➕ Yeni Analiz Başlat", type="primary", use_container_width=True):
        st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.messages = []
        st.session_state.chat_session = model.start_chat(history=[])
        st.rerun()

    st.markdown("<p style='font-size:0.75rem; color:#64748B; font-weight:700; margin-top:25px; margin-bottom:15px; letter-spacing: 0.5px;'>GEÇMİŞ ANALİZLER</p>", unsafe_allow_html=True)
    
    t_db = db.copy()
    for cid in sorted(t_db.keys(), reverse=True):
        if st.session_state.edit_id == cid:
            new_val = st.text_input("Düzenle", value=t_db[cid][0].get("title", t_db[cid][0]["content"][:15]), key=f"r_{cid}", label_visibility="collapsed")
            if st.button("💾 Kaydet", key=f"s_{cid}", use_container_width=True):
                t_db[cid][0]["title"] = new_val
                save_db(t_db)
                st.session_state.edit_id = None
                st.rerun()
        else:
            c1, c2, c3 = st.columns([0.65, 0.15, 0.20])
            with c1:
                display_t = t_db[cid][0].get("title", t_db[cid][0]["content"][:18] + "...")
                if st.button(f"💬 {display_t}", key=f"ch_{cid}", use_container_width=True):
                    st.session_state.current_chat_id = cid
                    st.session_state.messages = t_db[cid]
                    st.rerun()
            with c2:
                if st.button("✏️", key=f"e_{cid}", help="Yeniden Adlandır"):
                    st.session_state.edit_id = cid
                    st.rerun()
            with c3:
                if st.button("🗑️", key=f"d_{cid}", help="Sil"):
                    del t_db[cid]
                    save_db(t_db)
                    if st.session_state.current_chat_id == cid: 
                        st.session_state.messages = []
                    st.rerun()

# ==========================================
# 7. ANA EKRAN & MESAJLAŞMA
# ==========================================
if not st.session_state.messages:
    st.markdown('<h1 class="portal-title">Siber Hukuk Portalı</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#64748B; font-size:1.1rem;">Hukuki vakayı veya sormak istediğiniz dijital hakları aşağıya yazın.</p>', unsafe_allow_html=True)

for msg in st.session_state.messages:
    av = "👤" if msg["role"] == "user" else "⚖️"
    with st.chat_message(msg["role"], avatar=av):
        st.markdown(msg["content"])

# ==========================================
# 8. SOHBET GİRDİSİ VE ANALİZ
# ==========================================
if prompt := st.chat_input("Hukuki vakayı yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚖️"):
        try:
            res = st.session_state.chat_session.send_message(prompt, stream=True)
            
            full_res = ""
            message_placeholder = st.empty()
            
            for chunk in res:
                full_res += chunk.text
                message_placeholder.markdown(full_res + "▌")
                time.sleep(0.01)
            
            message_placeholder.markdown(full_res)
            
            if len(st.session_state.messages) == 1:
                st.session_state.messages[0]["title"] = prompt[:25]
                
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            db[st.session_state.current_chat_id] = st.session_state.messages
            save_db(db)
            
        except Exception as e:
            st.error("Model bağlantısında bir hata oluştu.")
