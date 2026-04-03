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
        background-color: #FFFFFF !important;
        color: #1E293B !important;
    }

    /* Hide sidebar toggle buttons */
    button[data-testid="baseButton-headerNoPadding"],
    [data-testid="collapsedControl"],
    button[title*="keyboard"],
    button[aria-label*="keyboard"],
    section[data-testid="stSidebar"] ~ div > button,
    div[data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }
    button[kind="header"] { display: none !important; }
    .st-emotion-cache-dvne4q, .st-emotion-cache-1gulkj5, [class*="collapsedControl"] { display: none !important; }

    /* ── SIDEBAR ── */
    section[data-testid="stSidebar"] {
        width: 260px !important;
        min-width: 260px !important;
        max-width: 260px !important;
    }
    section[data-testid="stSidebar"] > div:first-child {
        width: 260px !important;
        background-color: #FAFAFA !important;
        border-right: 0.5px solid #E5E7EB !important;
        padding-top: 1rem !important;
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
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        color: #FFFFFF !important;
    }

    /* ── GEÇMİŞ İTEMLERİ ── */
    .history-btn > button {
        text-align: left !important;
        font-size: 0.8rem !important;
        color: #4B5563 !important;
        border-radius: 6px !important;
        padding: 6px 10px !important;
        width: 100% !important;
        border: none !important;
        background: transparent !important;
    }
    .history-btn > button:hover {
        background: #F1F5F9 !important;
        color: #1E293B !important;
    }
    .history-btn-active > button {
        background: #EEEDFE !important;
        color: #534AB7 !important;
        font-weight: 600 !important;
        border-left: 3px solid #534AB7 !important;
        border-radius: 6px !important;
        padding-left: 10px !important;
    }

    /* ── MESAJ BALONLARI ── */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        padding: 0.5rem 0 !important;
    }

    div[data-testid="stMarkdownContainer"]:has(.usr-msg) {
        background-color: #534AB7 !important;
        color: #FFFFFF !important;
        border-radius: 14px 14px 14px 4px !important;
        padding: 12px 18px !important;
        display: inline-block !important;
    }
    div[data-testid="stMarkdownContainer"]:has(.usr-msg) p,
    div[data-testid="stMarkdownContainer"]:has(.usr-msg) li {
        color: #FFFFFF !important;
    }

    div[data-testid="stMarkdownContainer"]:has(.ast-msg) {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 4px 14px 14px 14px !important;
        padding: 14px 20px !important;
        color: #1E293B !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02) !important;
    }
    div[data-testid="stMarkdownContainer"]:has(.ast-msg) p,
    div[data-testid="stMarkdownContainer"]:has(.ast-msg) li,
    div[data-testid="stMarkdownContainer"]:has(.ast-msg) strong {
        color: #1E293B !important;
    }

    /* ── INPUT AREA ── */
    [data-testid="stBottomBlockContainer"],
    [data-testid="stBottom"],
    .stChatFloatingInputContainer {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
    }
    div[data-testid="stChatInput"] {
        background-color: #FFFFFF !important;
        padding-bottom: 1rem !important;
    }
    [data-testid="stChatInput"] textarea {
        background-color: #F8FAFC !important;
        color: #1E293B !important;
        border-radius: 12px !important;
        border: 1px solid #E2E8F0 !important;
    }
    [data-testid="stChatInput"] button {
        background-color: #534AB7 !important;
        color: white !important;
    }

    .block-container { max-width: 860px !important; padding-top: 1rem !important; padding-bottom: 0 !important; }

    /* ── WELCOME CARDS (compact) ── */
    .welcome-card {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        padding: 8px 12px !important;
        margin-bottom: 4px !important;
    }
    .welcome-card-icon  { font-size: 1rem; margin-bottom: 2px; display: block; }
    .welcome-card-title { font-size: 0.82rem; font-weight: 600; color: #1E293B; line-height: 1.3; }
    .welcome-card-desc  { font-size: 0.71rem; color: #64748B; margin-top: 2px; line-height: 1.4; overflow: visible; }

    .card-trigger .stButton > button {
        margin-top: -2px !important;
        opacity: 0 !important;
        height: 2px !important;
        min-height: 2px !important;
        width: 100% !important;
        border: none !important;
    }

    .chip-wrap .stButton > button {
        background: #FFFFFF !important;
        color: #534AB7 !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 20px !important;
        padding: 6px 14px !important;
    }

    .portal-title { text-align: center; font-weight: 700; font-size: 2rem; color: #0F172A; margin-bottom: 0.2rem; }

    .topbar { display: flex; align-items: center; padding: 8px 0 14px; border-bottom: 0.5px solid #E2E8F0; margin-bottom: 6px; }
    .status-dot { width: 7px; height: 7px; background: #1D9E75; border-radius: 50%; margin-right: 8px; }
    .topbar-title { font-size: 0.88rem; font-weight: 500; color: #1E293B; }

    .sb-section-label { font-size: 0.59rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; padding: 10px 2px 3px; }

    .disclaimer { text-align: center; font-size: 0.7rem; color: #94A3B8; margin-top: 6px; }
    #scroll-bottom { height: 1px; }

    /* Sidebar header styles */
    .sb-header { padding: 0 4px 12px 4px; }
    .sb-project-label { font-size: 0.65rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px; }
    .sb-bot-name { font-size: 1rem; font-weight: 700; color: #1E293B; margin-bottom: 10px; }
    .sb-owner { font-size: 0.75rem; color: #64748B; margin-bottom: 14px; }
    .sb-owner span { font-weight: 600; color: #1E293B; }
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
        <div class='sb-header'>
            <div class='sb-project-label'>Bilişim Güvenliği Teknolojisi Bitirme Projesi</div>
            <div class='sb-bot-name'>⚖️ Siber Hukuk Botu</div>
            <div class='sb-owner'>Proje Sahibi: <span>Merve Havuz</span></div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("＋ Yeni Analiz Oluştur", type="primary", use_container_width=True):
        st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.messages = []
        st.session_state.chat_session = model.start_chat(history=[])
        st.session_state.queued_prompt = ""
        st.session_state.scroll_to_bottom = False
        st.rerun()

    st.markdown("<hr style='border:none;border-top:0.5px solid #E5E7EB;margin:10px 0;'>", unsafe_allow_html=True)

    t_db = load_db()
    grouped = group_chats_by_date(t_db)

    for group_name, cids in grouped.items():
        if not cids:
            continue
        st.markdown(f"<div class='sb-section-label'>{group_name}</div>", unsafe_allow_html=True)

        for cid in cids:
            is_active = cid == st.session_state.current_chat_id
            title = (t_db[cid][0].get("title") or t_db[cid][0]["content"][:22]) if t_db[cid] else "Analiz"
            active_cls = "history-btn-active" if is_active else "history-btn"

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

# ==========================================
# 8. ANA EKRAN & AI YÜRÜTME
# ==========================================
chat_active = bool(st.session_state.messages) or bool(st.session_state.queued_prompt)

if chat_active:
    if st.session_state.messages:
        current_title = st.session_state.messages[0].get("title", st.session_state.messages[0]["content"][:35] + "…")
    else:
        current_title = st.session_state.queued_prompt[:35] + "…"

    st.markdown(f"""
        <div class='topbar'>
            <span class='status-dot'></span>
            <span class='topbar-title'>{current_title}</span>
        </div>
    """, unsafe_allow_html=True)

    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "⚖️"):
            marker = "<div class='usr-msg'></div>" if msg["role"] == "user" else "<div class='ast-msg'></div>"
            st.markdown(marker + msg["content"], unsafe_allow_html=True)

    if st.session_state.queued_prompt:
        prompt = st.session_state.queued_prompt
        st.session_state.queued_prompt = ""

        with st.chat_message("user", avatar="👤"):
            st.markdown("<div class='usr-msg'></div>" + prompt, unsafe_allow_html=True)

        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant", avatar="⚖️"):
            placeholder = st.empty()
            placeholder.markdown("<div class='ast-msg'></div>" + """
                <div style='color:#94A3B8;font-size:0.85rem;padding:4px 0;'>
                    ⚖️ &nbsp;Analiz ediliyor...
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
                    st.session_state.messages[0]["title"] = prompt[:25]

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
    st.markdown('<h1 class="portal-title">⚖️ Siber Hukuk Portalı</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;color:#64748B;margin-bottom:1rem;font-size:0.88rem;">Hukuki vakayı veya dijital haklarınızı yazın.</p>', unsafe_allow_html=True)

    welcome_items = [
        ("🔒", "KVKK İhlali",        "Kişisel veri ihlali durumunda ne yapmalıyım?"),
        ("💻", "Siber Saldırı",       "Sisteme izinsiz erişimde hukuki adımlar nelerdir?"),
        ("📱", "Sosyal Medya Hukuku", "İnternette hakaret ve iftira davası nasıl açılır?"),
        ("🏛️", "Şikayet Dilekçesi",  "BTK'ya şikayet dilekçesi nasıl hazırlanır?"),
    ]

    col_a, col_b = st.columns(2)
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

    st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

    chips = [
        ("📄 Dilekçe oluştur",  "Siber suç için resmi dilekçe oluşturmama yardım et."),
        ("⏱ Başvuru süresi?",   "Siber suçlarda başvuru ve dava açma süreleri nedir?"),
        ("💰 Ceza miktarı?",    "Siber suçlarda öngörülen ceza miktarları nedir?"),
        ("🔍 Kanun maddeleri",  "Türkiye'de siber suçlarla ilgili kanun maddeleri nelerdir?"),
    ]
    st.markdown("<div class='chip-wrap'>", unsafe_allow_html=True)
    chip_cols = st.columns(len(chips))
    for col, (label, question) in zip(chip_cols, chips):
        with col:
            if st.button(label, key=f"chip_{label}"):
                st.session_state.queued_prompt = question
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

# ==========================================
# 9. SOHBET GİRDİSİ (Alt Çubuk)
# ==========================================
if prompt := st.chat_input("Hukuki vakayı buraya yazın..."):
    st.session_state.queued_prompt = prompt
    st.rerun()

st.markdown("""
    <div class='disclaimer'>
        ⚠️ Bu platform hukuki tavsiye niteliği taşımamaktadır. Bilgiler yalnızca genel rehberlik amaçlıdır. Hukuki süreçler için bir avukana danışmanız önerilir.
    </div>
""", unsafe_allow_html=True)
