import streamlit as st
import google.generativeai as genai
import time
import json
import os
from datetime import datetime

# ==========================================
# 1. SAYFA AYARLARI (ZORUNLU ÜSTTE)
# ==========================================
st.set_page_config(
    page_title="Siber Hukuk Asistanı",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"   # expanded kalabilir, buton her durumda görünecek
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
# 3. ÖZEL CSS + FLOATING MENU BUTTON
# ==========================================
st.markdown("""
<style>
    /* ── TOOLBAR (sağ üst menü) gizle ── */
    [data-testid="stToolbar"] { display: none !important; }

    /* ── Streamlit'in kendi sidebar butonunu gizle (biz kendi butonumuzu enjekte edeceğiz) ── */
    button[data-testid="stSidebarCollapseButton"],
    button[data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }

    /* ── CUSTOM FLOATING TOGGLE BUTTON ── */
    #custom-menu-btn {
        position:         fixed;
        top:              14px;
        left:             14px;
        z-index:          999999;
        width:            44px;
        height:           44px;
        background:       #3B82F6;
        border:           none;
        border-radius:    12px;
        cursor:           pointer;
        display:          flex;
        align-items:      center;
        justify-content:  center;
        box-shadow:       0 4px 14px rgba(59,130,246,0.5);
        transition:       background 0.2s, transform 0.2s;
    }
    #custom-menu-btn:hover {
        background:  #2563EB;
        transform:   scale(1.08);
    }
    #custom-menu-btn svg {
        width:  22px;
        height: 22px;
        fill:   white;
    }

    /* ── HEADER şeffaf ── */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* ── ANA KONTEYNER ── */
    .block-container { 
        padding-top: 2rem !important; 
        max-width: 850px !important; 
        margin: 0 auto !important; 
    }

    /* ── SİDEBAR ── */
    [data-testid="stSidebar"] { 
        background-color: #F8FAFC !important; 
        border-right: 1px solid #E2E8F0 !important;
    }

    /* ── BAŞLIK ── */
    .portal-title {
        text-align: center;
        font-weight: 800;
        font-size: 2.2rem;
        color: #0F172A;
        pointer-events: none;
        margin-top: 1rem;
    }

    /* ── SOHBET LİSTESİ BUTONLARI ── */
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

<!-- FLOATING HAMBURGER BUTTON -->
<button id="custom-menu-btn" title="Menüyü Aç/Kapat">
    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <rect y="4"  width="24" height="2.5" rx="1.5"/>
        <rect y="11" width="24" height="2.5" rx="1.5"/>
        <rect y="18" width="24" height="2.5" rx="1.5"/>
    </svg>
</button>

<script>
(function() {
    function toggleSidebar() {
        // Streamlit'in sidebar'ını bulmak için birden fazla yol dene
        const selectors = [
            'button[data-testid="stSidebarCollapseButton"]',
            'button[data-testid="collapsedControl"]',
            '[data-testid="stSidebarCollapsedControl"] button'
        ];
        for (const sel of selectors) {
            const btn = window.parent.document.querySelector(sel);
            if (btn) { btn.click(); return; }
        }
        // Buton bulunamazsa sidebar section'ına class toggle yap
        const sidebar = window.parent.document.querySelector('[data-testid="stSidebar"]');
        if (sidebar) {
            const isHidden = sidebar.style.marginLeft === '0px' || sidebar.style.marginLeft === '';
            sidebar.style.transition = 'margin-left 0.3s ease';
            sidebar.style.marginLeft = isHidden ? '-350px' : '0px';
        }
    }

    // Buton DOM'a eklendikten sonra event'i bağla
    function attachBtn() {
        const btn = document.getElementById('custom-menu-btn');
        if (btn) {
            btn.addEventListener('click', toggleSidebar);
        } else {
            setTimeout(attachBtn, 200);
        }
    }
    attachBtn();
})();
</script>
""", unsafe_allow_html=True)

# ==========================================
# 4. API VE MODEL
# ==========================================
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-3-flash-preview') 
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
# 6. SOL MENÜ
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
    
    t_db = db.copy()
    for cid in sorted(t_db.keys(), reverse=True):
        if st.session_state.edit_id == cid:
            new_val = st.text_input("Edit", value=t_db[cid][0].get("title", t_db[cid][0]["content"][:15]), key=f"r_{cid}", label_visibility="collapsed")
            if st.button("💾", key=f"s_{cid}"):
                t_db[cid][0]["title"] = new_val
                save_db(t_db)
                st.session_state.edit_id = None
                st.rerun()
        else:
            c1, c2, c3 = st.columns([0.76, 0.12, 0.12])
            with c1:
                display_t = t_db[cid][0].get("title", t_db[cid][0]["content"][:20] + "...")
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
    st.markdown('<p style="text-align:center; color:#64748B;">Analiz için detayları aşağıya yazın.</p>', unsafe_allow_html=True)

for msg in st.session_state.messages:
    av = "👤" if msg["role"] == "user" else "⚖️"
    with st.chat_message(msg["role"], avatar=av):
        st.markdown(msg["content"])

# ==========================================
# 8. SOHBET & STREAMING
# ==========================================
if prompt := st.chat_input("Hukuki vakayı yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚖️"):
        status_msg = st.empty()
        status_msg.markdown('<p style="color:#94A3B8; font-style:italic; font-size:0.85rem;">⚖️ Analiz ediliyor...</p>', unsafe_allow_html=True)
        
        try:
            res = st.session_state.chat_session.send_message(prompt, stream=True)
            status_msg.empty()
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
        except Exception as e:
            st.error("Bir hata oluştu. Lütfen tekrar deneyin.")
