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
# 2. ULTRA ESTETİK MİNİMALİST CSS
# ==========================================
st.markdown("""
<style>
    /* ÜST BAR GİZLEME */
    [data-testid="stHeader"], [data-testid="stToolbar"], .stDeployButton { display: none !important; }
    
    /* ÜST BOŞLUKLARI SIFIRLAMA */
    .block-container { padding-top: 0.5rem !important; max-width: 850px !important; }
    [data-testid="stSidebar"] > div:first-child { padding-top: 0.5rem !important; }

    /* Arkaplan ve Sidebar */
    .stApp { background: #FFFFFF; }
    [data-testid="stSidebar"] { 
        background-color: #F9FAFB !important; 
        border-right: 1px solid #F3F4F6 !important; 
    }
    
    /* Motivasyon Yazısı */
    .motivation-text { 
        font-style: italic; color: #3B82F6; font-size: 0.8rem; 
        margin-bottom: 5px; font-weight: 500; line-height: 1.2; 
    }
    
    /* Sidebar Başlıkları */
    .sidebar-section-title { 
        font-size: 0.65rem; text-transform: uppercase; color: #9CA3AF; 
        font-weight: 700; margin-top: 12px; margin-bottom: 5px; letter-spacing: 0.5px; 
    }

    /* MODERN LİSTE TASARIMI (Kutucuksuz) */
    .stButton > button {
        border: none !important;
        background: transparent !important;
        text-align: left !important;
        font-size: 0.88rem !important;
        color: #374151 !important;
        padding: 8px 10px !important;
        width: 100% !important;
        transition: background 0.2s ease !important;
        border-radius: 8px !important;
    }
    .stButton > button:hover {
        background: #F3F4F6 !important;
    }

    /* Düzenleme ve Silme İkonları İçin Küçük Butonlar */
    .action-btn button {
        padding: 2px 5px !important;
        font-size: 0.75rem !important;
        background: transparent !important;
        border: none !important;
        opacity: 0.5;
    }
    .action-btn button:hover {
        opacity: 1;
        background: #E5E7EB !important;
    }

    /* Mesaj Balonları - Daha Yumuşak */
    [data-testid="stChatMessage"] { padding: 0.5rem 0 !important; }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown {
        background-color: #F3F4F6 !important; border-radius: 20px !important; padding: 10px 15px !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown {
        background-color: #FFFFFF !important; border: 1px solid #F3F4F6 !important; border-radius: 20px !important; 
        padding: 10px 15px !important; box-shadow: 0 2px 10px rgba(0,0,0,0.02) !important;
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
    st.error("Sistem Hatası!")
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
# 5. SOL MENÜ (ULTRA TEMİZ LİSTE)
# ==========================================
with st.sidebar:
    st.markdown("<h3 style='color:#111827; margin:0;'>⚖️ Siber Asistan</h3>", unsafe_allow_html=True)
    st.markdown('<p class="motivation-text">"Dijital dünyada adaletin rehberi."</p>', unsafe_allow_html=True)
    
    st.markdown('<p class="sidebar-section-title">PROJE SAHİBİ</p>', unsafe_allow_html=True)
    st.markdown("👤 **Merve [Soyadı]**", unsafe_allow_html=True)
    
    st.divider()
    
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.messages = []
        st.session_state.chat_session = model.start_chat(history=[])
        st.rerun()

    st.markdown('<p class="sidebar-section-title">GEÇMİŞ</p>', unsafe_allow_html=True)
    
    temp_db = db.copy()
    for chat_id in sorted(temp_db.keys(), reverse=True):
        # Her satır için bir kapsayıcı
        with st.container():
            c1, c2, c3 = st.columns([0.75, 0.12, 0.13])
            
            with c1:
                if st.session_state.edit_mode == chat_id:
                    new_title = st.text_input("Edit", value=temp_db[chat_id][0].get("title", temp_db[chat_id][0]["content"][:15]), key=f"i_{chat_id}", label_visibility="collapsed")
                    if st.button("✔️", key=f"s_{chat_id}"):
                        temp_db[chat_id][0]["title"] = new_title
                        save_db(temp_db)
                        st.session_state.edit_mode = None
                        st.rerun()
                else:
                    title = temp_db[chat_id][0].get("title", temp_db[chat_id][0]["content"][:20] + "...")
                    if st.button(f"💬 {title}", key=f"ch_{chat_id}"):
                        st.session_state.current_chat_id = chat_id
                        st.session_state.messages = temp_db[chat_id]
                        st.rerun()
            
            # İkonlar sadece sade birer sembol olarak sağa yaslı
            with c2:
                st.markdown('<div class="action-btn">', unsafe_allow_html=True)
                if st.button("✏️", key=f"e_{chat_id}"):
                    st.session_state.edit_mode = chat_id
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
                
            with c3:
                st.markdown('<div class="action-btn">', unsafe_allow_html=True)
                if st.button("🗑️", key=f"d_{chat_id}"):
                    del temp_db[chat_id]
                    save_db(temp_db)
                    if st.session_state.current_chat_id == chat_id: st.session_state.messages = []
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 6. ANA EKRAN
# ==========================================
if not st.session_state.messages:
    st.markdown('<h2 style="text-align:center; color:#111827; margin-top:2rem;">Siber Hukuk Analizi</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#6B7280;">Hukuki bir soru sorun veya vakayı anlatın.</p>', unsafe_allow_html=True)

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
        status = st.empty()
        status.markdown('<p style="color:#9CA3AF; font-style:italic; font-size:0.8rem;">⚖️ Analiz ediliyor...</p>', unsafe_allow_html=True)
        
        try:
            response = st.session_state.chat_session.send_message(prompt, stream=True)
            status.empty()
            full_res = ""
            placeholder = st.empty()
            
            for chunk in response:
                full_res += chunk.text
                placeholder.markdown(full_res + "▌")
                time.sleep(0.01)
            
            placeholder.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            db[st.session_state.current_chat_id] = st.session_state.messages
            save_db(db)
            
        except Exception as e:
            status.empty()
            st.error("Bir hata oluştu.")
