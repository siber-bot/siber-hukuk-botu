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
# 3. ÖZEL CSS (SABİT SİDEBAR & RESMİ UI)
# ==========================================
st.markdown("""
<style>
    .stApp, .main { background-color: #FFFFFF !important; }
    header[data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }

    /* SİDEBAR'I ZORLA AÇIK TUTAN MODERN YAPI */
    section[data-testid="stSidebar"] { 
        background-color: #F8FAFC !important; 
        border-right: 1px solid #E2E8F0 !important;
        min-width: 320px !important;
        max-width: 320px !important;
        transform: none !important;
        visibility: visible !important;
        display: block !important;
    }
    
    section[data-testid="stSidebar"] > div:first-child { background-color: transparent !important; }

    /* Butonları Gizle */
    button[data-testid="stSidebarCollapseButton"], [data-testid="collapsedControl"] { display: none !important; }

    .block-container { padding-top: 2.5rem !important; max-width: 850px !important; margin: 0 auto !important; }

    .portal-title { text-align: center; font-weight: 800; font-size: 2.2rem; color: #0F172A; margin-top: 0; pointer-events: none; }

    /* GEÇMİŞ SOHBET LİSTESİ TASARIMI */
    div[data-testid="stVerticalBlock"] div.stButton > button {
        text-align: left !important;
        width: 100% !important;
        border: none !important;
        background: transparent !important; 
        padding: 10px 14px !important;
        border-radius: 10px !important;
        color: #475569 !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stVerticalBlock"] div.stButton > button:hover {
        background-color: #F1F5F9 !important;
        color: #1E293B !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. API VE MODEL (KORUNAN AYAR)
# ==========================================
SISTEM_PROMPTU = "Sen uzman bir Siber Hukuk Asistanısın. Yanıtlarını resmi, madde işaretli ve Türkiye yasalarına dayandırarak ver."

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    
    # KORUNAN AYAR: gemini-3-flash-preview (Doğru İsim Budur)
    model = genai.GenerativeModel('gemini-3-flash-preview') 
except Exception as e:
    st.error(f"Sistem Başlatılamadı: {str(e)}")
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
# 6. SOL MENÜ
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color:#0F172A; margin:0; font-weight:800;'>⚖️ Siber Asistan</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.85rem; color:#3B82F6; font-style:italic; margin-bottom:20px;'>Dijital dünyada adaletin rehberi.</p>", unsafe_allow_html=True)
    
    st.markdown("<p style='font-size:0.7rem; color:#64748B; font-weight:700; margin-bottom:0;'>PROJE SAHİBİ</p>", unsafe_allow_html=True)
    st.markdown("👤 **Merve [Soyadı]**")
    
    st.divider()
    
    if st.button("➕ Yeni Analiz Başlat", type="primary", use_container_width=True):
        st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.messages = []
        st.session_state.chat_session = model.start_chat(history=[])
        st.rerun()

    st.markdown("<p style='font-size:0.7rem; color:#64748B; font-weight:700; margin-top:20px; margin-bottom:10px;'>GEÇMİŞ ANALİZLER</p>", unsafe_allow_html=True)
    
    t_db = db.copy()
    for cid in sorted(t_db.keys(), reverse=True):
        if st.session_state.edit_id == cid:
            new_val = st.text_input("D", value=t_db[cid][0].get("title", t_db[cid][0]["content"][:15]), key=f"r_{cid}", label_visibility="collapsed")
            if st.button("💾", key=f"s_{cid}"):
                t_db[cid][0]["title"] = new_val
                save_db(t_db)
                st.session_state.edit_id = None
                st.rerun()
        else:
            c1, c2, c3 = st.columns([0.7, 0.15, 0.15])
            with c1:
                display_t = t_db[cid][0].get("title", t_db[cid][0]["content"][:18] + "...")
                if st.button(f"💬 {display_t}", key=f"ch_{cid}", use_container_width=True):
                    st.session_state.current_chat_id = cid
                    st.session_state.messages = t_db[cid]
                    st.rerun()
            with c2:
                if st.button("✏️", key=f"e_{cid}"):
                    st.session_state.edit_id = cid
                    st.rerun()
            with c3:
                if st.button("🗑️", key=f"d_{cid}"):
                    del t_db[cid]
                    save_db(t_db)
                    if st.session_state.current_chat_id == cid: st.session_state.messages = []
                    st.rerun()

# ==========================================
# 7. ANA EKRAN
# ==========================================
if not st.session_state.messages:
    st.markdown('<h1 class="portal-title">Siber Hukuk Portalı</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#64748B;">Analiz için vaka detaylarını aşağıya yazın.</p>', unsafe_allow_html=True)

for msg in st.session_state.messages:
    av = "👤" if msg["role"] == "user" else "⚖️"
    with st.chat_message(msg["role"], avatar=av):
        st.markdown(msg["content"])

# ==========================================
# 8. ANALİZ VE SOFT STREAMING
# ==========================================
if prompt := st.chat_input("Hukuki vakayı yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚖️"):
        st.markdown('<p style="color:#94A3B8; font-style:italic; font-size:0.85rem;">⚖️ Analiz ediliyor...</p>', unsafe_allow_html=True)
        try:
            # Sistem promptunu soruya gömüyoruz
            tam_prompt = f"GİZLİ SİSTEM KOMUTU: {SISTEM_PROMPTU}\n\nSORU: {prompt}"
            res = st.session_state.chat_session.send_message(tam_prompt, stream=True)
            
            full_res = ""
            ph = st.empty()
            
            for chunk in res:
                full_res += chunk.text
                ph.markdown(full_res + "▌")
                time.sleep(0.01)
            
            ph.markdown(full_res)
            
            # Başlık atama (ilk mesajsa)
            if len(st.session_state.messages) == 1:
                st.session_state.messages[0]["title"] = prompt[:20]

            st.session_state.messages.append({"role": "assistant", "content": full_res})
            db[st.session_state.current_chat_id] = st.session_state.messages
            save_db(db)
        except Exception as e:
            st.error("Model bağlantısı kurulamadı. Lütfen API kotanızı kontrol edin.")
