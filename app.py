import streamlit as st
import google.generativeai as genai
import time
import json
import os
from datetime import datetime, timedelta

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

    /* ── Streamlit gizleme ── */
    header[data-testid="stHeader"],
    [data-testid="stToolbar"],
    footer,
    [data-testid="stStatusWidget"],
    [data-testid="stDeployButton"],
    .stAppDeployButton { display: none !important; }

    /* ── Genel arka plan ── */
    .stApp { background-color: #F8FAFC !important; }

    /* ── SIDEBAR ── */
    section[data-testid="stSidebar"] {
        background-color: #FAFAFA !important;
        border-right: 0.5px solid #E5E7EB !important;
    }

    /* Arama kutusu */
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

    /* Yeni Analiz butonu – mor */
    section[data-testid="stSidebar"] button[kind="primary"] {
        background-color: #534AB7 !important;
        border-color: #534AB7 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
    }
    section[data-testid="stSidebar"] button[kind="primary"]:hover {
        background-color: #4339A8 !important;
        border-color: #4339A8 !important;
    }

    /* Sidebar geçmiş satırları */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
        align-items: center !important;
        background: transparent;
        transition: background 0.15s;
        border-radius: 6px;
        margin-bottom: 2px;
    }
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:hover {
        background: #F1F5F9;
    }

    /* Geçmiş satır metin kesimi */
    [data-testid="stSidebar"] .stButton button p {
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        font-size: 0.82rem !important;
        text-align: left !important;
    }

    /* Düzenle / Sil ikon butonları */
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

    /* ── MESAJ BALONLARI ── */
    [data-testid="stChatMessage"] {
        padding: 0.5rem 0 !important;
        line-height: 1.65 !important;
    }

    /* Kullanıcı balonu – mor zemin, beyaz yazı */
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

    /* Asistan balonu – beyaz zemin, border */
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

    /* Gönder butonu – mor */
    [data-testid="stChatInput"] button {
        background-color: #534AB7 !important;
        color: white !important;
        border-radius: 8px !important;
    }
    [data-testid="stChatInput"] button:hover {
        background-color: #4339A8 !important;
    }

    /* Input textarea */
    [data-testid="stChatInput"] textarea {
        border-radius: 12px !important;
        border: 0.5px solid #E2E8F0 !important;
        font-size: 0.875rem !important;
    }

    /* Ana içerik genişliği */
    .block-container {
        max-width: 860px !important;
        padding-top: 1rem !important;
        padding-bottom: 0 !important;
    }

    /* ── Yazıyor animasyonu ── */
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

    /* ── Aksiyon butonları (kopyala, beğen vb.) ── */
    .action-row button {
        background: transparent !important;
        border: 0.5px solid #E2E8F0 !important;
        border-radius: 6px !important;
        font-size: 0.72rem !important;
        color: #94A3B8 !important;
        padding: 2px 8px !important;
        height: 24px !important;
        min-height: 24px !important;
        line-height: 1 !important;
    }
    .action-row button:hover {
        background: #F8FAFC !important;
        color: #534AB7 !important;
        border-color: #AFA9EC !important;
    }

    /* ── Hızlı öneri chip'leri ── */
    .chip-row button {
        background: #EEEDFE !important;
        color: #534AB7 !important;
        border: 0.5px solid #AFA9EC !important;
        border-radius: 20px !important;
        font-size: 0.78rem !important;
        font-weight: 400 !important;
        padding: 5px 14px !important;
        white-space: nowrap !important;
    }
    .chip-row button:hover {
        background: #DDD9FC !important;
        border-color: #7F77DD !important;
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
        margin-bottom: 8px;
        transition: border-color 0.15s, box-shadow 0.15s;
        cursor: pointer;
    }
    .welcome-card:hover {
        border-color: #AFA9EC;
        box-shadow: 0 2px 10px rgba(83,74,183,0.08);
    }
    .welcome-card-icon { font-size: 1.1rem; margin-bottom: 6px; display: block; }
    .welcome-card-title { font-size: 0.85rem; font-weight: 500; color: #1E293B; }
    .welcome-card-desc  { font-size: 0.75rem; color: #64748B; margin-top: 2px; }

    /* Hoşgeldin kartı buton gizleme (arka plandaki stButton) */
    .welcome-btn-wrap button {
        position: absolute !important;
        opacity: 0 !important;
        width: 100% !important;
        height: 100% !important;
        top: 0 !important;
        left: 0 !important;
        cursor: pointer !important;
    }
    .welcome-btn-wrap {
        position: relative !important;
        margin-bottom: 8px !important;
    }

    /* ── Yasal uyarı ── */
    .disclaimer {
        text-align: center;
        font-size: 0.7rem;
        color: #94A3B8;
        padding: 6px 16px 2px;
        border-top: 0.5px solid #F1F5F9;
        margin-top: 6px;
    }

    /* ── Sidebar etiket stilleri ── */
    .sb-logo  { padding: 8px 4px 0; display: flex; align-items: center; gap: 8px; }
    .sb-label {
        font-size: 0.63rem;
        font-weight: 600;
        color: #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        padding: 10px 4px 4px;
    }

    /* ── Geçmiş konuşma satırları – modernleştirilmiş ── */
    .history-item {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 7px 8px;
        border-radius: 8px;
        margin-bottom: 2px;
        background: transparent;
        transition: background 0.15s;
        cursor: pointer;
    }
    .history-item:hover { background: #F1F5F9; }
    .history-item.active {
        background: #EEEDFE;
        border-left: 2px solid #534AB7;
    }
    .history-icon {
        font-size: 0.75rem;
        color: #CBD5E1;
        flex-shrink: 0;
    }
    .history-text {
        font-size: 0.8rem;
        color: #374151;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        flex: 1;
        min-width: 0;
    }
    .history-item.active .history-text { color: #534AB7; font-weight: 500; }
    .history-actions {
        display: flex;
        gap: 2px;
        opacity: 0;
        transition: opacity 0.15s;
    }
    .history-item:hover .history-actions { opacity: 1; }
    .history-action-btn {
        width: 20px; height: 20px;
        border-radius: 4px;
        border: none;
        background: transparent;
        color: #94A3B8;
        font-size: 0.65rem;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: background 0.1s, color 0.1s;
    }
    .history-action-btn:hover { background: #E2E8F0; color: #534AB7; }

    /* ── Proje sahibi bilgi kartı ── */
    .project-owner-card {
        margin-top: 10px;
        padding: 10px 12px;
        border-top: 0.5px solid #F1F5F9;
    }
    .project-owner-label {
        font-size: 0.58rem;
        font-weight: 600;
        color: #CBD5E1;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        margin-bottom: 5px;
    }
    .project-owner-name {
        font-size: 0.82rem;
        font-weight: 600;
        color: #374151;
        letter-spacing: -0.2px;
    }
    .project-owner-sub {
        font-size: 0.68rem;
        color: #94A3B8;
        margin-top: 1px;
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
    .status-dot   { width: 8px; height: 8px; background: #1D9E75; border-radius: 50%; display: inline-block; flex-shrink: 0; }
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
        cursor: default;
    }
    .topbar-btn:hover { background: #F8FAFC; color: #534AB7; border-color: #AFA9EC; }
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
if "liked_msgs" not in st.session_state:
    st.session_state.liked_msgs = []
# Kart/chip tıklamasından gelen prompt
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# ==========================================
# 6. YARDIMCI FONKSİYONLAR
# ==========================================
def group_chats_by_date(chat_dict):
    """Konuşmaları tarihe göre gruplandır."""
    today = datetime.now().date()
    groups = {"Bugün": [], "Bu Hafta": [], "Geçen Hafta": [], "Daha Önce": []}
    for cid in sorted(chat_dict.keys(), reverse=True):
        try:
            chat_date = datetime.strptime(cid, "%Y%m%d_%H%M%S").date()
            diff = (today - chat_date).days
            if diff == 0:
                groups["Bugün"].append(cid)
            elif diff <= 7:
                groups["Bu Hafta"].append(cid)
            elif diff <= 14:
                groups["Geçen Hafta"].append(cid)
            else:
                groups["Daha Önce"].append(cid)
        except:
            groups["Daha Önce"].append(cid)
    return groups


def send_message(prompt: str):
    """Verilen prompt'u işleyerek AI yanıtını döndürür ve state'i günceller."""
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚖️"):
        placeholder = st.empty()
        placeholder.markdown("""
            <div style='display:flex; align-items:center; gap:8px;
                        color:#94A3B8; font-size:0.85rem; padding:4px 0;'>
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
            db[st.session_state.current_chat_id] = st.session_state.messages
            save_db(db)

        except Exception as e:
            placeholder.markdown("")
            st.error("Bir hata oluştu. Lütfen API anahtarınızı kontrol edin.")

# ==========================================
# 7. SOL MENÜ (SIDEBAR)
# ==========================================
with st.sidebar:

    # Logo + başlık
    st.markdown("""
        <div class='sb-logo'>
            <span style='font-size:1.3rem'>⚖️</span>
            <div>
                <p style='font-size:0.95rem; font-weight:600; margin:0; color:#1E293B;'>Siber Asistan</p>
                <p style='font-size:0.7rem; color:#94A3B8; margin:0; font-style:italic;'>Dijital adaletin rehberi.</p>
            </div>
        </div>
        <div style='height:12px'></div>
    """, unsafe_allow_html=True)

    # Yeni analiz butonu
    if st.button("＋ Yeni Analiz Başlat", type="primary", use_container_width=True):
        st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.messages = []
        st.session_state.chat_session = model.start_chat(history=[])
        st.session_state.pending_prompt = None
        st.rerun()

    # Konuşma arama kutusu
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    search_query = st.text_input(
        label="ara",
        placeholder="🔍  Konuşmalarda ara...",
        label_visibility="collapsed",
        key="search_input"
    )

    # ── Geçmiş konuşmalar – modernleştirilmiş ──
    t_db = db.copy()

    if search_query:
        t_db = {
            cid: msgs for cid, msgs in t_db.items()
            if any(search_query.lower() in msg.get("content", "").lower() for msg in msgs)
        }

    grouped = group_chats_by_date(t_db)

    for group_name, cids in grouped.items():
        if not cids:
            continue
        st.markdown(f"<div class='sb-label'>{group_name}</div>", unsafe_allow_html=True)

        for cid in cids:
            is_active = cid == st.session_state.current_chat_id

            if st.session_state.edit_id == cid:
                # Düzenleme modu
                new_val = st.text_input(
                    "Düzenle",
                    value=t_db[cid][0].get("title", "Analiz"),
                    key=f"r_{cid}",
                    label_visibility="collapsed"
                )
                col_s, col_c = st.columns(2)
                with col_s:
                    if st.button("✓ Kaydet", key=f"s_{cid}", use_container_width=True):
                        t_db[cid][0]["title"] = new_val
                        save_db(t_db)
                        st.session_state.edit_id = None
                        st.rerun()
                with col_c:
                    if st.button("✕ İptal", key=f"c_{cid}", use_container_width=True):
                        st.session_state.edit_id = None
                        st.rerun()
            else:
                title = t_db[cid][0].get("title", t_db[cid][0]["content"][:22]) if t_db[cid] else "Analiz"
                active_class = "active" if is_active else ""

                # Modern history item satırı
                c1, c2, c3 = st.columns([0.76, 0.12, 0.12])
                with c1:
                    # Görsel satır
                    st.markdown(f"""
                        <div class='history-item {active_class}'>
                            <span class='history-icon'>{'◆' if is_active else '◇'}</span>
                            <span class='history-text'>{title}</span>
                        </div>
                    """, unsafe_allow_html=True)
                    # Tıklanabilir şeffaf buton
                    if st.button("‎", key=f"ch_{cid}", use_container_width=True,
                                 help=title):
                        st.session_state.current_chat_id = cid
                        st.session_state.messages = t_db[cid]
                        st.session_state.pending_prompt = None
                        st.rerun()
                with c2:
                    if st.button("✎", key=f"e_{cid}", help="Yeniden adlandır"):
                        st.session_state.edit_id = cid
                        st.rerun()
                with c3:
                    if st.button("🗑", key=f"d_{cid}", help="Sil"):
                        del t_db[cid]
                        save_db(t_db)
                        if cid == st.session_state.current_chat_id:
                            st.session_state.messages = []
                            st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                        st.rerun()

    # ── Proje sahibi bilgi kartı (en alt) ──
    st.markdown("""
        <div class='project-owner-card'>
            <div class='project-owner-label'>Proje Sahibi</div>
            <div class='project-owner-name'>Merve Havuz</div>
            <div class='project-owner-sub'>Siber Hukuk Asistanı · Okul Projesi</div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 8. ANA EKRAN
# ==========================================

# Topbar – aktif konuşma varsa göster
if st.session_state.messages:
    current_title = st.session_state.messages[0].get(
        "title",
        st.session_state.messages[0]["content"][:35] + "…"
    )
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

# ── Boş ekran – hoşgeldin kartları & chip'ler ──
if not st.session_state.messages:
    st.markdown('<h1 class="portal-title">⚖️ Siber Hukuk Portalı</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align:center;color:#64748B;margin-bottom:1.6rem;">'
        'Hukuki vakayı veya dijital haklarınızı yazın.</p>',
        unsafe_allow_html=True
    )

    welcome_items = [
        ("🔒", "KVKK İhlali",          "Kişisel veri ihlali durumunda ne yapmalıyım?"),
        ("💻", "Siber Saldırı",         "Sisteme izinsiz erişimde hukuki adımlar nelerdir?"),
        ("📱", "Sosyal Medya Hukuku",   "İnternette hakaret ve iftira davası nasıl açılır?"),
        ("🏛️", "Şikayet Dilekçesi",     "BTK'ya şikayet dilekçesi nasıl hazırlanır?"),
    ]

    col_a, col_b = st.columns(2)
    for idx, (icon, title, desc) in enumerate(welcome_items):
        with col_a if idx % 2 == 0 else col_b:
            # Kartı HTML ile göster
            st.markdown(f"""
                <div class='welcome-card'>
                    <span class='welcome-card-icon'>{icon}</span>
                    <div class='welcome-card-title'>{title}</div>
                    <div class='welcome-card-desc'>{desc}</div>
                </div>
            """, unsafe_allow_html=True)
            # Kartın altına şeffaf Streamlit butonu (tıklanabilirlik için)
            if st.button(f"{icon} {title}", key=f"wcard_{idx}", use_container_width=True):
                st.session_state.pending_prompt = desc

    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

    # Chip butonları
    st.markdown("<div class='chip-row'>", unsafe_allow_html=True)
    ch1, ch2, ch3, ch4 = st.columns([0.28, 0.25, 0.25, 0.22])
    chips = [
        (ch1, "📄 Dilekçe oluştur",   "Siber suç için dilekçe oluşturmama yardım et."),
        (ch2, "⏱ Başvuru süresi?",    "Siber suçlarda başvuru ve dava açma süreleri nedir?"),
        (ch3, "💰 Ceza miktarı?",      "Siber suçlarda öngörülen ceza miktarları nedir?"),
        (ch4, "🔍 Kanun maddeleri",    "Türkiye'de siber suçlarla ilgili kanun maddeleri nelerdir?"),
    ]
    for col, label, question in chips:
        with col:
            if st.button(label, key=f"chip_{label}"):
                st.session_state.pending_prompt = question
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

# ── Mevcut mesajları göster ──
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
                label = "👍✓" if liked else "👍"
                if st.button(label, key=f"like_{i}"):
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

# ==========================================
# 9. SOHBET GİRDİSİ
# ==========================================

# Kart / chip tıklamasından gelen pending prompt'u işle
if st.session_state.pending_prompt:
    prompt_to_send = st.session_state.pending_prompt
    st.session_state.pending_prompt = None
    send_message(prompt_to_send)
    st.rerun()

# Ana chat input
if prompt := st.chat_input("Hukuki vakayı buraya yazın..."):
    send_message(prompt)
    st.rerun()

# Yasal uyarı
st.markdown("""
    <div class='disclaimer'>
        ⚠️ Bu platform hukuki tavsiye niteliği taşımamaktadır.
        Bilgiler yalnızca genel rehberlik amaçlıdır.
        Hukuki süreçler için bir avukana danışmanız önerilir.
    </div>
""", unsafe_allow_html=True)
