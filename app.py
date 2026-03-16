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
# 3. ÖZEL CSS (GENÇ, DİNAMİK VE İNOVATİF)
# ==========================================
st.markdown("""
<style>
    /* ANA UYGULAMA TEMA AYARLARI */
    .stApp, .main { background-color: #FFFFFF !important; }
    header[data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }

    /* SİDEBAR'I ZORLA AÇIK TUTAN YAPI */
    section[data-testid="stSidebar"] { 
        background-color: #F9FAFB !important; 
        border-right: 1px solid #E5E7EB !important;
        min-width: 320px !important;
        max-width: 320px !important;
        transform: none !important;
        visibility: visible !important;
        display: block !important;
    }
    section[data-testid="stSidebar"] > div:first-child { background-color: transparent !important; }
    button[data-testid="stSidebarCollapseButton"], [data-testid="collapsedControl"] { display: none !important; }

    .block-container { padding-top: 2.5rem !important; max-width: 850px !important; margin: 0 auto !important; }
    .portal-title { text-align: center; font-weight: 800; font-size: 2.2rem; color: #0F172A; margin-top: 0; pointer-events: none; }

    /* YENİ ANALİZ BUTONU (KURUMSAL AMA HAVALI) */
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: #1E293B !important; 
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 1rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        box-shadow: 0 4px 10px rgba(30, 41, 59, 0.2) !important;
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background: #0F172A !important;
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 6px 15px rgba(30, 41, 59, 0.3) !important;
    }

    /* GEÇMİŞ ANALİZ METNİ (Sola Yaslı, Modern) */
    [data-testid="column"]:nth-child(1) .stButton > button[kind="secondary"] {
        text-align: left !important;
        padding: 10px 12px !important;
        color: #374151 !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        border-radius: 12px !important;
        border: none !important;
        background: transparent !important;
        transition: all 0.2s !important;
    }
    [data-testid="column"]:nth-child(1) .stButton > button[kind="secondary"]:hover {
        background: #F1F5F9 !important;
        color: #0F172A !important;
    }

    /* ========================================= */
    /* GENÇ & DİNAMİK AKSİYON BUTONLARI (Z KUŞAĞI) */
    /* ========================================= */
    
    /* İkon Kolonları: Kapsül (Pill) Şekli ve 3D His */
    [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(2) .stButton > button,
    [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(3) .stButton > button {
        border: none !important;
        background: #F1F5F9 !important; /* Standart yumuşak gri */
        border-radius: 14px !important; /* Modern squircle hatlar */
        padding: 6px 0 !important;
        font-size: 1.1rem !important;
        color: #64748B !important;
        /* Alışılagelmişin dışında, oyun tarzı zıplama animasyonu */
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important; 
    }

    /* 🪄 Sihir (Düzenle) Butonu Hover: Neon Mor/Pembe Gradient */
    [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(2) .stButton > button:hover {
        background: linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%) !important;
        color: white !important;
        /* Zıplayıp sağa yatma efekti */
        transform: translateY(-4px) scale(1.15) rotate(10deg) !important;
        box-shadow: 0 8px 15px rgba(236, 72, 153, 0.4) !important;
    }

    /* 💥 Patlat (Sil) Butonu Hover: Neon Kırmızı/Turuncu Gradient */
    [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(3) .stButton > button:hover {
        background: linear-gradient(135deg, #EF4444 0%, #F97316 100%) !important;
        color: white !important;
        /* Zıplayıp sola yatma efekti */
        transform: translateY(-4px) scale(1.15) rotate(-10deg) !important;
        box-shadow: 0 8px 15px rgba(239, 68, 68, 0.4) !important;
    }

    /* ========================================= */
    /* MESAJ BALONLARI */
    [data-testid="stChatMessage"] { padding: 0.5rem 0 !important; }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown {
        background-color: #F1F5F9 !important; border-radius: 20px !important; padding: 10px 15px !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown {
        background-color: #FFFFFF !important; border: 1px solid #F1F5F9 !important; border-radius: 20px !important; 
        padding: 10px 15px !important; box-shadow: 0 4px 15px rgba(0,0,0,0.03) !important;
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
# 6. SOL MENÜ (İNOVATİF SİDEBAR)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color:#0F172A; margin-top:0px; margin-bottom:5px; font-weight:800;'>⚖️ Siber Asistan</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.85rem; color:#3B82F6; font-style:italic; margin-bottom:25px;'>Dijital dünyada adaletin rehberi.</p>", unsafe_allow_html=True)
    
    st.markdown("<p style='font-size:0.75rem; color:#64748B; font-weight:700; margin-bottom:5px; letter-spacing: 0.5px;'>PROJE SAHİBİ</p>", unsafe_allow_html=True)
    st.markdown("👤 **Merve [Soyadı]**")
    
    st.divider()
    
    if st.button("➕ Yeni Analiz Başlat", type="primary", use_container_width=True):
        st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.messages = []
        st.session_state.chat_session = model.start_chat(history=[])
        st.rerun()

    st.markdown("<p style='font-size:0.75rem; color:#64748B; font-weight:700; margin-top:25px; margin-bottom:15px; letter-spacing: 0.5px;'>GEÇMİŞ ANALİZLER</p>", unsafe_allow_html=True)
    
    t_db = db.copy()
    for cid in sorted(t_db.keys(), reverse=True):
        if st.session_state.edit_id == cid:
            new_val = st.text_input("Düzenle", value=t_db[cid][0].get("title", t_db[cid][0]["content"][:15]), key=f"r_{cid}", label_visibility="collapsed")
            # Kaydet butonunu da "Primary" yapıp Roket ekledik!
            if st.button("🚀 Kaydet", type="primary", key=f"s_{cid}", use_container_width=True):
                t_db[cid][0]["title"] = new_val
                save_db(t_db)
                st.session_state.edit_id = None
                st.rerun()
        else:
            # Kolon oranlarını yeni animasyonlar için optimize ettik
            c1, c2, c3 = st.columns([0.68, 0.16, 0.16], gap="small")
            with c1:
                display_t = t_db[cid][0].get("title", t_db[cid][0]["content"][:20] + "...")
                if st.button(f"{display_t}", key=f"ch_{cid}", use_container_width=True):
                    st.session_state.current_chat_id = cid
                    st.session_state.messages = t_db[cid]
                    st.rerun()
            with c2:
                # Sihir Değneği Butonu
                if st.button("🪄", key=f"e_{cid}", help="İsmi Yeniden Adlandır"):
                    st.session_state.edit_id = cid
                    st.rerun()
            with c3:
                # Patlama (Yok Etme) Butonu
                if st.button("💥", key=f"d_{cid}", help="Geçmişi Sil"):
                    del t_db[cid]
                    save_db(t_db)
                    if st.session_state.current_chat_id == cid: 
                        st.session_state.messages = []
                    st.rerun()

# ==========================================
# 7. ANA EKRAN & MESAJLAŞMA
# ==========================================
if not st.session_state.messages:
    st.markdown('<h1 class="portal-title">Siber Hukuk Portalı</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#64748B; font-size:1.1rem;">Hukuki vakayı veya sormak istediğiniz dijital hakları aşağıya yazın.</p>', unsafe_allow_html=True)

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
        st.markdown('<p style="color:#94A3B8; font-style:italic; font-size:0.85rem;">⚖️ Analiz ediliyor...</p>', unsafe_allow_html=True)
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
                st.session_state.messages[0]["title"] = prompt[:25]
                
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            db[st.session_state.current_chat_id] = st.session_state.messages
            save_db(db)
            
        except Exception as e:
            st.error("Model bağlantısında bir hata oluştu.")
