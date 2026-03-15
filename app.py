import streamlit as st
import google.generativeai as genai
from datetime import datetime

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
except Exception as e:
    st.error("⚠️ API Anahtarı eksik veya hatalı. Lütfen secrets.toml dosyasını kontrol edin.")
    st.stop()

st.set_page_config(
    page_title="Siber Hukuk Asistanı",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&family=DM+Mono:wght@400;500&family=Playfair+Display:wght@600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
.stApp {
    background-color: #f7f7f8 !important;
    color: #1a1a2e !important;
    font-family: 'DM Sans', sans-serif !important;
}

section.main, .main,
[data-testid="stAppViewContainer"] > section,
[data-testid="stMainBlockContainer"],
[data-testid="stVerticalBlock"] {
    background-color: #f7f7f8 !important;
}

[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
#MainMenu, footer, header {
    display: none !important;
    visibility: hidden !important;
}

/* ── SIDEBAR ──────────────────────────────────── */
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e5e7eb !important;
    min-width: 260px !important;
    max-width: 260px !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 1.5rem 1rem 1rem !important;
}

.sidebar-header {
    margin-bottom: 1.5rem;
}
.sidebar-brand {
    font-size: 1rem;
    font-weight: 600;
    color: #111827;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 0.3rem;
}
.sidebar-brand-icon {
    width: 28px; height: 28px;
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    border-radius: 7px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.8rem;
}
.sidebar-dev {
    font-size: 0.75rem;
    color: #9ca3af;
    font-family: 'DM Mono', monospace;
    padding-left: 36px;
}
.sidebar-divider {
    height: 1px;
    background: #f3f4f6;
    margin: 1rem 0;
}
.sidebar-section-title {
    font-size: 0.7rem;
    font-weight: 600;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.6rem;
    font-family: 'DM Mono', monospace;
}
.chat-history-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 10px;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.1s ease;
    margin-bottom: 2px;
}
.chat-history-item:hover { background: #f3f4f6; }
.chat-history-item.active { background: #eef2ff; }
.chat-icon { font-size: 0.8rem; color: #9ca3af; }
.chat-label {
    font-size: 0.82rem;
    color: #374151;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 180px;
}
.chat-label.active { color: #4338ca; font-weight: 500; }
.chat-date {
    font-size: 0.68rem;
    color: #d1d5db;
    margin-left: auto;
    flex-shrink: 0;
    font-family: 'DM Mono', monospace;
}
.sidebar-new-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
    padding: 9px 12px;
    background: #4f46e5;
    color: #ffffff;
    border: none;
    border-radius: 9px;
    font-size: 0.84rem;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.15s ease;
    font-family: 'DM Sans', sans-serif;
    margin-bottom: 1rem;
}
.sidebar-new-btn:hover { background: #4338ca; }

/* ── LAYOUT ───────────────────────────────────── */
.block-container {
    max-width: 780px !important;
    width: 100% !important;
    margin: 0 auto !important;
    padding: 0 1rem 5rem 1rem !important;
}

/* ── NAV BAR (sadece boş ekranda) ─────────────── */
.nav-bar {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1.5rem 0 0.5rem;
}
.nav-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.05rem;
    font-weight: 600;
    color: #111827;
    letter-spacing: -0.01em;
}
.nav-logo-icon {
    width: 32px; height: 32px;
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.9rem;
}

/* ── HERO ─────────────────────────────────────── */
.hero-wrap {
    display: flex; flex-direction: column;
    align-items: center; padding: 2rem 0 2rem; text-align: center;
}
.hero-orb {
    width: 72px; height: 72px;
    background: radial-gradient(circle at 35% 35%, #3b82f6, #7c3aed 60%, #c4b5fd);
    border-radius: 50%; margin-bottom: 1.5rem;
    box-shadow: 0 0 40px rgba(124,58,237,0.2), 0 0 80px rgba(59,130,246,0.1);
    animation: pulse-orb 3s ease-in-out infinite;
}
@keyframes pulse-orb {
    0%,100% { box-shadow: 0 0 40px rgba(124,58,237,0.2), 0 0 80px rgba(59,130,246,0.1); }
    50%      { box-shadow: 0 0 60px rgba(124,58,237,0.35), 0 0 120px rgba(59,130,246,0.15); }
}
.hero-title {
    font-size: 2rem; font-weight: 600; color: #111827;
    letter-spacing: -0.03em; margin-bottom: 0.6rem; line-height: 1.2;
}
.hero-sub {
    font-size: 0.95rem; color: #6b7280;
    max-width: 400px; line-height: 1.6; margin-bottom: 2rem;
}

/* ── SUGGESTION CHIPS ─────────────────────────── */
.chips-wrap {
    display: flex; flex-wrap: wrap; gap: 8px;
    justify-content: center; max-width: 620px;
}
.chip {
    background: #ffffff; border: 1px solid #e5e7eb;
    border-radius: 20px; padding: 8px 16px;
    font-size: 0.82rem; color: #374151; cursor: pointer;
    transition: all 0.15s ease; white-space: nowrap;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.chip:hover { background: #eef2ff; border-color: #c7d2fe; color: #4338ca; }

/* ── MESSAGES ─────────────────────────────────── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important; padding: 0.1rem 0 !important;
    box-shadow: none !important;
}
[data-testid="stChatMessage"] [data-testid="chatAvatarIcon-user"],
[data-testid="stChatMessage"] [data-testid="chatAvatarIcon-assistant"] {
    background: transparent !important; border: none !important;
}
[data-testid="stChatMessage"] .stMarkdown p {
    font-size: 0.95rem !important; line-height: 1.75 !important; color: #1f2937 !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown {
    background: #eef2ff; border: 1px solid #c7d2fe;
    border-radius: 16px 16px 4px 16px;
    padding: 0.75rem 1rem; display: inline-block;
    max-width: 85%; float: right;
}

/* ── INPUT BAR ────────────────────────────────── */
[data-testid="stBottom"] {
    background: #f7f7f8 !important; border-top: none !important;
}
[data-testid="stChatFloatingInputContainer"] {
    background: #f7f7f8 !important;
    padding: 0.75rem 1rem 1.25rem !important;
    border-top: 1px solid #e5e7eb !important;
}
[data-testid="stChatInput"] {
    background: #ffffff !important; border: 1px solid #d1d5db !important;
    border-radius: 14px !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06) !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
}
[data-testid="stChatInput"] textarea {
    color: #111827 !important; font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important; caret-color: #6366f1 !important;
    background: transparent !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #9ca3af !important; }
[data-testid="stChatInputSubmitButton"] button {
    background: #4f46e5 !important; border-radius: 8px !important;
    border: none !important; transition: background 0.15s ease !important;
}
[data-testid="stChatInputSubmitButton"] button:hover { background: #4338ca !important; }

/* ── SPINNER ──────────────────────────────────── */
[data-testid="stSpinner"] { color: #6366f1 !important; }

/* ── DISCLAIMER ───────────────────────────────── */
.disclaimer {
    text-align: center;
    font-family: 'Playfair Display', serif;
    font-size: 0.82rem;
    font-weight: 600;
    color: #dc2626;
    background: #fff7f7;
    border: 1px solid #fecaca;
    border-radius: 10px;
    padding: 0.65rem 1.2rem;
    margin: 0.5rem auto 1rem;
    max-width: 520px;
    letter-spacing: 0.01em;
}

/* ── STREAMLIT BUTTONS ────────────────────────── */
.stButton > button {
    background: #ffffff !important; border: 1px solid #e5e7eb !important;
    color: #374151 !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 0.82rem !important;
    padding: 0.4rem 0.9rem !important; transition: all 0.15s ease !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
}
.stButton > button:hover {
    background: #f9fafb !important; border-color: #c7d2fe !important; color: #4338ca !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #9ca3af; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SİSTEM PROMPTU
# ==========================================
SISTEM_PROMPTU = """Sen "Siber Hukuk Asistanı" adlı uzman bir yapay zeka sistemsin.
Türk Hukuku kapsamında bilişim suçları, siber güvenlik hukuku ve veri gizliliği konularında derin bilgiye sahipsin.

Temel uzmanlık alanların:
- TCK (Türk Ceza Kanunu) Bilişim Suçları: Madde 243-246
- KVKK (Kişisel Verilerin Korunması Kanunu) ve veri ihlalleri
- BTK (Bilgi Teknolojileri ve İletişim Kurumu) mevzuatı
- USOM (Ulusal Siber Olaylara Müdahale Merkezi) prosedürleri
- Siber zorbalık, dolandırıcılık, kimlik hırsızlığı vakaları
- Elektronik delil ve dijital adli bilişim hukuku

Cevap kuralların:
1. Her zaman Türkçe yanıt ver
2. Yapılandırılmış, okunması kolay yanıtlar yaz
3. İlgili kanun maddelerini açıkça belirt (örn: TCK m.243)
4. Pratik adımlar ve öneri sun
5. Sonunda kısa bir yasal uyarı ekle
6. Gereksiz tekrar ve dolgu kelimelerden kaçın

ÖNEMLİ: Bu bir hukuki danışmanlık hizmeti değildir; bilgilendirme amaçlıdır."""

# ==========================================
# SESSION STATE
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = []  # [{title, messages, date}]
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# ==========================================
# YARDIMCI FONKSİYONLAR
# ==========================================
def save_current_chat():
    if st.session_state.messages:
        first_msg = st.session_state.messages[0]["content"]
        title = first_msg[:40] + ("…" if len(first_msg) > 40 else "")
        st.session_state.chat_histories.insert(0, {
            "title": title,
            "messages": st.session_state.messages.copy(),
            "date": datetime.now().strftime("%d.%m")
        })

def start_new_chat():
    save_current_chat()
    st.session_state.messages = []
    st.session_state.chat_session = model.start_chat(history=[])
    st.session_state.pending_prompt = None

def load_chat(idx):
    save_current_chat()
    st.session_state.messages = st.session_state.chat_histories[idx]["messages"].copy()
    st.session_state.chat_session = model.start_chat(history=[])
    st.session_state.pending_prompt = None

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <div class="sidebar-brand">
            <div class="sidebar-brand-icon">⚖️</div>
            Siber Hukuk Asistanı
        </div>
        <div class="sidebar-dev">Merve &amp; [Adın] · 2025</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("＋  Yeni Sohbet", key="sidebar_new", use_container_width=True):
        start_new_chat()
        st.rerun()

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-title">Geçmiş Sohbetler</div>', unsafe_allow_html=True)

    if not st.session_state.chat_histories:
        st.markdown('<p style="font-size:0.8rem;color:#c4c4c4;padding:4px 10px;">Henüz geçmiş sohbet yok.</p>', unsafe_allow_html=True)
    else:
        for i, chat in enumerate(st.session_state.chat_histories):
            col1, col2 = st.columns([5, 1])
            with col1:
                if st.button(f"💬  {chat['title']}", key=f"history_{i}", use_container_width=True):
                    load_chat(i)
                    st.rerun()
            with col2:
                st.markdown(f"<span style='font-size:0.65rem;color:#d1d5db;line-height:2.8;display:block;text-align:right'>{chat['date']}</span>", unsafe_allow_html=True)

# ==========================================
# ANA İÇERİK
# ==========================================
is_empty = len(st.session_state.messages) == 0

# Nav bar sadece boş ekranda
if is_empty:
    st.markdown("""
    <div class="nav-bar">
        <div class="nav-logo">
            <div class="nav-logo-icon">⚖️</div>
            Siber Hukuk Asistanı
        </div>
    </div>
    """, unsafe_allow_html=True)

# Hero + chips
SUGGESTIONS = [
    "🔒 Hesabım hacklendi, ne yapmalıyım?",
    "📧 Phishing e-postası aldım",
    "🛡️ KVKK kapsamında haklarım neler?",
    "💳 Online dolandırıcılık nasıl şikayet edilir?",
    "📱 Sosyal medyada hakaret suç mu?",
    "🔍 Dijital delil nasıl toplanır?",
]

if is_empty:
    st.markdown("""
    <div class="hero-wrap">
        <div class="hero-orb"></div>
        <div class="hero-title">Size nasıl yardımcı olabilirim?</div>
        <div class="hero-sub">Bilişim suçları, siber güvenlik hukuku ve KVKK konularında sorularınızı yanıtlıyorum.</div>
    </div>
    """, unsafe_allow_html=True)

    # Chip butonları — tıklanınca pending_prompt set eder
    cols = st.columns(2)
    for i, suggestion in enumerate(SUGGESTIONS):
        with cols[i % 2]:
            if st.button(suggestion, key=f"chip_{i}", use_container_width=True):
                st.session_state.pending_prompt = suggestion
                st.rerun()

# Mesajları göster
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "⚖️"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ==========================================
# SOHBET AKIŞI — hem chat_input hem chip
# ==========================================
def handle_prompt(prompt: str):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    with st.chat_message("assistant", avatar="⚖️"):
        with st.spinner(""):
            try:
                tam_prompt = f"{SISTEM_PROMPTU}\n\nKullanıcı sorusu: {prompt}"
                response = st.session_state.chat_session.send_message(tam_prompt)
                yanit = response.text
                st.markdown(yanit)
                st.session_state.messages.append({"role": "assistant", "content": yanit})
            except Exception:
                hata = "Sunucularımızda anlık bir yoğunluk yaşanıyor. Lütfen birkaç saniye sonra tekrar deneyin."
                st.error(hata)
                st.session_state.messages.append({"role": "assistant", "content": hata})

# Chip'ten gelen pending prompt
if st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None
    handle_prompt(prompt)
    st.rerun()

# Chat input
if prompt := st.chat_input("Hukuki bir soru sorun veya vakayı anlatın…"):
    handle_prompt(prompt)
    st.rerun()

# ==========================================
# DISCLAIMER
# ==========================================
st.markdown("""
<div class="disclaimer">
    ⚠️ Bu asistan avukat değildir ve hukuki danışmanlık sunmaz — yalnızca bilgilendirme amaçlıdır.
</div>
""", unsafe_allow_html=True)
