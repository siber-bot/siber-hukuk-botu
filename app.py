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
# 2. PREMIUM MİNİMALİST CSS
# ==========================================
st.markdown("""
<style>
    /* ÜST BAR VE GEREKSİZ ARAÇLARI GİZLE */
    [data-testid="stHeader"], [data-testid="stToolbar"], .stDeployButton { display: none !important; }
    
    /* ÜST BOŞLUKLARI TAMAMEN SIFIRLA */
    .block-container { padding-top: 0rem !important; max-width: 850px !important; margin-top: -30px; }
    [data-testid="stSidebar"] > div:first-child { padding-top: 1rem !important; }

    /* Genel Arkaplan ve Font */
    .stApp { background: #FFFFFF; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { 
        background-color: #F9FAFB !important; 
        border-right: 1px solid #F3F4F6 !important; 
        width: 300px !important;
    }
    
    /* Sidebar Başlık ve Motivasyon */
    .sidebar-brand { font-size: 1.1rem; font-weight: 700; color: #111827; margin-bottom: 2px; }
    .motivation-text { font-style: italic; color: #3B82F6; font-size: 0.8rem; margin-bottom: 15px; line-height: 1.3; }
    .sidebar-section-title { font-size: 0.65rem; text-transform: uppercase; color: #9CA3AF; font-weight: 700; margin-top: 20px; margin-bottom: 8px; letter-spacing: 0.8px; }

    /* YENİ SOHBET BUTONU (Premium Stil) */
    .stButton > button[kind="secondary"] {
        background: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 10px !important;
        color: #374151 !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
    }
    .stButton > button[kind="secondary"]:hover {
        border-color: #3B82F6 !important;
        background: #F0F7FF !important;
        color: #3B82F6 !important;
    }

    /* SOHBET SATIRI TASARIMI */
    div[data-testid="stVerticalBlock"] > div:has(div.chat-row-container) { padding: 0 !important; }
    
    .chat-entry-btn button {
        border: none !important;
        background: transparent !important;
        text-align: left !important;
        color: #4B5563 !important;
        font-size: 0.85rem !important;
        padding: 10px 12px !important;
        width: 100% !important;
        border-radius: 8px !important;
        transition: background 0.2s !important;
    }
    .chat-entry-btn button:hover {
        background: #F3F4F6 !important;
        color: #111827 !important;
    }

    /* Aksiyon Butonları (Düzenle/Sil) için şık görünüm */
    .action-button button {
        background: transparent !important;
        border: none !important;
        font-size: 0.8rem !important;
        padding: 5px !important;
        opacity: 0.4;
        transition: opacity 0.2s !important;
    }
    .action-button button:hover {
        opacity: 1 !important;
        background: #E5E7EB !important;
        border-radius: 4px !important;
    }

    /* Mesaj Balonları */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown {
        background-color: #F3F4F6 !important; border-radius: 18px !important; padding: 12px 16px !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown {
        background-color: #FFFFFF !important; border: 1px solid #F3F4F6 !important; border-radius: 18px !important; padding: 12px 16px !important; box-shadow: 0 4px 12px rgba(0,0,0,0.02) !important;
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
# 5. SOL MENÜ (SIDEBAR)
# ==========================================
with st.sidebar:
    st.markdown('<div class="sidebar-brand">⚖️ Siber Asistan</div>', unsafe_allow_html=True)
    st.markdown('<div class="motivation-text">"Dijital dünyada adaletin rehberi."</div>', unsafe_allow_html=True)
    
    st.markdown('<p class="sidebar-section-title">PROJE SAHİBİ</p>', unsafe_allow_html=True)
    st.markdown("👤 **Merve [Soyadı]**", unsafe_allow_html=True)
    
    st.divider()
    
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.messages = []
        st.session_state.chat_session = model.start_chat(history=[])
        st.session_state.edit_id = None
        st.rerun()

    st.markdown('<p class="sidebar-section-title">GEÇMİŞ SOHBETLER</p>', unsafe_allow_html=True)
    
    temp_db = db.copy()
    for cid in sorted(temp_db.keys(), reverse=True):
        # Satır Konteyneri
        with st.container():
            # Başlık Edit Modu Kontrolü
            if st.session_state.edit_id == cid:
                new_title = st.text_input("Edit Title", value=temp_db[cid][0].get("title", temp_db[cid][0]["content"][:15]), key=f"inp_{cid}", label_visibility="collapsed")
                if st.button("✔️", key=f"ok_{cid}"):
                    temp_db[cid][0]["title"] = new_title
                    save_db(temp_db)
                    st.session_state.edit_id = None
                    st.rerun()
            else:
                # Normal Satır Görünümü
                c1, c2, c3 = st.columns([0.76, 0.12, 0.12])
                with c1:
                    t = temp_db[cid][0].get("title", temp_db[cid][0]["content"][:20] + "...")
                    st.markdown('<div class="chat-entry-btn">', unsafe_allow_html=True)
                    if st.button(f"💬 {t}", key=f"sel_{cid}"):
                        st.session_state.current_chat_id = cid
                        st.session_state.messages = temp_db[cid]
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                with c2:
                    st.markdown('<div class="action-button">', unsafe_allow_html=True)
                    if st.button("✏️", key=f"ed_{cid}"):
                        st.session_state.edit_id = cid
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                with c3:
                    st.markdown('<div class="action-button">', unsafe_allow_html=True)
                    if st.button("🗑️", key=f"dl_{cid}"):
                        del temp_db[cid]
                        save_db(temp_db)
                        if st.session_state.current_chat_id == cid: st.session_state.messages = []
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 6. ANA EKRAN
# ==========================================
if not st.session_state.messages:
    st.markdown('<h2 style="text-align:center; color:#111827; margin-top:3rem; font-weight:800; letter-spacing:-0.03em;">Siber Hukuk Analizi</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#6B7280; font-size:1.1rem;">Bilişim suçları ve mevzuat danışma merkezi.</p>', unsafe_allow_html=True)

for msg in st.session_state.messages:
    av = "👤" if msg["role"] == "user" else "⚖️"
    with st.chat_message(msg["role"], avatar=av):
        st.markdown(msg["content"])

# ==========================================
# 7. SOHBET & SOFT YAZMA
# ==========================================
if p := st.chat_input("Hukuki vakayı anlatın..."):
    st.session_state.messages.append({"role": "user", "content": p})
    with st.chat_message("user", avatar="👤"):
        st.markdown(p)

    with st.chat_message("assistant", avatar="⚖️"):
        ld = st.empty()
        ld.markdown('<p style="color:#9CA3AF; font-size:0.85rem; font-style:italic;">⚖️ Mevzuat taranıyor...</p>', unsafe_allow_html=True)
        
        try:
            res = st.session_state.chat_session.send_message(p, stream=True)
            ld.empty()
            full = ""
            ph = st.empty()
            
            for chunk in res:
                full += chunk.text
                ph.markdown(full + "▌")
                time.sleep(0.01)
            
            ph.markdown(full)
            st.session_state.messages.append({"role": "assistant", "content": full})
            db[st.session_state.current_chat_id] = st.session_state.messages
            save_db(db)
            
        except:
            ld.empty()
            st.error("Bir hata oluştu.")
