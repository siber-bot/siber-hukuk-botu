import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. API VE MODEL AYARLARI
# ==========================================
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
except Exception as e:
    st.error("⚠️ API Anahtarı eksik veya hatalı. Lütfen secrets.toml dosyasını kontrol edin.")
    st.stop()

# ==========================================
# 2. SAYFA YAPILANDIRMASI
# ==========================================
st.set_page_config(
    page_title="Siber Hukuk Asistanı",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 3. GLOBAL CSS — TAM YENİDEN TASARIM
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* ── RESET & BASE ─────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: #0f0f0f !important;
    color: #e8e8e8 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Streamlit chrome gizle */
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
#MainMenu,
footer,
header { display: none !important; visibility: hidden !important; }

/* Sidebar gizle */
[data-testid="stSidebar"] { display: none !important; }

/* ── LAYOUT ───────────────────────────────────── */
.block-container {
    max-width: 780px !important;
    width: 100% !important;
    margin: 0 auto !important;
    padding: 0 1rem 5rem 1rem !important;
}

/* Tüm arka planları zorla siyah yap */
section.main, .main,
[data-testid="stAppViewContainer"] > section,
[data-testid="stMainBlockContainer"],
[data-testid="stVerticalBlock"] {
    background-color: #0f0f0f !important;
}

/* ── TOP NAV BAR ──────────────────────────────── */
.nav-bar {
    position: sticky;
    top: 0;
    z-index: 100;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 0;
    background: linear-gradient(to bottom, #0f0f0f 80%, transparent);
    margin-bottom: 0.5rem;
}

.nav-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1rem;
    font-weight: 600;
    color: #ffffff;
    letter-spacing: -0.01em;
}

.nav-logo-icon {
    width: 32px;
    height: 32px;
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
}

.nav-badge {
    font-size: 0.7rem;
    font-weight: 500;
    color: #6b7280;
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 20px;
    padding: 3px 10px;
    font-family: 'DM Mono', monospace;
}

/* ── HERO (BOŞ EKRAN) ─────────────────────────── */
.hero-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 4rem 0 2.5rem;
    text-align: center;
}

.hero-orb {
    width: 72px;
    height: 72px;
    background: radial-gradient(circle at 35% 35%, #3b82f6, #7c3aed 60%, #1e1b4b);
    border-radius: 50%;
    margin-bottom: 1.5rem;
    box-shadow: 0 0 40px rgba(124, 58, 237, 0.3), 0 0 80px rgba(59, 130, 246, 0.1);
    animation: pulse-orb 3s ease-in-out infinite;
}

@keyframes pulse-orb {
    0%, 100% { box-shadow: 0 0 40px rgba(124, 58, 237, 0.3), 0 0 80px rgba(59, 130, 246, 0.1); }
    50% { box-shadow: 0 0 60px rgba(124, 58, 237, 0.5), 0 0 120px rgba(59, 130, 246, 0.2); }
}

.hero-title {
    font-size: 2rem;
    font-weight: 600;
    color: #f9fafb;
    letter-spacing: -0.03em;
    margin-bottom: 0.6rem;
    line-height: 1.2;
}

.hero-sub {
    font-size: 0.95rem;
    color: #6b7280;
    max-width: 400px;
    line-height: 1.6;
    margin-bottom: 2.5rem;
}

/* ── SUGGESTION CHIPS ─────────────────────────── */
.chips-wrap {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
    max-width: 640px;
}

.chip {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 20px;
    padding: 8px 16px;
    font-size: 0.82rem;
    color: #9ca3af;
    cursor: pointer;
    transition: all 0.15s ease;
    white-space: nowrap;
}

.chip:hover {
    background: #232323;
    border-color: #404040;
    color: #d1d5db;
}

/* ── MESSAGES ─────────────────────────────────── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0.1rem 0 !important;
    box-shadow: none !important;
}

/* Kullanıcı mesajı */
[data-testid="stChatMessage"][data-testid*="user"],
.st-emotion-cache-1c7y2kl {
    background: transparent !important;
}

/* Avatar */
[data-testid="stChatMessage"] [data-testid="chatAvatarIcon-user"],
[data-testid="stChatMessage"] [data-testid="chatAvatarIcon-assistant"] {
    background: transparent !important;
    border: none !important;
}

/* Mesaj içeriği stili */
[data-testid="stChatMessage"] .stMarkdown p {
    font-size: 0.95rem !important;
    line-height: 1.75 !important;
    color: #e2e8f0 !important;
}

/* User bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown {
    background: #1e2433;
    border: 1px solid #2d3748;
    border-radius: 16px 16px 4px 16px;
    padding: 0.75rem 1rem;
    display: inline-block;
    max-width: 85%;
    float: right;
}

/* ── INPUT BAR ────────────────────────────────── */
/* Tüm sayfanın altını kapatan beyaz/gri katmanı sıfırla */
[data-testid="stBottom"] {
    background: #0f0f0f !important;
    border-top: none !important;
}

[data-testid="stChatFloatingInputContainer"] {
    background: #0f0f0f !important;
    padding: 0.75rem 1rem 1.25rem !important;
    border-top: 1px solid #1c1c1c !important;
}

[data-testid="stChatInput"] {
    background: #1a1a1a !important;
    border: 1px solid #2e2e2e !important;
    border-radius: 14px !important;
    transition: border-color 0.2s ease !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4) !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #4f46e5 !important;
    box-shadow: 0 4px 24px rgba(79, 70, 229, 0.15) !important;
}

