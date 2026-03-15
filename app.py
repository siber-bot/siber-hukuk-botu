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
# 2. SIFIRDAN TASARLANAN İNOVATİF CSS
# ==========================================
st.markdown("""
<style>
    /* ÜST BAR GİZLEME AMA MENÜ TUŞUNU KORUMA */
    [data-testid="stHeader"] { background-color: rgba(255,255,255,0); }
    [data-testid="stToolbar"] { display: none !important; }
    
    /* MENÜ KAPALIYKEN AÇMA TUŞUNUN GÖRÜNÜRLÜĞÜ */
    .st-emotion-cache-6qob1r { 
        position: fixed; 
        left: 20px; 
        top: 20px; 
        z-index: 1000000; 
        background: #F8FAFC; 
        border-radius: 10px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    /* ANA KONTEYNER AYARLARI */
    .block-container { padding-top: 1rem !important; max-width: 900px !important; }
    [data-testid="stSidebar"] { 
        background-color: #F8FAFC !important; 
        border-right: 1px solid #E2E8F0 !important;
        padding-top: 0 !important;
    }

    /* MARKA ALANI */
    .brand-section { padding: 10px 0; border-bottom: 1px solid #F1F5F9; margin-bottom: 20px; }
    .brand-title { font-size: 1.25rem; font-weight: 800; color: #1E293B; letter-spacing: -0.5px; }
    .motivation { font-size: 0.8rem; color: #3B82F6; font-style: italic; line-height: 1.2; margin-top: 5px; }

    /* İNOVATİF CHAT LİSTESİ (Hover Effect) */
    .chat-item-wrapper {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 12px;
        margin: 4px 0;
        border-radius: 12px;
        transition: all 0.2s ease;
        cursor: pointer;
        position: relative;
    }
    
    .chat-item-wrapper:hover {
        background: #F1F5F9;
    }

    /* YENİ SOHBET BUTONU */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 20px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2) !important;
    }

    /* MESAJ BALONLARI */
    [data-testid="stChatMessage"] { border: none !important; }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown {
        background-color: #F1F5F9 !important;
        border-radius: 20px 20px 4px 20px !important;
        padding: 15px 20px !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown {
        background-color: #FFFFFF !important;
        border: 1px solid #F1F5F9 !important;
        border-radius: 20px 20px 20px 4px !important;
        padding: 15px 20px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.03) !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. API VE MODEL
# ==========================================
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-3-flash-preview') 
except:
    st.error("Sistem Hatası!")
    st.stop()

# ==========================================
# 4. VERİ YÖNETİMİ
# ==========================================
db = load_db()

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
if "messages" not in st.session_state:
    st.session_state.messages = db.get(st.session_state.current_chat_id, [])
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
if "rename_id" not in st.session_state:
    st.session_state.rename_id = None

# ==========================================
# 5. SOL MENÜ (İNOVATİF TASARIM)
# ==========================================
with st.sidebar:
    # Üst Bölüm
    st.markdown("""
        <div class="brand-section">
            <div class="brand-title">⚖️ Siber Hukuk</div>
            <div class="motivation">Dijital dünyada adaletin rehberi, siber güvenliğin sesi.</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<p style="font-size:0.65rem; color:#94A3B8; font-weight:700; margin-bottom:10px;">PROJE SAHİBİ</p>', unsafe_allow_html=True)
    st.markdown("👤 **Merve [Soyadı]**")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("➕ Yeni Analiz Başlat", type="primary", use_container_width=True):
        st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.messages = []
        st.session_state.chat_session = model.start_chat(history=[])
        st.session_state.rename_id = None
        st.rerun()

    st.markdown('<p style="font-size:0.65rem; color:#94A3B8; font-weight:700; margin-top:25px; margin-bottom:10px;">GEÇMİŞ SOHBETLER</p>', unsafe_allow_html=True)
    
    # Yeni Nesil Chat Listesi
    temp_db = db.copy()
    for cid in sorted(temp_db.keys(), reverse=True):
        # Konteyner ile butonları hizalıyoruz
        with st.container():
            if st.session_state.rename_id == cid:
                new_t = st.text_input("Yeniden Adlandır", value=temp_db[cid][0].get("title", temp_db[cid][0]["content"][:15]), key=f"rename_{cid}", label_visibility="collapsed")
                if st.button("💾", key=f"save_{cid}"):
                    temp_db[cid][0]["title"] = new_t
                    save_db(temp_db)
                    st.session_state.rename_id = None
                    st.rerun()
            else:
                # ANA SOHBET SATIRI
                col_text, col_act = st.columns([0.8, 0.2])
                with col_text:
                    title = temp_db[cid][0].get("title", temp_db[cid][0]["content"][:22] + "...")
                    # Stilize edilmiş şeffaf buton
                    if st.button(f"💬 {title}", key=f"chat_{cid}", use_container_width=True):
                        st.session_state.current_chat_id = cid
                        st.session_state.messages = temp_db[cid]
                        st.rerun()
                
                with col_act:
                    # Küçük ikon menüsü
                    sub_col1, sub_col2 = st.columns(2)
                    with sub_col1:
                        if st.button("✏️", key=f"edit_{cid}", help="Düzenle"):
                            st.session_state.rename_id = cid
                            st.rerun()
                    with sub_col2:
                        if st.button("🗑️", key=f"del_{cid}", help="Sil"):
                            del temp_db[cid]
                            save_db(temp_db)
                            if st.session_state.current_chat_id == cid: st.session_state.messages = []
                            st.rerun()

# ==========================================
# 6. ANA EKRAN
# ==========================================
if not st.session_state.messages:
    st.markdown('<h1 style="text-align:center; color:#1E293B; margin-top:4rem; font-weight:800;">Siber Hukuk Analizi</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#64748B; font-size:1.1rem;">Bilişim vakalarını TCK ve KVKK kapsamında analiz eden uzman asistan.</p>', unsafe_allow_html=True)

for msg in st.session_state.messages:
    av = "👤" if msg["role"] == "user" else "⚖️"
    with st.chat_message(msg["role"], avatar=av):
        st.markdown(msg["content"])

# ==========================================
# 7. SOHBET & SOFT STREAMING
# ==========================================
if p := st.chat_input("Vaka detaylarını veya sorunuzu buraya yazın..."):
    st.session_state.messages.append({"role": "user", "content": p})
    with st.chat_message("user", avatar="👤"):
        st.markdown(p)

    with st.chat_message("assistant", avatar="⚖️"):
        status = st.empty()
        status.markdown('<p style="color:#3B82F6; font-size:0.85rem; font-weight:500;">⚖️ Mevzuat Analiz Ediliyor...</p>', unsafe_allow_html=True)
        
        try:
            res = st.session_state.chat_session.send_message(p, stream=True)
            status.empty()
            full_res = ""
            placeholder = st.empty()
            
            for chunk in res:
                full_res += chunk.text
                placeholder.markdown(full_res + "▌")
                time.sleep(0.01)
            
            placeholder.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            db[st.session_state.current_chat_id] = st.session_state.messages
            save_db(db)
            
        except Exception as e:
            status.empty()
            st.error("Analiz sırasında bir kısıtlamaya takıldık. Lütfen kısa süre sonra tekrar deneyin.")
