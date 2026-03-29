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
# 3. ÖZEL CSS (MENÜ VE İKON DÜZELTMELERİ)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&display=swap');
    * { font-family: 'DM Sans', sans-serif !important; }

    /* ── GENEL VE GİZLEMELER ── */
    header[data-testid="stHeader"], footer, [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stStatusWidget"], [data-testid="stDeployButton"] { display: none !important; }
    .stApp { background-color: #F8FAFC !important; }

    /* ── SOHBET BALONCUKLARI VE TİPOGRAFİ ── */
    [data-testid="stChatMessage"] { padding: 0.8rem 0 !important; line-height: 1.6 !important; }
    
    /* Kullanıcı Balonu */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 16px 16px 0 16px !important;
        padding: 12px 18px !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03) !important;
    }

    /* Asistan Balonu (Uçuk Mavi) */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown {
        background-color: #F0F7FF !important;
        border: 1px solid #D1E5FF !important;
        border-radius: 16px 16px 16px 0 !important;
        padding: 12px 18px !important;
    }

    /* Gönder Butonu Rengi */
    [data-testid="stChatInput"] button { background-color: #0F172A !important; color: white !important; }

    /* ── SIDEBAR & MENÜ İKONLARI (DÜZELTİLDİ) ── */
    section[data-testid="stSidebar"] { background-color: #F9FAFB !important; border-right: 1px solid #E5E7EB !important; }
    
    /* Sidebar Başlık ve Boşluklar */
    .sb-logo { padding: 15px 5px 0; display: flex; align-items: center; gap: 8px; }
    .sb-label { font-size: 0.65rem; font-weight: 600; color: #9CA3AF; text-transform: uppercase; padding: 12px 5px 5px; }

    /* Geçmiş Listesi Satır Tasarımı */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
        align-items: center !important;
        gap: 2px !important;
        padding: 2px 5px !important;
        border-radius: 8px;
        transition: background 0.15s ease;
    }
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:hover { background: #EAEFF6 !important; }

    /* Metin Kesme ve Buton Temizliği */
    [data-testid="stSidebar"] button { 
        border: none !important; 
        background: transparent !important; 
        box-shadow: none !important; 
        padding: 0 !important;
    }
    
    /* İkonların Küçültülmesi ve Hizalanması */
    [data-testid="stSidebar"] [data-testid="column"] .stButton button {
        font-size: 0.85rem !important;
        color: #94A3B8 !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }
    [data-testid="stSidebar"] [data-testid="column"] .stButton button:hover {
        color: #1E293B !important;
        transform: scale(1.1);
    }

    /* Ana İçerik Genişliği */
    .block-container { max-width: 820px !important; padding-top: 2.5rem !important; }
    .portal-title { text-align: center; font-weight: 700; font-size: 2rem; color: #0F172A; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. API VE MODEL
# ==========================================
SISTEM_PROMPTU = "Sen uzman bir Siber Hukuk Asistanısın. Yanıtlarını resmi, madde işaretli ve Türkiye yasalarına dayandırarak ver."

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    # İlk koddaki model ismini koruyoruz
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
        <div class='sb-logo'>⚖️ <p style='font-size:1rem; font-weight:600; margin:0;'>Siber Asistan</p></div>
        <p style='font-size:0.75rem; color:#94A3B8; font-style:italic; padding:0 5px;'>Dijital adaletin rehberi.</p>
        <div class='sb-label'>Proje Sahibi</div>
        <p style='font-size:0.85rem; color:#374151; padding:0 5px; font-weight:500;'>👤 Merve Havuz</p>
        <hr style='border:none; border-top:1px solid #E5E7EB; margin:10px 0;'/>
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
            new_val = st.text_input("Ad", value=t_db[cid][0].get("title", t_db[cid][0]["content"][:20]), key=f"r_{cid}", label_visibility="collapsed")
            c_s, c_c = st.columns(2)
            with c_s: 
                if st.button("✓", key=f"s_{cid}"):
                    t_db[cid][0]["title"] = new_val; save_db(t_db); st.session_state.edit_id = None; st.rerun()
            with c_c:
                if st.button("✕", key=f"c_{cid}"):
                    st.session_state.edit_id = None; st.rerun()
        else:
            c1, c2, c3 = st.columns([0.76, 0.12, 0.12])
            with c1:
                display_t = t_db[cid][0].get("title", t_db[cid][0]["content"][:24] + "…")
                is_active = (st.session_state.current_chat_id == cid)
                label = f"{'▸ ' if is_active else ''}{display_t}"
                if st.button(label, key=f"ch_{cid}", use_container_width=True):
                    st.session_state.current_chat_id = cid
                    st.session_state.messages = t_db[cid]
                    st.rerun()
            with c2:
                if st.button("✦", key=f"e_{cid}"): # Düzenle ikonu
                    st.session_state.edit_id = cid; st.rerun()
            with c3:
                if st.button("✕", key=f"d_{cid}"): # Sil ikonu
                    del t_db[cid]; save_db(t_db); st.rerun()

# ==========================================
# 7. ANA EKRAN
# ==========================================
if not st.session_state.messages:
    st.markdown('<h1 class="portal-title">Siber Hukuk Portalı</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;color:#64748B;">Hukuki vakayı veya dijital haklarınızı aşağıya yazın.</p>', unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="👤" if msg["role"]=="user" else "⚖️"):
        st.markdown(msg["content"])

# ==========================================
# 8. SOHBET GİRDİSİ VE ANALİZ (ORİJİNAL MANTIK GERİ GELDİ)
# ==========================================
if prompt := st.chat_input("Hukuki vakayı yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚖️"):
        st.markdown('<p style="color:#94A3B8; font-style:italic; font-size:0.85rem;">⚖️ Analiz ediliyor…</p>', unsafe_allow_html=True)
        
        try:
            # İLK KODDAKİ TAM PROMPT VE STREAM YAPISI
            tam_prompt = f"GİZLİ SİSTEM KOMUTU: {SISTEM_PROMPTU}\n\nSORU: {prompt}"
            res = st.session_state.chat_session.send_message(tam_prompt, stream=True)

            st.empty()
            full_res = ""
            placeholder = st.empty()

            for chunk in res:
                full_res += chunk.text
                placeholder.markdown(full_res + "▌")
                time.sleep(0.01) # Orijinal bekleme süresi

            placeholder.markdown(full_res)

            if len(st.session_state.messages) == 1:
                st.session_state.messages[0]["title"] = prompt[:28]

            st.session_state.messages.append({"role": "assistant", "content": full_res})
            db[st.session_state.current_chat_id] = st.session_state.messages
            save_db(db)

        except Exception as e:
            st.error("Model bağlantısında bir hata oluştu.")
