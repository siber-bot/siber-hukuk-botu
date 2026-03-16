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
# 3. ÖZEL CSS
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&display=swap');
    * { font-family: 'DM Sans', sans-serif !important; }

    /* ── GENEL ── */
    .stApp, .main { background-color: #F8FAFC !important; }
    header[data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"]      { display: none !important; }
    #MainMenu                      { display: none !important; }
    footer                         { display: none !important; }

    /* ── Streamlit "Manage app" ve tüm sağ alt badge varyantlarını gizle ── */
    [data-testid="stDeployButton"]  { display: none !important; }
    [data-testid="stStatusWidget"]  { display: none !important; }
    [class*="viewerBadge"]          { display: none !important; }
    [class*="StatusWidget"]         { display: none !important; }
    ._container_51w34_1             { display: none !important; }
    .st-emotion-cache-zq5wmm        { display: none !important; }

    /* ── SİDEBAR ── */
    section[data-testid="stSidebar"] {
        background-color: #F9FAFB !important;
        border-right: 1px solid #E5E7EB !important;
        min-width: 290px !important;
        max-width: 290px !important;
        transform: none !important;
        visibility: visible !important;
        display: block !important;
    }
    section[data-testid="stSidebar"] > div:first-child {
        background-color: transparent !important;
        padding: 0 10px !important;
    }
    button[data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"] { display: none !important; }

    /* ── ANA İÇERİK ── */
    .block-container {
        padding-top: 2.5rem !important;
        max-width: 820px !important;
        margin: 0 auto !important;
    }
    .portal-title {
        text-align: center;
        font-weight: 700;
        font-size: 2rem;
        color: #0F172A;
        margin-top: 0;
        pointer-events: none;
        letter-spacing: -0.5px;
    }

    /* ══════════════════════════════════
       YENİ ANALİZ BAŞLAT BUTONU
    ══════════════════════════════════ */
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: #0F172A !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1rem !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        transition: background 0.18s ease, box-shadow 0.18s ease !important;
        width: 100% !important;
        box-shadow: 0 1px 4px rgba(15,23,42,0.16) !important;
        text-align: center !important;
        letter-spacing: 0.1px !important;
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background: #1E293B !important;
        box-shadow: 0 4px 14px rgba(15,23,42,0.22) !important;
        transform: none !important;
    }

    /* ══════════════════════════════════════════════════
       GEÇMİŞ SATIRLARI — tam sıfırlanmış, modern pill
    ══════════════════════════════════════════════════ */

    /* Satır kapsayıcı — hafif hover zeminli */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
        position: relative !important;
        border-radius: 8px !important;
        padding: 0 2px !important;
        margin-bottom: 1px !important;
        gap: 2px !important;
        align-items: center !important;
        transition: background 0.15s ease !important;
    }
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:hover {
        background: #EAEFF6 !important;
    }

    /* Tüm sütunların padding'ini sıfırla */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]
        > [data-testid="column"] {
        padding: 0 !important;
        min-width: 0 !important;
    }

    /* Streamlit'in stButton sarmalayıcısındaki boşlukları sıfırla */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]
        > [data-testid="column"] > div,
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]
        > [data-testid="column"] [data-testid="stButton"] {
        width: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* ── Ana isim butonu ── */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]
        > [data-testid="column"]:nth-child(1) .stButton > button {
        text-align: left !important;
        padding: 8px 6px 8px 10px !important;
        color: #4B5563 !important;
        font-size: 0.855rem !important;
        font-weight: 400 !important;
        border-radius: 8px !important;
        border: none !important;
        background: transparent !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        box-shadow: none !important;
        width: 100% !important;
        min-height: 0 !important;
        height: 36px !important;
        line-height: 1.4 !important;
        transition: color 0.15s !important;
        display: flex !important;
        align-items: center !important;
    }
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:hover
        > [data-testid="column"]:nth-child(1) .stButton > button {
        color: #111827 !important;
    }

    /* ── İkon kolonları: 34px sabit ── */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]
        > [data-testid="column"]:nth-child(2),
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]
        > [data-testid="column"]:nth-child(3) {
        flex: 0 0 34px !important;
        max-width: 34px !important;
        min-width: 34px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]
        > [data-testid="column"]:nth-child(2) [data-testid="stButton"],
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]
        > [data-testid="column"]:nth-child(3) [data-testid="stButton"] {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 34px !important;
    }

    /* ── İkon butonları: 34×34, tam ortalı ── */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]
        > [data-testid="column"]:nth-child(2) .stButton > button,
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]
        > [data-testid="column"]:nth-child(3) .stButton > button {
        opacity: 0 !important;
        pointer-events: none !important;
        background: #F1F5F9 !important;
        border: none !important;
        border-radius: 7px !important;
        padding: 0 !important;
        margin: 0 auto !important;
        font-size: 0.85rem !important;
        color: #9CA3AF !important;
        box-shadow: none !important;
        width: 34px !important;
        height: 34px !important;
        min-height: 0 !important;
        max-height: 34px !important;
        min-width: 0 !important;
        line-height: 34px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition:
            opacity 0.15s ease,
            background 0.12s ease,
            color 0.12s ease !important;
    }

    /* İkon butonları görünür ol */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:hover
        > [data-testid="column"]:nth-child(2) .stButton > button,
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:hover
        > [data-testid="column"]:nth-child(3) .stButton > button {
        opacity: 1 !important;
        pointer-events: auto !important;
    }

    /* Kalem: hover'da mavi pill */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:hover
        > [data-testid="column"]:nth-child(2) .stButton > button:hover {
        background: #E0EAFF !important;
        color: #3B5BDB !important;
        border-radius: 6px !important;
    }

    /* Çöp: hover'da kırmızı pill */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:hover
        > [data-testid="column"]:nth-child(3) .stButton > button:hover {
        background: #FFE4E4 !important;
        color: #C92A2A !important;
        border-radius: 6px !important;
    }

    /* İkon buton içindeki TÜM sarmalayıcıları sıfırla (div, p, span) */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]
        > [data-testid="column"]:nth-child(2) .stButton > button *,
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]
        > [data-testid="column"]:nth-child(3) .stButton > button * {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0 !important;
        margin: 0 !important;
        line-height: 1 !important;
        width: 100% !important;
        height: 100% !important;
        font-size: 0.85rem !important;
    }

    /* ── KEYBOARD HINT GİZLE (sadece baloncuk, buton değil) ── */
    /* Streamlit'in sağ üst köşedeki küçük klavye ipucu etiketi */
    [data-testid="stTooltipContent"]               { display: none !important; }
    [data-baseweb="tooltip"]                       { display: none !important; }
    [role="tooltip"]                               { display: none !important; }
    kbd                                            { display: none !important; }

    /* ── DÜZENLEME MODU ── */
    [data-testid="stSidebar"] .stTextInput input {
        background: #FFFFFF !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 8px !important;
        color: #1E293B !important;
        font-size: 0.875rem !important;
        padding: 7px 10px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    }
    [data-testid="stSidebar"] .stTextInput input:focus {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
    }

    /* Kaydet / İptal */
    [data-testid="stSidebar"] .stButton > button[kind="secondary"] {
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        border-radius: 8px !important;
        padding: 6px 10px !important;
        border: 1.5px solid #E2E8F0 !important;
        background: #FFFFFF !important;
        color: #374151 !important;
        box-shadow: none !important;
        transition: all 0.15s !important;
    }
    [data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
        background: #F1F5F9 !important;
        border-color: #CBD5E1 !important;
    }

    /* ══════════════════════════════════
       MESAJ BALONLARI
    ══════════════════════════════════ */
    [data-testid="stChatMessage"] { padding: 0.4rem 0 !important; }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown {
        background: #F1F5F9 !important;
        border-radius: 16px !important;
        padding: 10px 16px !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown {
        background: #FFFFFF !important;
        border: 1px solid #E9EEF5 !important;
        border-radius: 16px !important;
        padding: 10px 16px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04) !important;
    }

    /* ══════════════════════════════════
       SIDEBAR HTML PARÇALARI
    ══════════════════════════════════ */
    .sb-logo  { padding: 20px 2px 4px; display:flex; align-items:center; gap:9px; }
    .sb-title { font-size:1rem; font-weight:600; color:#0F172A; margin:0; }
    .sb-tag   { font-size:0.75rem; color:#94A3B8; padding:2px 2px 16px; font-style:italic; }
    .sb-label {
        font-size:0.68rem; font-weight:600; color:#9CA3AF;
        letter-spacing:0.08em; text-transform:uppercase;
        padding: 16px 2px 7px;
    }
    .sb-divider { border:none; border-top:1px solid #E5E7EB; margin:6px 0 12px; }
</style>

<!-- Manage app'i JS ile tamamen yok et -->
<script>
(function() {
    function killManageApp() {
        var selectors = [
            '[data-testid="stStatusWidget"]',
            '[data-testid="stDeployButton"]',
            '[class*="viewerBadge"]',
            '[class*="StatusWidget"]',
            '[class*="stStatusWidget"]',
            '.st-emotion-cache-zq5wmm',
            '._container_51w34_1',
        ];
        selectors.forEach(function(sel) {
            document.querySelectorAll(sel).forEach(function(el) {
                el.style.setProperty('display','none','important');
                el.style.setProperty('visibility','hidden','important');
                el.style.setProperty('opacity','0','important');
                el.style.setProperty('pointer-events','none','important');
            });
        });
        document.querySelectorAll('a, button, span, div').forEach(function(el) {
            if (el.children.length === 0 && el.textContent.trim() === 'Manage app') {
                var p = el;
                for (var i = 0; i < 8; i++) {
                    p.style.setProperty('display','none','important');
                    if (p.parentElement) p = p.parentElement; else break;
                }
            }
        });
    }
    killManageApp();
    new MutationObserver(killManageApp).observe(document.body, { childList: true, subtree: true });
})();
</script>
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
# 6. SOL MENÜ
# ==========================================
with st.sidebar:
    st.markdown("""
        <div class='sb-logo'>
            <span style='font-size:1.25rem'>⚖️</span>
            <p class='sb-title'>Siber Asistan</p>
        </div>
        <p class='sb-tag'>Dijital dünyada adaletin rehberi.</p>
        <div class='sb-label'>Proje Sahibi</div>
        <p style='font-size:0.85rem;color:#374151;padding:0 2px 8px;font-weight:500;'>
            👤 Merve [Soyadı]
        </p>
        <hr class='sb-divider'/>
    """, unsafe_allow_html=True)

    if st.button("＋  Yeni Analiz Başlat", type="primary", use_container_width=True):
        st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.messages = []
        st.session_state.chat_session = model.start_chat(history=[])
        st.rerun()

    st.markdown("<div class='sb-label'>Geçmiş Analizler</div>", unsafe_allow_html=True)

    t_db = db.copy()
    for cid in sorted(t_db.keys(), reverse=True):
        if st.session_state.edit_id == cid:
            # ── Düzenleme modu ────────────────────
            new_val = st.text_input(
                "Ad",
                value=t_db[cid][0].get("title", t_db[cid][0]["content"][:20]),
                key=f"r_{cid}",
                label_visibility="collapsed"
            )
            col_save, col_cancel = st.columns(2, gap="small")
            with col_save:
                if st.button("✓ Kaydet", type="primary", key=f"s_{cid}", use_container_width=True):
                    t_db[cid][0]["title"] = new_val
                    save_db(t_db)
                    st.session_state.edit_id = None
                    st.rerun()
            with col_cancel:
                if st.button("✕ İptal", key=f"c_{cid}", use_container_width=True):
                    st.session_state.edit_id = None
                    st.rerun()
        else:
            # ── Normal görünüm ───────────────────
            c1, c2, c3 = st.columns([0.76, 0.12, 0.12], gap="small")
            with c1:
                display_t = t_db[cid][0].get("title", t_db[cid][0]["content"][:26] + "…")
                is_active = (st.session_state.current_chat_id == cid)
                label = f"{'▸ ' if is_active else ''}{display_t}"
                if st.button(label, key=f"ch_{cid}", use_container_width=True):
                    st.session_state.current_chat_id = cid
                    st.session_state.messages = t_db[cid]
                    st.rerun()
            with c2:
                if st.button("✦", key=f"e_{cid}"):
                    st.session_state.edit_id = cid
                    st.rerun()
            with c3:
                if st.button("✕", key=f"d_{cid}"):
                    del t_db[cid]
                    save_db(t_db)
                    if st.session_state.current_chat_id == cid:
                        st.session_state.messages = []
                        st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                    st.rerun()

# ==========================================
# 7. ANA EKRAN
# ==========================================
if not st.session_state.messages:
    st.markdown('<h1 class="portal-title">Siber Hukuk Portalı</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align:center;color:#64748B;font-size:1rem;margin-top:0.4rem;">'
        'Hukuki vakayı veya sormak istediğiniz dijital hakları aşağıya yazın.</p>',
        unsafe_allow_html=True
    )

for msg in st.session_state.messages:
    av = "👤" if msg["role"] == "user" else "⚖️"
    with st.chat_message(msg["role"], avatar=av):
        st.markdown(msg["content"])

# ==========================================
# 8. SOHBET GİRDİSİ VE ANALİZ
# ==========================================
if prompt := st.chat_input("Hukuki vakayı yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚖️"):
        st.markdown(
            '<p style="color:#94A3B8;font-style:italic;font-size:0.85rem;">⚖️ Analiz ediliyor…</p>',
            unsafe_allow_html=True
        )
        try:
            tam_prompt = f"GİZLİ SİSTEM KOMUTU: {SISTEM_PROMPTU}\n\nSORU: {prompt}"
            res = st.session_state.chat_session.send_message(tam_prompt, stream=True)

            st.empty()
            full_res = ""
            placeholder = st.empty()

            for chunk in res:
                full_res += chunk.text
                placeholder.markdown(full_res + "▌")
                time.sleep(0.01)

            placeholder.markdown(full_res)

            if len(st.session_state.messages) == 1:
                st.session_state.messages[0]["title"] = prompt[:28]

            st.session_state.messages.append({"role": "assistant", "content": full_res})
            db[st.session_state.current_chat_id] = st.session_state.messages
            save_db(db)

        except Exception as e:
            st.error("Model bağlantısında bir hata oluştu.")
