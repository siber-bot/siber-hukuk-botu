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
# 3. ÖZEL CSS (JAVASCRIPT OLMADAN KESİN ÇÖZÜM)
# ==========================================
st.markdown("""
<style>
    /* KARANLIK MODU İPTAL ET - ZORUNLU AYDINLIK TEMA */
    .stApp, .main { background-color: #FFFFFF !important; }
    [data-testid="stHeader"] { background: transparent !important; }
    .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #0F172A !important; }

    /* SİDEBAR STİLİ */
    [data-testid="stSidebar"] { 
        background-color: #F8FAFC !important; 
        border-right: 1px solid #E2E8F0 !important;
        z-index: 1000000 !important;
    }

    /* ARAÇ ÇUBUĞUNU GİZLE */
    [data-testid="stToolbar"] { display: none !important; }

    /* -------------------------------------------------------------
       SİHİRLİ DOKUNUŞ: STREAMLIT'İN KENDİ BUTONLARINI ŞEKİLLENDİRME 
       ------------------------------------------------------------- */
       
    /* MENÜ KAPALIYKEN ÇIKAN ORİJİNAL BUTON */
    [data-testid="collapsedControl"] {
        position: fixed !important;
        top: 14px !important;
        left: 14px !important;
        width: 44px !important;
        height: 44px !important;
        background-color: #3B82F6 !important;
        border-radius: 12px !important;
        z-index: 999999 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 14px rgba(59,130,246,0.5) !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="collapsedControl"]:hover { background-color: #2563EB !important; transform: scale(1.08) !important; }
    [data-testid="collapsedControl"] svg { fill: white !important; color: white !important; width: 22px !important; height: 22px !important; }

    /* MENÜ AÇIKKEN ÇIKAN ORİJİNAL BUTON */
    [data-testid="stSidebarCollapseButton"] {
        position: fixed !important;
        top: 14px !important;
        left: 14px !important;
        width: 44px !important;
        height: 44px !important;
        background-color: #3B82F6 !important;
        border-radius: 12px !important;
        z-index: 999999 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 14px rgba(59,130,246,0.5) !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebarCollapseButton"]:hover { background-color: #2563EB !important; transform: scale(1.08) !important; }
    [data-testid="stSidebarCollapseButton"] svg { fill: white !important; color: white !important; width: 22px !important; height: 22px !important; }

    /* ANA KONTEYNER */
    .block-container { 
        padding-top: 4.5rem !important; 
        max-width: 850px !important; 
        margin: 0 auto !important; 
    }

    /* BAŞLIK */
    .portal-title {
        text-align: center;
        font-weight: 800;
        font-size: 2.2rem;
        color: #0F172A;
        margin-top: 1rem;
    }

    /* SOHBET LİSTESİ BUTONLARI */
    div[data-testid="stVerticalBlock"] div.stButton > button {
        text-align: left !important;
        width: 100% !important;
        border: none !important;
        background: transparent !important;
        padding: 8px 12px !important;
        border-radius: 10px !important;
        color: #475569 !important;
        transition: all 0.2s !important;
    }
    div[data-testid="stVerticalBlock"] div.stButton > button:hover {
        background-color: #F1F5F9 !important;
        color: #1E293B !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. API VE MODEL
# ==========================================
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    # Model güncellendi
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
# 6. SOL MENÜ (SİDEBAR) İÇERİĞİ
# ==========================================
with st.sidebar:
    st.markdown("<h3 style='color:#0F172A; margin-top:20px;'>⚖️ Siber Asistan</h3>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.85rem; color:#3B82F6; font-style:italic; margin-bottom:20px;'>Dijital dünyada adaletin rehberi.</p>", unsafe_allow_html=True)
    
    st.markdown("<p style='font-size:0.7rem; color:#94A3B8; font-weight:700; margin-bottom:5px;'>PROJE SAHİBİ</p>", unsafe_allow_html=True)
    st.markdown("👤 **Merve [Soyadı]**")
    
    st.divider()
    
    if st.button("➕ Yeni Analiz Başlat", type="primary", use_container_width=True):
        st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.messages = []
        st.session_state.chat_session = model.start_chat(history=[])
        st.rerun()

    st.markdown("<p style='font-size:0.7rem; color:#94A3B8; font-weight:700; margin-top:20px; margin-bottom:10px;'>GEÇMİŞ ANALİZLER</p>", unsafe_allow_html=True)
    
    t_db = db.copy()
    for cid in sorted(t_db.keys(), reverse=True):
        if st.session_state.edit_id == cid:
            new_val = st.text_input("Düzenle", value=t_db[cid][0].get("title", t_db[cid][0]["content"][:15]), key=f"r_{cid}", label_visibility="collapsed")
            if st.button("💾", key=f"s_{cid}"):
                t_db[cid][0]["title"] = new_val
                save_db(t_db)
                st.session_state.edit_id = None
                st.rerun()
        else:
            c1, c2, c3 = st.columns([0.70, 0.15, 0.15])
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
                    if st.session_state.current_chat_id == cid: 
                        st.session_state.messages = []
                    st.rerun()

# ==========================================
# 7. ANA EKRAN
# ==========================================
if not st.session_state.messages:
    st.markdown('<h1 class="portal-title">Siber Hukuk Portalı</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#64748B;">Hukuki vakayı veya sormak istediğiniz dijital hakları aşağıya yazın.</p>', unsafe_allow_html=True)

for msg in st.session_state.messages:
    av = "👤" if msg["role"] == "user" else "⚖️"
    with st.chat_message(msg["role"], avatar=av):
        st.markdown(msg["content"])

# ==========================================
# 8. SOHBET & ANALİZ SÜRECİ
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
                time.sleep(0.01) # Soft yazma animasyonu (Analiz yazısı kaldırıldı)
            
            message_placeholder.markdown(full_res)
            
            if len(st.session_state.messages) == 1:
                st.session_state.messages[0]["title"] = prompt[:25]
                
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            db[st.session_state.current_chat_id] = st.session_state.messages
            save_db(db)
            
        except Exception as e:
            st.error("Model bağlantısında bir hata oluştu.")
