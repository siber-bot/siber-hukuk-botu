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

    .stApp { background-color: #F8FAFC !important; }

    /* ── SIDEBAR ── */
    section[data-testid="stSidebar"] {
        background-color: #FAFAFA !important;
        border-right: 0.5px solid #E5E7EB !important;
    }
    section[data-testid="stSidebar"] [data-testid="stTextInput"] input {
        font-size: 0.8rem !important;
        border-radius: 8px !important;
        border: 0.5px solid #E2E8F0 !important;
        background: #FFFFFF !important;
        padding: 6px 10px !important;
        color: #475569 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stTextInput"] input::placeholder {
        color: #94A3B8 !important;
    }

    /* ── FIX 1: Sadece secondary/default butonları sıfırla, primary HARIÇ ── */
    section[data-testid="stSidebar"] .stButton > button:not([kind="primary"]) {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
    }

    /* Yeni Analiz butonu — PRIMARY, güçlü tanım, sıfırlamadan muaf */
    section[data-testid="stSidebar"] .stButton > button[kind="primary"],
    section[data-testid="stSidebar"] button[kind="primary"] {
        background-color: #534AB7 !important;
        background: #534AB7 !important;
        border: 1px solid #534AB7 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        color: #FFFFFF !important;
        opacity: 1 !important;
        box-shadow: 0 1px 4px rgba(83,74,183,0.25) !important;
    }
    section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover,
    section[data-testid="stSidebar"] button[kind="primary"]:hover {
        background-color: #4339A8 !important;
        background: #4339A8 !important;
        border-color: #4339A8 !important;
        color: #FFFFFF !important;
    }

    /* History item butonları */
    section[data-testid="stSidebar"] .history-btn > button {
        text-align: left !important;
        font-size: 0.8rem !important;
        color: #4B5563 !important;
        border-radius: 8px !important;
        padding: 7px 10px !important;
        width: 100% !important;
        transition: background 0.12s !important;
    }
    section[data-testid="stSidebar"] .history-btn > button:hover {
        background: #F1F5F9 !important;
        color: #1E293B !important;
    }
    section[data-testid="stSidebar"] .history-btn-active > button {
        background: #EEEDFE !important;
        color: #534AB7 !important;
        font-weight: 600 !important;
        border-left: 2px solid #534AB7 !important;
        border-radius: 0 8px 8px 0 !important;
        padding-left: 12px !important;
    }

    /* Icon butonlar */
    section[data-testid="stSidebar"] .icon-btn > button {
        width: 24px !important;
        height: 24px !important;
        min-height: 24px !important;
        padding: 0 !important;
        font-size: 0.65rem !important;
        color: #CBD5E1 !important;
        border-radius: 5px !important;
    }
    section[data-testid="stSidebar"] .icon-btn > button:hover {
        background: #F1F5F9 !important;
        color: #534AB7 !important;
    }

    /* ── MESAJ BALONLARI ── */
    [data-testid="stChatMessage"] {
        padding: 0.5rem 0 !important;
        line-height: 1.65 !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown {
        background-color: #534AB7 !important;
        border: none !important;
        border-radius: 14px 4px 14px 14px !important;
        padding: 12px 18px !important;
        display: inline-block !important;
        max-width: 80% !important;
        margin-left: auto !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown p,
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown li,
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown strong {
        color: #FFFFFF !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown {
        background-color: #FFFFFF !important;
        border: 0.5px solid #E2E8F0 !important;
        border-radius: 4px 14px 14px 14px !important;
        padding: 14px 20px !important;
        color: #1E293B !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown p,
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown li {
        color: #1E293B !important;
    }

    /* Chat input */
    [data-testid="stChatInput"] button {
        background-color: #534AB7 !important;
        color: white !important;
        border-radius: 8px !important;
    }
    [data-testid="stChatInput"] button:hover { background-color: #4339A8 !important; }
    [data-testid="stChatInput"] textarea {
        border-radius: 12px !important;
        border: 0.5px solid #E2E8F0 !important;
        font-size: 0.875rem !important;
    }

    .block-container {
        max-width: 860px !important;
        padding-top: 1rem !important;
        padding-bottom: 0 !important;
    }

    /* Yazıyor animasyonu */
    @keyframes typing-bounce {
        0%, 80%, 100% { opacity: 0.25; transform: translateY(0); }
        40%            { opacity: 1;    transform: translateY(-5px); }
    }
    .typing-dot {
        display: inline-block;
        width: 7px; height: 7px;
        background: #94A3B8;
        border-radius: 50%;
        margin: 0 2px;
        animation: typing-bounce 1.2s ease-in-out infinite;
    }
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }

    /* Aksiyon butonları */
    .action-row .stButton > button {
        background: transparent !important;
        border: 0.5px solid #E2E8F0 !important;
        border-radius: 6px !important;
        font-size: 0.72rem !important;
        color: #94A3B8 !important;
        padding: 2px 8px !important;
        height: 24px !important;
        min-height: 24px !important;
    }
    .action-row .stButton > button:hover {
        background: #F8FAFC !important;
        color: #534AB7 !important;
        border-color: #AFA9EC !important;
    }

    /* ── Portal başlığı ── */
    .portal-title {
        text-align: center;
        font-weight: 700;
        font-size: 2.2rem;
        color: #0F172A;
        letter-spacing: -1px;
        margin-bottom: 0.3rem;
    }

    /* ── Hoşgeldin kartları ── */
    .welcome-card {
        background: #FFFFFF;
        border: 0.5px solid #E2E8F0;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 2px;
        transition: border-color 0.15s, box-shadow 0.15s;
    }
    .welcome-card:hover {
        border-color: #AFA9EC;
        box-shadow: 0 2px 10px rgba(83,74,183,0.08);
    }
    .welcome-card-icon  { font-size: 1.1rem; margin-bottom: 6px; display: block; }
    .welcome-card-title { font-size: 0.85rem; font-weight: 600; color: #1E293B; }
    .welcome-card-desc  { font-size: 0.73rem; color: #64748B; margin-top: 3px; line-height: 1.4; }

    /* Kart butonlarını gizle */
    .card-trigger .stButton > button {
        margin-top: -2px !important;
        opacity: 0 !important;
        height: 2px !important;
        min-height: 2px !important;
        padding: 0 !important;
        border: none !important;
        cursor: pointer !important;
        width: 100% !important;
    }

    /* ── Chip butonları ── */
    .chip-wrap .stButton > button {
        background: #F1F0FD !important;
        color: #534AB7 !important;
        border: 0.5px solid #C4C0F0 !important;
        border-radius: 20px !important;
        font-size: 0.76rem !important;
        font-weight: 500 !important;
        padding: 6px 14px !important;
        white-space: nowrap !important;
        transition: all 0.15s !important;
    }
    .chip-wrap .stButton > button:hover {
        background: #DDD9FC !important;
        border-color: #7F77DD !important;
    }

    /* ── Topbar ── */
    .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 0 14px;
        border-bottom: 0.5px solid #E2E8F0;
        margin-bottom: 6px;
    }
    .topbar-left  { display: flex; align-items: center; gap: 8px; }
    .status-dot   { width: 7px; height: 7px; background: #1D9E75; border-radius: 50%; flex-shrink: 0; }
    .topbar-title { font-size: 0.88rem; font-weight: 500; color: #1E293B; }
    .topbar-right { display: flex; gap: 6px; }
    .topbar-btn {
        display: inline-flex; align-items: center; gap: 4px;
        padding: 4px 10px;
        border: 0.5px solid #E2E8F0;
        border-radius: 7px;
        font-size: 0.73rem;
        color: #64748B;
        background: #FFFFFF;
    }

    /* ── Sidebar etiketler ── */
    .sb-section-label {
        font-size: 0.59rem;
        font-weight: 700;
        color: #C4C9D4;
        text-transform: uppercase;
        letter-spacing: 0.09em;
        padding: 12px 2px 4px;
    }

    /* ── Proje sahibi kartı ── */
    .owner-card {
        margin: 8px 0 14px 0;
        padding: 10px 12px;
        border-radius: 10px;
        background: #F5F4FF;
        border: 0.5px solid #DDD9FC;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .owner-avatar {
        width: 32px; height: 32px;
        border-radius: 50%;
        background: linear-gradient(135deg, #7B73E4 0%, #534AB7 100%);
        color: #fff;
        font-size: 0.72rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        letter-spacing: 0.5px;
    }
    .owner-info { flex: 1; min-width: 0; }
    .owner-name { font-size: 0.81rem; font-weight: 600; color: #2D2A6E; line-height: 1.3; }
    .owner-sub  { font-size: 0.64rem; color: #9491C8; margin-top: 1px; line-height: 1.4; }

    /* ── Disclaimer ── */
    .disclaimer {
        text-align: center;
        font-size: 0.7rem;
        color: #94A3B8;
        padding: 6px 16px 2px;
        border-top: 0.5px solid #F1F5F9;
        margin-top: 6px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. API VE MODEL  ← DOKUNULMUYOR
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


def run_ai(prompt: str):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚖️"):
        placeholder = st.empty()
        placeholder.markdown("""
            <div style='display:flex;align-items:center;gap:8px;
                        color:#94A3B8;font-size:0.85rem;padding:4px 0;'>
                <span>⚖️ &nbsp;Analiz ediliyor</span>
                <span class='typing-dot'></span>
                <span class='typing-dot'></span>
                <span class='typing-dot'></span>
            </div>
        """, unsafe_allow_html=True)

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
            fresh_db = load_db()
            fresh_db[st.session_state.current_chat_id] = st.session_state.messages
            save_db(fresh_db)

        except Exception:
            placeholder.markdown("")
            st.error("Bir hata oluştu. Lütfen API anahtarınızı kontrol edin.")

# ==========================================
# 7. SOL MENÜ (SIDEBAR)
# ==========================================
with st.sidebar:

    # ── FIX 2: Proje sahibi kartı en üstte ──
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
        st.rerun()

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    search_query = st.text_input(
        label="ara", placeholder="🔍  Konuşmalarda ara...",
        label_visibility="collapsed", key="search_input"
    )

    # Geçmiş konuşmalar
    t_db = load_db()
    if search_query:
        t_db = {
            cid: msgs for cid, msgs in t_db.items()
            if any(search_query.lower() in m.get("content", "").lower() for m in msgs)
        }

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
                    key=f"r_{cid}", label_visibility="collapsed"
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
                title = (t_db[cid][0].get("title") or t_db[cid][0]["content"][:22]) if t_db[cid] else "Analiz"
                active_cls = "history-btn-active" if is_active else "history-btn"

                row_c, edit_c, del_c = st.columns([0.76, 0.12, 0.12])
                with row_c:
                    st.markdown(f"<div class='{active_cls}'>", unsafe_allow_html=True)
                    if st.button(title, key=f"ch_{cid}", use_container_width=True):
                        st.session_state.current_chat_id = cid
                        st.session_state.messages = t_db[cid]
                        st.session_state.queued_prompt = ""
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                with edit_c:
                    st.markdown("<div class='icon-btn'>", unsafe_allow_html=True)
                    if st.button("✎", key=f"e_{cid}", help="Yeniden adlandır"):
                        st.session_state.edit_id = cid
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                with del_c:
                    st.markdown("<div class='icon-btn'>", unsafe_allow_html=True)
                    if st.button("🗑", key=f"d_{cid}", help="Sil"):
                        del t_db[cid]
                        save_db(t_db)
                        if cid == st.session_state.current_chat_id:
                            st.session_state.messages = []
                            st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 8. ANA EKRAN
# ==========================================
chat_active = bool(st.session_state.messages) or bool(st.session_state.queued_prompt)

if chat_active:
    if st.session_state.messages:
        current_title = st.session_state.messages[0].get(
            "title", st.session_state.messages[0]["content"][:35] + "…"
        )
    else:
        current_title = st.session_state.queued_prompt[:35] + "…"

    st.markdown(f"""
        <div class='topbar'>
            <div class='topbar-left'>
                <span class='status-dot'></span>
                <span class='topbar-title'>{current_title}</span>
            </div>
            <div class='topbar-right'>
                <span class='topbar-btn'>↓ &nbsp;Dışa Aktar</span>
                <span class='topbar-btn'>↗ &nbsp;Paylaş</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "⚖️"):
            st.markdown(msg["content"])

            if msg["role"] == "assistant":
                st.markdown("<div style='height:3px'></div>", unsafe_allow_html=True)
                st.markdown("<div class='action-row'>", unsafe_allow_html=True)
                ac1, ac2, ac3, ac4, _gap = st.columns([0.13, 0.08, 0.08, 0.13, 0.58])
                with ac1:
                    if st.button("📋 Kopyala", key=f"copy_{i}"):
                        st.toast("Panoya kopyalandı ✓", icon="✅")
                with ac2:
                    liked = i in st.session_state.liked_msgs
                    lbl = "👍✓" if liked else "👍"
                    if st.button(lbl, key=f"like_{i}"):
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

else:
    # ── PORTAL / KARŞILAMA EKRANI ──
    st.markdown('<h1 class="portal-title">⚖️ Siber Hukuk Portalı</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align:center;color:#64748B;margin-bottom:1.5rem;font-size:0.9rem;">'
        'Hukuki vakayı veya dijital haklarınızı yazın.</p>',
        unsafe_allow_html=True
    )

    welcome_items = [
        ("🔒", "KVKK İhlali",         "Kişisel veri ihlali durumunda ne yapmalıyım?"),
        ("💻", "Siber Saldırı",        "Sisteme izinsiz erişimde hukuki adımlar nelerdir?"),
        ("📱", "Sosyal Medya Hukuku",  "İnternette hakaret ve iftira davası nasıl açılır?"),
        ("🏛️", "Şikayet Dilekçesi",   "BTK'ya şikayet dilekçesi nasıl hazırlanır?"),
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
            if st.button(f"▸ {title}", key=f"wcard_{idx}", use_container_width=True):
                st.session_state.queued_prompt = desc
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

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
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

# ==========================================
# 9. SOHBET GİRDİSİ
# ==========================================
if st.session_state.queued_prompt:
    q = st.session_state.queued_prompt
    st.session_state.queued_prompt = ""
    run_ai(q)
    st.rerun()

if prompt := st.chat_input("Hukuki vakayı buraya yazın..."):
    run_ai(prompt)
    st.rerun()

# Disclaimer
st.markdown("""
    <div class='disclaimer'>
        ⚠️ Bu platform hukuki tavsiye niteliği taşımamaktadır.
        Bilgiler yalnızca genel rehberlik amaçlıdır.
        Hukuki süreçler için bir avukana danışmanız önerilir.
    </div>
""", unsafe_allow_html=True)
