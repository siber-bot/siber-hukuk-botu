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
        except:
            return {}
    return {}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ==========================================
# 3. ÖZEL CSS (UI/UX İYİLEŞTİRMELERİ)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&display=swap');
    * { font-family: 'DM Sans', sans-serif !important; }

    /* ── 7. PROTOTİP İZLERİNİ GİZLEME ── */
    header[data-testid="stHeader"], [data-testid="stToolbar"], footer { display: none !important; }
    [data-testid="stStatusWidget"], [data-testid="stDeployButton"], .stAppDeployButton { display: none !important; }

    /* ── GENEL ARKA PLAN ── */
    .stApp { background-color: #F8FAFC !important; }

    /* ── 6. TİPOGRAFİ & MESAJ BALONLARI (Madde 1 & 6) ── */
    [data-testid="stChatMessage"] { 
        padding: 1rem 0 !important; 
        line-height: 1.6 !important; 
    }
    
    /* Kullanıcı Balonu */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 15px 15px 0 15px !important;
        padding: 12px 18px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
    }

    /* Asistan Balonu (Uçuk Mavi) */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown {
        background-color: #F0F7FF !important;
        border: 1px solid #D1E5FF !important;
        border-radius: 15px 15px 15px 0 !important;
        padding: 12px 18px !important;
        color: #1E293B !important;
    }

    /* ── 2. GÖNDER BUTONU ── */
    [data-testid="stChatInput"] button {
        background-color: #0F172A !important;
        color: white !important;
        border-radius: 8px !important;
    }

    /* ── 3, 4, 5. SIDEBAR OPTİMİZASYONU ── */
    section[data-testid="stSidebar"] {
        background-color: #F9FAFB !important;
        border-right: 1px solid #E5E7EB !important;
    }

    /* Boşluk Azaltma (Madde 5) */
    .sb-logo { padding: 10px 5px 0 !important; display: flex; align-items: center; gap: 8px; }
    .sb-tag { font-size: 0.75rem; color: #94A3B8; padding: 0 5px 10px; font-style: italic; }
    .sb-label { font-size: 0.65rem; font-weight: 600; color: #9CA3AF; text-transform: uppercase; padding: 10px 5px 5px; }

    /* Geçmiş Listesi Satırları (Madde 3 & 4) */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
        align-items: center !important;
        background: transparent;
        transition: background 0.2s;
        border-radius: 6px;
        margin-bottom: 2px;
    }
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:hover { background: #F1F5F9; }

    /* Metin Kesme (Ellipsis) */
    [data-testid="stSidebar"] .stButton button p {
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        font-size: 0.85rem !important;
        text-align: left !important;
    }

    /* İkonları Küçültme ve Hizalama */
    [data-testid="stSidebar"] [data-testid="column"] .stButton button {
        height: 26px !important;
        min-height: 26px !important;
        width: 26px !important;
        padding: 0 !important;
        display: grid !important;
        place-items: center !important;
        font-size: 0.7rem !important;
        border: none !important;
        background: transparent !important;
    }

    /* ── ANA İÇERİK ── */
    .block-container { max-width: 850px !important; padding-top: 3rem !important; }
    .portal-title { text-align: center; font-weight: 700; font-size: 2.2rem; color: #0F172A; letter-spacing: -1px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. API VE MODEL
# ==========================================
SISTEM_PROMPTU = "Sen uzman bir Siber Hukuk Asistanısın. Yanıtlarını resmi, madde işaretli ve Türkiye yasalarına dayandırarak ver."

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-3-flash-preview')
except Exception as e:
    st.error("API Hatası! Lütfen Streamlit ayarlarını kontrol edin.")
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
# 6. SOL MENÜ (SIDEBAR)
# ==========================================
with st.sidebar:
    st.markdown("""
        <div class='sb-logo'><span style='font-size:1.2rem'>⚖️</span><p style='font-size:1.1rem; font-weight:600; margin:0;'>Siber Asistan</p></div>
        <p class='sb-tag'>Dijital adaletin rehberi.</p>
        <div class='sb-label'>Proje Sahibi</div>
        <p style='font-size:0.85rem; color:#475569; padding:0 5px;'>👤 Merve Havuz</p>
    """, unsafe_allow_html=True)

    if st.button("＋ Yeni Analiz Başlat", type="primary", use_container_width=True):
        st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.messages = []
        st.session_state.chat_session = model.start_chat(history=[])
        st.rerun()

    st.markdown("<div class='sb-label'>Geçmiş Analizler</div>", unsafe_allow_html=True)

    t_db = db.copy()
    for cid in sorted(t_db.keys(), reverse=True):
        if st.session_state.edit_id == cid:
            new_val = st.text_input("Düzenle", value=t_db[cid][0].get("title", "Analiz"), key=f"r_{cid}", label_visibility="collapsed")
            col_s, col_c = st.columns(2)
            with col_s: 
                if st.button("✓", key=f"s_{cid}", use_container_width=True):
                    t_db[cid][0]["title"] = new_val
                    save_db(t_db); st.session_state.edit_id = None; st.rerun()
            with col_c:
                if st.button("✕", key=f"c_{cid}", use_container_width=True):
                    st.session_state.edit_id = None; st.rerun()
        else:
            c1, c2, c3 = st.columns([0.75, 0.12, 0.13])
            with c1:
                title = t_db[cid][0].get("title", t_db[cid][0]["content"][:20])
                if st.button(title, key=f"ch_{cid}", use_container_width=True):
                    st.session_state.current_chat_id = cid
                    st.session_state.messages = t_db[cid]
                    st.rerun()
            with c2:
                if st.button("✎", key=f"e_{cid}"):
                    st.session_state.edit_id = cid; st.rerun()
            with c3:
                if st.button("🗑️", key=f"d_{cid}"):
                    del t_db[cid]; save_db(t_db); st.rerun()

# ==========================================
# 7. ANA EKRAN
# ==========================================
if not st.session_state.messages:
    st.markdown('<h1 class="portal-title">Siber Hukuk Portalı</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;color:#64748B;">Hukuki vakayı veya dijital haklarınızı yazın.</p>', unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="👤" if msg["role"]=="user" else "⚖️"):
        st.markdown(msg["content"])

# ==========================================
# 8. SOHBET GİRDİSİ
# ==========================================
if prompt := st.chat_input("Hukuki vakayı buraya yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚖️"):
        placeholder = st.empty()
        placeholder.markdown("⚖️ *Analiz ediliyor...*")
        
        try:
            full_prompt = f"{SISTEM_PROMPTU}\n\nKullanıcı Sorusu: {prompt}"
            response = st.session_state.chat_session.send_message(full_prompt, stream=True)
            
            full_res = ""
            for chunk in response:
                full_res += chunk.text
                placeholder.markdown(full_res + "▌")
            
            placeholder.markdown(full_res)

            if len(st.session_state.messages) == 1:
                st.session_state.messages[0]["title"] = prompt[:25]

            st.session_state.messages.append({"role": "assistant", "content": full_res})
            db[st.session_state.current_chat_id] = st.session_state.messages
            save_db(db)

        except Exception as e:
            st.error("Bir hata oluştu. Lütfen API anahtarınızı kontrol edin.")
