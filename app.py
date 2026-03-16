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
# 3. ÖZEL CSS (GÜVENLİ VE ZARİF TASARIM)
# ==========================================
st.markdown("""
<style>
    /* ANA UYGULAMA TEMA AYARLARI */
    .stApp, .main { background-color: #FFFFFF !important; }
    
    /* Üst barı SİLME, sadece şeffaf yap ki menü açma tuşu yaşasın */
    header[data-testid="stHeader"] { background-color: transparent !important; }
    
    /* Sadece sağ üstteki gereksiz "Deploy" vb. yazıları gizle */
    [data-testid="stToolbar"] { display: none !important; }

    /* SİDEBAR TASARIMI */
    section[data-testid="stSidebar"] { 
        background-color: #F8FAFC !important; 
        border-right: 1px solid #E2E8F0 !important;
    }

    /* ANA İÇERİK HİZALAMASI */
    .block-container { padding-top: 1rem !important; max-width: 850px !important; margin: 0 auto !important; }
    .portal-title { text-align: center; font-weight: 800; font-size: 2.2rem; color: #0F172A; margin-top: 0; pointer-events: none; }

    /* ========================================= */
    /* MODERN CHAT LİSTESİ (Kutular ve kaba emojiler yok) */
    /* ========================================= */
    
    /* Sol Menüdeki Tüm Butonların Kaba Çerçevelerini Sıfırla */
    div[data-testid="stVerticalBlock"] div.stButton > button {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
    }

    /* Geçmiş Analiz Metni (Sola Yaslı, Şeffaf) */
    [data-testid="column"]:nth-child(1) .stButton > button {
        text-align: left !important;
        padding: 6px 10px !important;
        color: #475569 !important;
        font-size: 0.95rem !important;
        border-radius: 8px !important;
    }
    [data-testid="column"]:nth-child(1) .stButton > button:hover {
        background: #E2E8F0 !important;
        color: #0F172A !important;
    }

    /* Düzenle (✎) ve Sil (✕) İkonları (Soluk ve Zarif) */
    [data-testid="column"]:nth-child(2) .stButton > button,
    [data-testid="column"]:nth-child(3) .stButton > button {
        color: #94A3B8 !important;
        font-size: 1.1rem !important;
        padding: 6px 0 !important;
    }
    [data-testid="column"]:nth-child(2) .stButton > button:hover { color: #3B82F6 !important; /* Mavi */ }
    [data-testid="column"]:nth-child(3) .stButton > button:hover { color: #EF4444 !important; /* Kırmızı */ }

    /* Yeni Analiz Butonu (Kurumsal Lacivert) */
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: #1E293B !important; 
        color: #FFFFFF !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover { background: #334155 !important; }

    /* ========================================= */
    /* MESAJ BALONLARI */
    /* ========================================= */
    [data-testid="stChatMessage"] { padding: 0.5rem 0 !important; }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown {
        background-color: #F1F5F9 !important; border-radius: 20px !important; padding: 10px 15px !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown {
        background-color: #FFFFFF !important; border: 1px solid #E2E8F0 !important; border-radius: 20px !important; 
        padding: 10px 15px !important; box-shadow: 0 2px 10px rgba(0,0,0,0.02) !important;
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
    # Model ismi korundu (Gemini 3 Flash'ın kod tarafındaki adı)
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
# 6. SOL MENÜ (STABİL VE MODERN)
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

    st.markdown("<p style='font-size:0.75rem; color:#64748B; font-weight:700; margin-top:25px; margin-bottom:10px; letter-spacing: 0.5px;'>GEÇMİŞ ANALİZLER</p>", unsafe_allow_html=True)
    
    t_db = db.copy()
    for cid in sorted(t_db.keys(), reverse=True):
        if st.session_state.edit_id == cid:
            new_val = st.text_input("Düzenle", value=t_db[cid][0].get("title", t_db[cid][0]["content"][:15]), key=f"r_{cid}", label_visibility="collapsed")
            if st.button("💾 Kaydet", key=f"s_{cid}", use_container_width=True):
                t_db[cid][0]["title"] = new_val
                save_db(t_db)
                st.session_state.edit_id = None
                st.rerun()
        else:
            c1, c2, c3 = st.columns([0.76, 0.12, 0.12])
            with c1:
                display_t = t_db[cid][0].get("title", t_db[cid][0]["content"][:22] + "...")
                # Emoji sildik, sadece metin
                if st.button(f"{display_t}", key=f"ch_{cid}", use_container_width=True):
                    st.session_state.current_chat_id = cid
                    st.session_state.messages = t_db[cid]
                    st.rerun()
            with c2:
                # Zarif kalem sembolü
                if st.button("✎", key=f"e_{cid}", help="Yeniden Adlandır"):
                    st.session_state.edit_id = cid
                    st.rerun()
            with c3:
                # Zarif çarpı sembolü
                if st.button("✕", key=f"d_{cid}", help="Sil"):
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
            
            st.empty() # Loading yazısını temizle
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
