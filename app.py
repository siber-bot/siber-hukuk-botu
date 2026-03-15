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
# 2. ÖZEL CSS: MENÜ BUTONU VE RESMİ TASARIM
# ==========================================
st.markdown("""
<style>
    /* ÜST BARI GİZLE AMA MENÜ BUTONUNU (HAMBURGER) KORU VE ŞIKLAŞTIR */
    header[data-testid="stHeader"] {
        background-color: rgba(255,255,255,0) !important;
    }
    
    /* Streamlit'in kendi menü açma butonunu sol üstte sabit ve şık yap */
    button[data-testid="stSidebarCollapseButton"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        color: #3B82F6 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
        left: 10px !important;
        top: 10px !important;
    }

    /* Gereksiz diğer toolbar öğelerini gizle */
    [data-testid="stToolbar"] { display: none !important; }

    /* ANA KONTEYNER */
    .block-container { padding-top: 3rem !important; max-width: 850px !important; }
    [data-testid="stSidebar"] { 
        background-color: #F8FAFC !important; 
        border-right: 1px solid #E2E8F0 !important;
    }

    /* TIKLANAMAZ DÜZ METİN BAŞLIK (H1/H2) */
    .static-title {
        text-align: center;
        color: #0F172A;
        font-weight: 800;
        pointer-events: none; /* Tıklanmayı engeller */
        user-select: none;    /* Seçilmeyi engeller */
        margin-top: 2rem;
    }

    /* İNOVATİF SOHBET LİSTESİ */
    div[data-testid="stVerticalBlock"] div.stButton > button {
        text-align: left !important;
        width: 100% !important;
        padding: 8px 12px !important;
        color: #475569 !important;
        border-radius: 10px !important;
        border: none !important;
        background: transparent !important;
    }
    div[data-testid="stVerticalBlock"] div.stButton > button:hover {
        background-color: #F1F5F9 !important;
        transform: translateX(4px);
    }

    /* MESAJ BALONLARI */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown {
        background-color: #F1F5F9 !important;
        border-radius: 18px 18px 0 18px !important;
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
    st.error("API Bağlantı Hatası!")
    st.stop()

# ==========================================
# 4. DATA YÖNETİMİ
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
# 5. SOL MENÜ (RESMİ VE ŞIK)
# ==========================================
with st.sidebar:
    st.markdown("<h3 style='color:#0F172A; margin-top:0;'>⚖️ Siber Asistan</h3>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.8rem; color:#3B82F6; font-style:italic;'>Dijital dünyada adaletin rehberi.</p>", unsafe_allow_html=True)
    
    st.divider()
    
    if st.button("➕ Yeni Analiz Başlat", type="primary", use_container_width=True):
        st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.messages = []
        st.session_state.chat_session = model.start_chat(history=[])
        st.rerun()

    st.markdown("<p style='font-size:0.65rem; color:#94A3B8; font-weight:700; margin-top:20px; margin-bottom:10px;'>GEÇMİŞ ANALİZLER</p>", unsafe_allow_html=True)
    
    temp_db = db.copy()
    for cid in sorted(temp_db.keys(), reverse=True):
        if st.session_state.edit_id == cid:
            new_t = st.text_input("Başlık", value=temp_db[cid][0].get("title", temp_db[cid][0]["content"][:15]), key=f"ren_{cid}", label_visibility="collapsed")
            if st.button("💾", key=f"sv_{cid}"):
                temp_db[cid][0]["title"] = new_t
                save_db(temp_db)
                st.session_state.edit_id = None
                st.rerun()
        else:
            c1, c2, c3 = st.columns([0.76, 0.12, 0.12])
            with c1:
                t = temp_db[cid][0].get("title", temp_db[cid][0]["content"][:20] + "...")
                if st.button(f"💬 {t}", key=f"b_{cid}", use_container_width=True):
                    st.session_state.current_chat_id = cid
                    st.session_state.messages = temp_db[cid]
                    st.rerun()
            with c2:
                if st.button("✏️", key=f"e_{cid}"):
                    st.session_state.edit_id = cid
                    st.rerun()
            with c3:
                if st.button("🗑️", key=f"d_{cid}"):
                    del temp_db[cid]
                    save_db(temp_db)
                    if st.session_state.current_chat_id == cid: st.session_state.messages = []
                    st.rerun()

# ==========================================
# 6. ANA EKRAN
# ==========================================
if not st.session_state.messages:
    # Tıklanamaz hale getirilen başlık alanı
    st.markdown('<h1 class="static-title">Siber Hukuk Portalı</h1>', unsafe_allow_html=True)
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
        st.markdown('<p style="color:#94A3B8; font-style:italic; font-size:0.85rem;">⚖️ Analiz ediliyor...</p>', unsafe_allow_html=True)
        try:
            res = st.session_state.chat_session.send_message(p, stream=True)
            st.empty() # "Analiz ediliyor" yazısını temizle
            full_res = ""
            ph = st.empty()
            for chunk in res:
                full_res += chunk.text
                ph.markdown(full_res + "▌")
                time.sleep(0.01)
            ph.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            db[st.session_state.current_chat_id] = st.session_state.messages
            save_db(db)
        except:
            st.error("Bir sorun oluştu.")
