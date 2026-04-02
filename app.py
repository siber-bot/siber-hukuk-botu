import streamlit as st
import google.generativeai as genai
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
# 3. ÖZEL CSS
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&display=swap');
    * { font-family: 'DM Sans', sans-serif !important; }

    header[data-testid="stHeader"],
    [data-testid="stToolbar"],
    footer,
    [data-testid="stStatusWidget"],
    [data-testid="stDeployButton"],
    .stAppDeployButton { display: none !important; }

    html, body, [class*="css"], .stApp, [data-testid="stAppViewContainer"] {
        background-color: #F8FAFC !important;
        color: #1E293B !important;
    }

    /* ── SIDEBAR TOGGLE: Gizleme — her zaman görünür ── */
    button[data-testid="baseButton-headerNoPadding"],
    [data-testid="collapsedControl"],
    div[data-testid="stSidebarCollapsedControl"],
    .st-emotion-cache-dvne4q,
    .st-emotion-cache-1gulkj5,
    [class*="collapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
    }
    button[kind="header"] { display: none !important; }

    /* ── SIDEBAR ── */
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] > div {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }

    section[data-testid="stSidebar"] .stButton > button:not([kind="primary"]) {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
    }

    section[data-testid="stSidebar"] .stButton > button[kind="primary"],
    section[data-testid="stSidebar"] button[kind="primary"] {
        background-color: #534AB7 !important;
        border: 1px solid #534AB7 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        color: #FFFFFF !important;
        padding: 10px 16px !important;
    }

    /* ── SIDEBAR SECTION LABELS ── */
    .sb-section-label {
        font-size: 0.6rem !important;
        font-weight: 700 !important;
        color: #94A3B8 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        padding: 14px 4px 5px !important;
        border-top: 1px solid #F1F5F9 !important;
        margin-top: 6px !important;
        display: block !important;
    }

    /* ── HISTORY BUTTONS ── */
    section[data-testid="stSidebar"] .history-btn > button {
        text-align: left !important;
        font-size: 0.82rem !important;
        font-weight: 400 !important;
        color: #374151 !important;
        border-radius: 7px !important;
        padding: 8px 10px !important;
        width: 100% !important;
        line-height: 1.4 !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    section[data-testid="stSidebar"] .history-btn > button:hover {
        background: #F1F5F9 !important;
        color: #1E293B !important;
    }
    section[data-testid="stSidebar"] .history-btn-active > button {
        background: #EEEDFE !important;
        color: #3730A3 !important;
        font-weight: 600 !important;
        border-left: 3px solid #534AB7 !important;
        border-radius: 0 7px 7px 0 !important;
        padding-left: 10px !important;
        border-top: none !important;
        border-right: none !important;
        border-bottom: none !important;
        box-shadow: none !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
    }

    /* ── ICON BUTTONS ── */
    section[data-testid="stSidebar"] .icon-btn > button {
        width: 28px !important;
        height: 28px !important;
        min-height: 28px !important;
        padding: 0 !important;
        font-size: 0.85rem !important;
        color: #64748B !important;
        background: #F1F5F9 !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 6px !important;
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    section[data-testid="stSidebar"] .icon-btn > button:hover {
        background: #E2E8F0 !important;
        color: #1E293B !important;
    }
    section[data-testid="stSidebar"] .delete-btn > button:hover {
        background: #FEE2E2 !important;
        color: #DC2626 !important;
        border-color: #FECACA !important;
    }

    /* ── CHAT MESSAGES ── */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        padding: 0.35rem 0 !important;
        margin-bottom: 6px !important;
    }

    /* Kullanıcı mesajı: SOLDA — hafif indigo arka plan */
    div[data-testid="stMarkdownContainer"]:has(.usr-msg) {
        background-color: #EEF2FF !important;
        color: #1E293B !important;
        border-radius: 4px 16px 16px 16px !important;
        padding: 12px 18px !important;
        display: inline-block !important;
        max-width: 75% !important;
        float: left !important;
        line-height: 1.65 !important;
        border: 1px solid #C7D2FE !important;
        box-shadow: 0 1px 3px rgba(83,74,183,0.08) !important;
    }
    div[data-testid="stMarkdownContainer"]:has(.usr-msg) p,
    div[data-testid="stMarkdownContainer"]:has(.usr-msg) li {
        color: #1E293B !important;
        line-height: 1.65 !important;
        margin-bottom: 0.3em !important;
    }

    /* Asistan mesajı: SAĞDA — beyaz kart */
    div[data-testid="stMarkdownContainer"]:has(.ast-msg) {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 16px 4px 16px 16px !important;
        padding: 16px 22px !important;
        color: #1E293B !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
        max-width: 82% !important;
        float: right !important;
        line-height: 1.75 !important;
    }
    div[data-testid="stMarkdownContainer"]:has(.ast-msg) p {
        color: #1E293B !important;
        line-height: 1.75 !important;
        margin-bottom: 0.75em !important;
    }
    div[data-testid="stMarkdownContainer"]:has(.ast-msg) li {
        color: #334155 !important;
        line-height: 1.75 !important;
        margin-bottom: 0.45em !important;
    }
    div[data-testid="stMarkdownContainer"]:has(.ast-msg) strong {
        color: #0F172A !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMarkdownContainer"]:has(.ast-msg) h1,
    div[data-testid="stMarkdownContainer"]:has(.ast-msg) h2,
    div[data-testid="stMarkdownContainer"]:has(.ast-msg) h3 {
        color: #0F172A !important;
        font-weight: 700 !important;
        margin-top: 1em !important;
        margin-bottom: 0.5em !important;
        border-bottom: 1px solid #F1F5F9 !important;
        padding-bottom: 4px !important;
    }
    div[data-testid="stMarkdownContainer"]:has(.ast-msg) ul,
    div[data-testid="stMarkdownContainer"]:has(.ast-msg) ol {
        padding-left: 1.4em !important;
        margin-bottom: 0.8em !important;
    }
    div[data-testid="stMarkdownContainer"]:has(.ast-msg) ul li::marker {
        color: #534AB7 !important;
    }
    div[data-testid="stMarkdownContainer"]:has(.ast-msg) blockquote {
        border-left: 3px solid #534AB7 !important;
        padding: 8px 12px !important;
        color: #475569 !important;
        margin: 0.8em 0 !important;
        background: #F8FAFC !important;
        border-radius: 0 6px 6px 0 !important;
    }

    /* Float clearfix */
    .msg-clearfix { clear: both; display: block; height: 2px; }

    /* ── CHAT INPUT ── */
    [data-testid="stBottomBlockContainer"],
    [data-testid="stBottom"],
    .stChatFloatingInputContainer {
        background-color: #F8FAFC !important;
        background: #F8FAFC !important;
    }
    div[data-testid="stChatInput"] {
        background-color: #F8FAFC !important;
        padding-bottom: 1rem !important;
        padding-top: 0.75rem !important;
    }
    [data-testid="stChatInput"] textarea {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        border-radius: 12px !important;
        border: 1.5px solid #CBD5E1 !important;
        padding: 12px 16px !important;
        font-size: 0.9rem !important;
        line-height: 1.6 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: #94A3B8 !important;
        font-style: italic !important;
    }
    [data-testid="stChatInput"] textarea:focus {
        border-color: #534AB7 !important;
        box-shadow: 0 0 0 3px rgba(83,74,183,0.12) !important;
        outline: none !important;
    }
    [data-testid="stChatInput"] button {
        background-color: #534AB7 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        box-shadow: 0 2px 6px rgba(83,74,183,0.35) !important;
    }
    [data-testid="stChatInput"] button:hover {
        background-color: #4338CA !important;
    }

    /* ── LAYOUT ── */
    .block-container {
        max-width: 820px !important;
        padding-top: 1.25rem !important;
        padding-bottom: 0 !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* ── ACTION ROW ── */
    .action-row { margin-top: 8px; clear: both; }
    .action-row .stButton > button {
        background: #F8FAFC !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 20px !important;
        font-size: 0.72rem !important;
        color: #475569 !important;
        padding: 4px 12px !important;
        height: 28px !important;
        min-height: 28px !important;
        font-weight: 500 !important;
    }
    .action-row .stButton > button:hover {
        background: #F1F5F9 !important;
        color: #1E293B !important;
    }

    /* ── WELCOME SCREEN ── */
    .portal-title {
        text-align: center;
        font-weight: 700;
        font-size: 2rem;
        color: #0F172A;
        margin-bottom: 0.25rem;
    }
    .portal-subtitle {
        text-align: center;
        color: #475569;
        margin-bottom: 2rem;
        font-size: 0.92rem;
    }
    .welcome-card {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 16px 18px !important;
        margin-bottom: 10px !important;
    }
    .welcome-card-icon  { font-size: 1.2rem; margin-bottom: 8px; display: block; }
    .welcome-card-title { font-size: 0.88rem; font-weight: 600; color: #0F172A; }
    .welcome-card-desc  { font-size: 0.75rem; color: #475569; margin-top: 4px; line-height: 1.5; }

    .card-trigger .stButton > button {
        margin-top: -2px !important; opacity: 0 !important; height: 2px !important;
        min-height: 2px !important; width: 100% !important; border: none !important;
    }

    .chip-wrap .stButton > button {
        background: #FFFFFF !important;
        color: #534AB7 !important;
        border: 1.5px solid #C7D2FE !important;
        border-radius: 20px !important;
        padding: 7px 14px !important;
        font-size: 0.78rem !important;
        font-weight: 500 !important;
    }
    .chip-wrap .stButton > button:hover {
        background: #EEEDFE !important;
        border-color: #534AB7 !important;
    }

    /* ── TOPBAR ── */
    .topbar {
        display: flex; align-items: center;
        padding: 10px 0 14px;
        border-bottom: 1px solid #E2E8F0;
        margin-bottom: 16px;
    }
    .status-dot {
        width: 8px; height: 8px;
        background: #10B981; border-radius: 50%;
        margin-right: 10px; flex-shrink: 0;
        box-shadow: 0 0 0 2px rgba(16,185,129,0.2);
    }
    .topbar-title {
        font-size: 0.9rem; font-weight: 600; color: #1E293B;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }

    /* ── OWNER CARD ── */
    .owner-card {
        margin: 4px 0 16px 0; padding: 12px 14px;
        border-radius: 10px; background: #F8FAFC;
        border: 1px solid #E2E8F0;
        display: flex; align-items: center; gap: 10px;
    }
    .owner-avatar {
        width: 34px; height: 34px; border-radius: 50%;
        background: linear-gradient(135deg, #534AB7 0%, #7C3AED 100%);
        color: #fff; display: flex; align-items: center;
        justify-content: center; font-size: 0.72rem; font-weight: 700; flex-shrink: 0;
    }
    .owner-info { flex: 1; min-width: 0; }
    .owner-name { font-size: 0.83rem; font-weight: 600; color: #1E293B; }
    .owner-sub  { font-size: 0.65rem; color: #64748B; margin-top: 1px; }

    /* ── DISCLAIMER ── */
    .disclaimer {
        text-align: center; font-size: 0.7rem; color: #64748B;
        margin-top: 8px; padding: 0 1rem; line-height: 1.5;
    }

    #scroll-bottom { height: 1px; }

    @media (max-width: 768px) {
        .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
        div[data-testid="stMarkdownContainer"]:has(.usr-msg),
        div[data-testid="stMarkdownContainer"]:has(.ast-msg) { max-width: 94% !important; }
    }

    .typing-dot {
        display: inline-block; width: 6px; height: 6px; background: #94A3B8; border-radius: 50%;
        margin: 0 2px; animation: typing-bounce 1.2s ease-in-out infinite;
    }
    @keyframes typing-bounce {
        0%, 80%, 100% { opacity: 0.25; transform: translateY(0); }
        40% { opacity: 1; transform: translateY(-4px); }
    }
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
# 5. SESSION STATE
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
if "liked_msgs" not in st.session_state:
    st.session_state.liked_msgs = []
if "queued_prompt" not in st.session_state:
    st.session_state.queued_prompt = ""
if "scroll_to_bottom" not in st.session_state:
    st.session_state.scroll_to_bottom = False

# ==========================================
# 6. YARDIMCI FONKSİYONLAR
# ==========================================
def group_chats_by_date(chat_dict):
    today = datetime.now().date()
    groups = {"Bugün": [], "Bu Hafta": [], "Geçen Hafta": [], "Eskiler": []}
    for cid in sorted(chat_dict.keys(), reverse=True):
        try:
            d = datetime.strptime(cid, "%Y%m%d_%H%M%S").date()
            diff = (today - d).days
            if diff == 0:      groups["Bugün"].append(cid)
            elif diff <= 7:    groups["Bu Hafta"].append(cid)
            elif diff <= 14:   groups["Geçen Hafta"].append(cid)
            else:              groups["Eskiler"].append(cid)
        except:
            groups["Eskiler"].append(cid)
    return groups

def scroll_to_bottom():
    st.markdown("""
        <script>
            window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});
            setTimeout(() => window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'}), 300);
        </script>
    """, unsafe_allow_html=True)

# ==========================================
# 7. SOL MENÜ (SIDEBAR)
# ==========================================
with st.sidebar:
    st.markdown("""
        <div class='owner-card'>
            <div class='owner-avatar'>MH</div>
            <div class='owner-info'>
                <div class='owner-name'>Merve Havuz</div>
                <div class='owner-sub'>Siber Hukuk Asistanı · Okul Projesi</div>
            </div>
            <span style='font-size:1.2rem;flex-shrink:0;'>⚖️</span>
        </div>
    """, unsafe_allow_html=True)

    if st.button("＋ Yeni Analiz Başlat", type="primary", use_container_width=True):
        st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.messages = []
        st.session_state.chat_session = model.start_chat(history=[])
        st.session_state.queued_prompt = ""
        st.session_state.scroll_to_bottom = False
        st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    t_db = load_db()
    grouped = group_chats_by_date(t_db)

    for group_name, cids in grouped.items():
        if not cids:
            continue
        st.markdown(f"<div class='sb-section-label'>{group_name}</div>", unsafe_allow_html=True)

        for cid in cids:
            is_active = cid == st.session_state.current_chat_id

            if st.session_state.edit_id == cid:
                new_val = st.text_input(
                    "Düzenle",
                    value=(t_db[cid][0].get("title") or "Analiz") if t_db[cid] else "Analiz",
                    key=f"r_{cid}",
                    label_visibility="collapsed"
                )
                cs, cc = st.columns(2)
                with cs:
                    if st.button("✓ Kaydet", key=f"s_{cid}", use_container_width=True):
                        t_db[cid][0]["title"] = new_val
                        save_db(t_db)
                        st.session_state.edit_id = None
                        st.rerun()
                with cc:
                    if st.button("✕ İptal", key=f"c_{cid}", use_container_width=True):
                        st.session_state.edit_id = None
                        st.rerun()
            else:
                msgs = t_db.get(cid, [])
                title = (msgs[0].get("title") or msgs[0]["content"][:24]) if msgs else "Analiz"
                active_cls = "history-btn-active" if is_active else "history-btn"

                row_c, edit_c, del_c = st.columns([0.70, 0.15, 0.15], gap="small")
                with row_c:
                    st.markdown(f"<div class='{active_cls}'>", unsafe_allow_html=True)
                    if st.button(title, key=f"ch_{cid}", use_container_width=True):
                        st.session_state.current_chat_id = cid
                        st.session_state.messages = t_db[cid]
                        history_for_ai = []
                        for m in t_db[cid]:
                            r = "user" if m["role"] == "user" else "model"
                            history_for_ai.append({"role": r, "parts": [m["content"]]})
                        st.session_state.chat_session = model.start_chat(history=history_for_ai)
                        st.session_state.queued_prompt = ""
                        st.session_state.scroll_to_bottom = False
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                with edit_c:
                    st.markdown("<div class='icon-btn'>", unsafe_allow_html=True)
                    if st.button("✎", key=f"e_{cid}", help="Yeniden adlandır"):
                        st.session_state.edit_id = cid
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                with del_c:
                    st.markdown("<div class='icon-btn delete-btn'>", unsafe_allow_html=True)
                    if st.button("🗑", key=f"d_{cid}", help="Sil"):
                        del t_db[cid]
                        save_db(t_db)
                        if cid == st.session_state.current_chat_id:
                            st.session_state.messages = []
                            st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                            st.session_state.chat_session = model.start_chat(history=[])
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 8. ANA EKRAN & AI YÜRÜTME
# ==========================================
chat_active = bool(st.session_state.messages) or bool(st.session_state.queued_prompt)

if chat_active:
    if st.session_state.messages:
        current_title = st.session_state.messages[0].get("title", st.session_state.messages[0]["content"][:40] + "…")
    else:
        current_title = st.session_state.queued_prompt[:40] + "…"

    st.markdown(f"""
        <div class='topbar'>
            <span class='status-dot'></span>
            <span class='topbar-title'>{current_title}</span>
        </div>
    """, unsafe_allow_html=True)

    # --- Geçmiş Mesajları Çizdir ---
    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown("<div class='usr-msg'></div>" + msg["content"], unsafe_allow_html=True)
                st.markdown("<div class='msg-clearfix'></div>", unsafe_allow_html=True)
        else:
            with st.chat_message("assistant", avatar="⚖️"):
                st.markdown("<div class='ast-msg'></div>" + msg["content"], unsafe_allow_html=True)
                st.markdown("<div class='msg-clearfix'></div>", unsafe_allow_html=True)
                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
                st.markdown("<div class='action-row'>", unsafe_allow_html=True)
                ac1, ac2, ac3, ac4, _gap = st.columns([0.15, 0.09, 0.09, 0.13, 0.54])
                with ac1:
                    if st.button("📋 Kopyala", key=f"copy_{i}"):
                        st.toast("Panoya kopyalandı ✓", icon="✅")
                with ac2:
                    liked = i in st.session_state.liked_msgs
                    if st.button("👍 ✓" if liked else "👍", key=f"like_{i}"):
                        if i not in st.session_state.liked_msgs:
                            st.session_state.liked_msgs.append(i)
                            st.toast("Geri bildirim alındı!", icon="👍")
                with ac3:
                    if st.button("👎", key=f"dislike_{i}"):
                        st.toast("Geri bildirim alındı.", icon="👎")
                with ac4:
                    if st.button("↺ Yenile", key=f"regen_{i}"):
                        st.toast("Yanıt yenileniyor…", icon="↺")
                st.markdown("</div>", unsafe_allow_html=True)

    # --- YENİ PROMPT GELDİYSE AI'I ÇALIŞTIR ---
    if st.session_state.queued_prompt:
        prompt = st.session_state.queued_prompt
        st.session_state.queued_prompt = ""

        with st.chat_message("user", avatar="👤"):
            st.markdown("<div class='usr-msg'></div>" + prompt, unsafe_allow_html=True)
            st.markdown("<div class='msg-clearfix'></div>", unsafe_allow_html=True)

        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant", avatar="⚖️"):
            placeholder = st.empty()
            placeholder.markdown("<div class='ast-msg'></div>" + """
                <div style='display:flex;align-items:center;gap:8px;color:#64748B;font-size:0.85rem;padding:4px 0;'>
                    <span>⚖️ &nbsp;Analiz ediliyor</span>
                    <span class='typing-dot'></span><span class='typing-dot'></span><span class='typing-dot'></span>
                </div>
            """, unsafe_allow_html=True)

            try:
                full_prompt = f"{SISTEM_PROMPTU}\n\nKullanıcı Sorusu: {prompt}"
                response = st.session_state.chat_session.send_message(full_prompt, stream=True)
                full_res = ""
                for chunk in response:
                    full_res += chunk.text
                    placeholder.markdown("<div class='ast-msg'></div>" + full_res + "▌", unsafe_allow_html=True)

                placeholder.markdown("<div class='ast-msg'></div>" + full_res, unsafe_allow_html=True)

                if len(st.session_state.messages) == 1:
                    st.session_state.messages[0]["title"] = prompt[:28]

                st.session_state.messages.append({"role": "assistant", "content": full_res})
                fresh_db = load_db()
                fresh_db[st.session_state.current_chat_id] = st.session_state.messages
                save_db(fresh_db)
                st.session_state.scroll_to_bottom = True

            except Exception as e:
                placeholder.markdown("")
                st.error(f"⚠️ API Hatası Detayı: {e}")
                st.session_state.messages.pop()

        st.rerun()

    st.markdown("<div id='scroll-bottom'></div>", unsafe_allow_html=True)
    if st.session_state.scroll_to_bottom:
        scroll_to_bottom()
        st.session_state.scroll_to_bottom = False

else:
    # --- HOŞ GELDİNİZ EKRANI ---
    st.markdown('<h1 class="portal-title">⚖️ Siber Hukuk Portalı</h1>', unsafe_allow_html=True)
    st.markdown('<p class="portal-subtitle">Hukuki vakayı veya dijital haklarınızı yazın — Türkiye mevzuatına göre analiz edelim.</p>', unsafe_allow_html=True)

    welcome_items = [
        ("🔒", "KVKK İhlali",        "Kişisel veri ihlali durumunda ne yapmalıyım?"),
        ("💻", "Siber Saldırı",       "Sisteme izinsiz erişimde hukuki adımlar nelerdir?"),
        ("📱", "Sosyal Medya Hukuku", "İnternette hakaret ve iftira davası nasıl açılır?"),
        ("🏛️", "Şikayet Dilekçesi",  "BTK'ya şikayet dilekçesi nasıl hazırlanır?"),
    ]

    col_a, col_b = st.columns(2, gap="medium")
    for idx, (icon, title, desc) in enumerate(welcome_items):
        col = col_a if idx % 2 == 0 else col_b
        with col:
            st.markdown(f"""
                <div class='welcome-card'>
                    <span class='welcome-card-icon'>{icon}</span>
                    <div class='welcome-card-title'>{title}</div>
                    <div class='welcome-card-desc'>{desc}</div>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("<div class='card-trigger'>", unsafe_allow_html=True)
            if st.button(f"▸ {title}", key=f"wcard_{idx}"):
                st.session_state.queued_prompt = desc
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    chips = [
        ("📄 Dilekçe oluştur", "Siber suç için resmi dilekçe oluşturmama yardım et."),
        ("⏱ Başvuru süresi?",  "Siber suçlarda başvuru ve dava açma süreleri nedir?"),
        ("💰 Ceza miktarı?",   "Siber suçlarda öngörülen ceza miktarları nedir?"),
        ("🔍 Kanun maddeleri", "Türkiye'de siber suçlarla ilgili kanun maddeleri nelerdir?"),
    ]
    st.markdown("<div class='chip-wrap'>", unsafe_allow_html=True)
    chip_cols = st.columns(len(chips))
    for col, (label, question) in zip(chip_cols, chips):
        with col:
            if st.button(label, key=f"chip_{label}"):
                st.session_state.queued_prompt = question
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ==========================================
# 9. SOHBET GİRDİSİ
# ==========================================
if prompt := st.chat_input("Hukuki vakayı veya sorunuzu buraya yazın…"):
    st.session_state.queued_prompt = prompt
    st.rerun()

st.markdown("""
    <div class='disclaimer'>
        ⚠️ Bu platform hukuki tavsiye niteliği taşımamaktadır. Bilgiler yalnızca genel rehberlik amaçlıdır.
        Hukuki süreçler için bir avukata danışmanız önerilir.
    </div>
""", unsafe_allow_html=True)