[data-testid="stChatInput"] textarea {
    color: #e2e8f0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    caret-color: #818cf8 !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #4b5563 !important;
}

/* Send button */
[data-testid="stChatInputSubmitButton"] button {
    background: #4f46e5 !important;
    border-radius: 8px !important;
    border: none !important;
    transition: background 0.15s ease !important;
}
[data-testid="stChatInputSubmitButton"] button:hover {
    background: #4338ca !important;
}

/* ── SPINNER ──────────────────────────────────── */
[data-testid="stSpinner"] {
    color: #6366f1 !important;
}

/* ── DISCLAIMER ───────────────────────────────── */
.disclaimer {
    text-align: center;
    font-size: 0.72rem;
    color: #374151;
    padding: 0.5rem 0 1rem;
    font-family: 'DM Mono', monospace;
}

/* ── YENI SOHBET BUTONU ───────────────────────── */
.stButton > button {
    background: #1a1a1a !important;
    border: 1px solid #2e2e2e !important;
    color: #9ca3af !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.82rem !important;
    padding: 0.4rem 0.9rem !important;
    transition: all 0.15s ease !important;
}
.stButton > button:hover {
    background: #232323 !important;
    border-color: #404040 !important;
    color: #d1d5db !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #2a2a2a; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #3a3a3a; }

</style>
""", unsafe_allow_html=True)


# ==========================================
# 4. SİSTEM PROMPTU
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
3. Sonunda kısa bir yasal uyarı ekle
4. Gereksiz tekrar ve dolgu kelimelerden kaçın

ÖNEMLİ: Bu bir hukuki danışmanlık hizmeti değildir; bilgilendirme amaçlıdır."""


# ==========================================
# 5. SESSION STATE
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])


# ==========================================
# 6. NAVIGATION BAR
# ==========================================
col_logo, col_actions = st.columns([4, 1])

with col_logo:
    st.markdown("""
    <div class="nav-bar">
        <div class="nav-logo">
            <div class="nav-logo-icon">⚖️</div>
            Siber Hukuk Asistanı
        </div>
        <span class="nav-badge">v3.1 PRO</span>
    </div>
    """, unsafe_allow_html=True)

with col_actions:
    st.markdown("<div style='margin-top: 0.9rem;'>", unsafe_allow_html=True)
    if st.button("+ Yeni", key="new_chat"):
        st.session_state.messages = []
        st.session_state.chat_session = model.start_chat(history=[])
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# 7. BOŞKEN HERO EKRANI
# ==========================================
SUGGESTIONS = [
    "🔒 Hesabım hacklendi, ne yapmalıyım?",
    "📧 Phishing e-postası aldım",
    "🛡️ KVKK kapsamında haklarım neler?",
    "💳 Online dolandırıcılık nasıl şikayet edilir?",
    "📱 Sosyal medyada hakaret suç mu?",
    "🔍 Dijital delil nasıl toplanır?",
]

if len(st.session_state.messages) == 0:
    st.markdown("""
    <div class="hero-wrap">
        <div class="hero-orb"></div>
        <div class="hero-title">Size nasıl yardımcı olabilirim?</div>
        <div class="hero-sub">Bilişim suçları, siber güvenlik hukuku ve KVKK konularında sorularınızı yanıtlıyorum.</div>
        <div class="chips-wrap">
    """ + "".join([f'<span class="chip">{s}</span>' for s in SUGGESTIONS]) + """
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# 8. MESAJLARI GÖSTER
# ==========================================
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "⚖️"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])


# ==========================================
# 9. SOHBET AKIŞI
# ==========================================
if prompt := st.chat_input("Hukuki bir soru sorun veya vakayı anlatın…"):

    # Kullanıcı mesajı
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Asistan yanıtı
    with st.chat_message("assistant", avatar="⚖️"):
        with st.spinner(""):
            try:
                tam_prompt = f"{SISTEM_PROMPTU}\n\nKullanıcı sorusu: {prompt}"
                response = st.session_state.chat_session.send_message(tam_prompt)
                yanit = response.text
                st.markdown(yanit)
                st.session_state.messages.append({"role": "assistant", "content": yanit})

                if len(st.session_state.messages) == 2:
                    st.rerun()

            except Exception:
                hata = "Sunucularımızda anlık bir yoğunluk yaşanıyor. Lütfen birkaç saniye sonra tekrar deneyin."
                st.error(hata)
                st.session_state.messages.append({"role": "assistant", "content": hata})


# ==========================================
# 10. ALT BİLGİ (DISCLAIMER)
# ==========================================
st.markdown("""
<div class="disclaimer">
    ⚠️ Bu asistan avukat değildir ve hukuki danışmanlık sunmaz. Bilgilendirme amaçlıdır.
</div>
""", unsafe_allow_html=True)
