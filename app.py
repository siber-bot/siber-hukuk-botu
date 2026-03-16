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
        except: return {}
    return {}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ==========================================
# 3. ÖZEL CSS — MODERN AI ARAYÜZÜ
# ==========================================
st.markdown("""
<style>
    /* ── GENEL UYGULAMA ── */
    .stApp, .main { background-color: #FFFFFF !important; }
    header[data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"]       { display: none !important; }

    /* ── SİDEBAR KAPSAYICI ── */
    section[data-testid="stSidebar"] {
        background-color: #171717 !important;
        border-right: 1px solid #2A2A2A !important;
        min-width: 280px !important;
        max-width: 280px !important;
        transform: none !important;
        visibility: visible !important;
        display: block !important;
    }
    section[data-testid="stSidebar"] > div:first-child {
        background-color: transparent !important;
        padding: 0 !important;
    }
    button[data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"] { display: none !important; }

    /* ── ANA İÇERİK ── */
    .block-container {
        padding-top: 2.5rem !important;
        max-width: 800px !important;
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

    /* ══════════════════════════════════════
       YENİ ANALİZ BAŞLAT BUTONU
    ══════════════════════════════════════ */
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: transparent !important;
        color: #E5E5E5 !important;
        border: 1px solid #3A3A3A !important;
        border-radius: 8px !important;
        padding: 0.55rem 1rem !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        letter-spacing: 0px !important;
        transition: background 0.15s ease, border-color 0.15s ease !important;
        width: 100% !important;
        box-shadow: none !important;
        text-align: left !important;
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background: #2A2A2A !important;
        border-color: #4A4A4A !important;
        transform: none !important;
        box-shadow: none !important;
    }

    /* ══════════════════════════════════════
       GEÇMİŞ ANALİZ SATIRLARI — ChatGPT/Claude stili
    ══════════════════════════════════════ */

    /* Her satır: tam genişlik, hover'da arka plan */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
        position: relative !important;
        border-radius: 8px !important;
        padding: 1px 0 !important;
        transition: background 0.15s ease !important;
        margin-bottom: 1px !important;
    }
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:hover {
        background: #2A2A2A !important;
    }

    /* Ana chat isim butonu */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(1) .stButton > button {
        text-align: left !important;
        padding: 9px 10px 9px 12px !important;
        color: #C9C9C9 !important;
        font-size: 0.875rem !important;
        font-weight: 400 !important;
        border-radius: 8px !important;
        border: none !important;
        background: transparent !important;
        transition: color 0.15s !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        box-shadow: none !important;
        width: 100% !important;
    }
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:hover
        > [data-testid="column"]:nth-child(1) .stButton > button {
        color: #FFFFFF !important;
        background: transparent !important;
    }

    /* Aksiyon butonları: VARSAYILAN gizli */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]
        > [data-testid="column"]:nth-child(2) .stButton > button,
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]
        > [data-testid="column"]:nth-child(3) .stButton > button {
        opacity: 0 !important;
        pointer-events: none !important;
        background: transparent !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 6px 8px !important;
        font-size: 0.8rem !important;
        color: #888 !important;
        transition: opacity 0.15s ease, background 0.15s ease, color 0.15s ease !important;
        box-shadow: none !important;
        min-height: unset !important;
        height: 32px !important;
        line-height: 1 !important;
    }

    /* Aksiyon butonları: HOVER'DA görünür */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:hover
        > [data-testid="column"]:nth-child(2) .stButton > button,
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:hover
        > [data-testid="column"]:nth-child(3) .stButton > button {
        opacity: 1 !important;
        pointer-events: auto !important;
    }

    /* Düzenle butonu hover */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:hover
        > [data-testid="column"]:nth-child(2) .stButton > button:hover {
        background: #383838 !important;
        color: #FFFFFF !important;
    }

    /* Sil butonu hover: zarif kırmızı */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:hover
        > [data-testid="column"]:nth-child(3) .stButton > button:hover {
        background: rgba(239, 68, 68, 0.15) !important;
        color: #F87171 !important;
    }

    /* ── DÜZENLEME MODU (Text Input + Kaydet) ── */
    [data-testid="stSidebar"] .stTextInput input {
        background: #2A2A2A !important;
        border: 1px solid #4A4A4A !important;
        border-radius: 7px !important;
        color: #E5E5E5 !important;
        font-size: 0.875rem !important;
        padding: 7px 10px !important;
    }
    [data-testid="stSidebar"] .stTextInput input:focus {
        border-color: #6B7280 !important;
        box-shadow: 0 0 0 2px rgba(107,114,128,0.2) !important;
    }

    /* Kaydet Butonu — düz, yeşilimsi vurgu */
    [data-testid="stSidebar"] .stButton > button[kind="primary"].save-btn,
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] ~ div .stButton > button[kind="primary"] {
        background: #1A3A2A !important;
        color: #6EE7B7 !important;
        border: 1px solid #2D5A40 !important;
        border-radius: 7px !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        padding: 6px 12px !important;
        box-shadow: none !important;
        transition: background 0.15s !important;
    }

    /* ══════════════════════════════════════
       MESAJ BALONLARI
    ══════════════════════════════════════ */
    [data-testid="stChatMessage"] { padding: 0.5rem 0 !important; }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown {
        background-color: #F1F5F9 !important;
        border-radius: 18px !important;
        padding: 10px 15px !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown {
        background-color: #FFFFFF !important;
        border: 1px solid #F1F5F9 !important;
        border-radius: 18px !important;
        padding: 10px 15px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
    }

    /* ══════════════════════════════════════
       SIDEBAR TİPOGRAFİ
    ══════════════════════════════════════ */
    .sidebar-brand {
        padding: 20px 16px 6px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .sidebar-brand-title {
        font-size: 1rem;
        font-weight: 600;
        color: #E5E5E5;
        margin: 0;
        letter-spacing: -0.2px;
    }
    .sidebar-tagline {
        font-size: 0.75rem;
        color: #6B7280;
        padding: 0 16px 16px;
        font-style: italic;
    }
    .sidebar-section-label {
        font-size: 0.7rem;
        font-weight: 600;
        color: #4B5563;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 16px 16px 6px;
    }
    .sidebar-owner {
        font-size: 0.82rem;
        color: #9CA3AF;
        padding: 0 16px 12px;
    }
    .sidebar-divider {
        border: none;
        border-top: 1px solid #2A2A2A;
        margin: 4px 0 8px;
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
# 6. SOL MENÜ — MODERN AI SİDEBAR
# ==========================================
with st.sidebar:
    # Marka başlığı
    st.markdown("""
        <div class='sidebar-brand'>
            <span style='font-size:1.15rem;'>⚖️</span>
            <p class='sidebar-brand-title'>Siber Asistan</p>
        </div>
        <p class='sidebar-tagline'>Dijital dünyada adaletin rehberi.</p>
    """, unsafe_allow_html=True)

    # Proje sahibi
    st.markdown("<div class='sidebar-section-label'>Proje Sahibi</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-owner'>👤 Merve [Soyadı]</div>", unsafe_allow_html=True)

    st.markdown("<hr class='sidebar-divider'/>", unsafe_allow_html=True)

    # Yeni analiz butonu
    if st.button("＋  Yeni Analiz Başlat", type="primary", use_container_width=True):
        st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.messages = []
        st.session_state.chat_session = model.start_chat(history=[])
        st.rerun()

    # Geçmiş analizler başlığı
    st.markdown("<div class='sidebar-section-label' style='margin-top:20px;'>Geçmiş Analizler</div>", unsafe_allow_html=True)

    t_db = db.copy()
    for cid in sorted(t_db.keys(), reverse=True):
        if st.session_state.edit_id == cid:
            # ── DÜZENLEME MODU ──────────────────────────
            new_val = st.text_input(
                "Yeniden adlandır",
                value=t_db[cid][0].get("title", t_db[cid][0]["content"][:20]),
                key=f"r_{cid}",
                label_visibility="collapsed"
            )
            col_save, col_cancel = st.columns([1, 1], gap="small")
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
            # ── NORMAL GÖRÜNÜM ───────────────────────────
            # Sütun oranları: geniş isim alanı, iki küçük ikon
            c1, c2, c3 = st.columns([0.72, 0.14, 0.14], gap="small")
            with c1:
                display_t = t_db[cid][0].get("title", t_db[cid][0]["content"][:22] + "…")
                is_active = (st.session_state.current_chat_id == cid)
                btn_label = f"{'◉ ' if is_active else ''}{display_t}"
                if st.button(btn_label, key=f"ch_{cid}", use_container_width=True):
                    st.session_state.current_chat_id = cid
                    st.session_state.messages = t_db[cid]
                    st.rerun()
            with c2:
                # Kalem ikonu — yeniden adlandır
                if st.button("✎", key=f"e_{cid}", help="Yeniden Adlandır"):
                    st.session_state.edit_id = cid
                    st.rerun()
            with c3:
                # Çöp kutusu — sil
                if st.button("⌫", key=f"d_{cid}", help="Sohbeti Sil"):
                    del t_db[cid]
                    save_db(t_db)
                    if st.session_state.current_chat_id == cid:
                        st.session_state.messages = []
                        st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                    st.rerun()

# ==========================================
# 7. ANA EKRAN & MESAJLAŞMA
# ==========================================
if not st.session_state.messages:
    st.markdown('<h1 class="portal-title">Siber Hukuk Portalı</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align:center; color:#64748B; font-size:1rem; margin-top:0.5rem;">'
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
            '<p style="color:#94A3B8; font-style:italic; font-size:0.85rem;">⚖️ Analiz ediliyor…</p>',
            unsafe_allow_html=True
        )
        try:
            tam_prompt = f"GİZLİ SİSTEM KOMUTU: {SISTEM_PROMPTU}\n\nSORU: {prompt}"
            res = st.session_state.chat_session.send_message(tam_prompt, stream=True)

            st.empty()
            full_res = ""
            message_placeholder = st.empty()

            for chunk in res:
                full_res += chunk.text
                message_placeholder.markdown(full_res + "▌")
                time.sleep(0.01)

            message_placeholder.markdown(full_res)

            if len(st.session_state.messages) == 1:
                st.session_state.messages[0]["title"] = prompt[:28]

            st.session_state.messages.append({"role": "assistant", "content": full_res})
            db[st.session_state.current_chat_id] = st.session_state.messages
            save_db(db)

        except Exception as e:
            st.error("Model bağlantısında bir hata oluştu.")
