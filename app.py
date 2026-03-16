import streamlit as st
import streamlit.components.v1 as components
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
# 3. ÖZEL CSS (GÖRÜNMEZLİK TAKTİĞİ EKLENDİ)
# ==========================================
st.markdown("""
<style>
    /* Toolbar gizle */
    [data-testid="stToolbar"] { display: none !important; }

    /* Streamlit'in kendi butonlarını SİLME, JS'in tıklayabilmesi için GÖRÜNMEZ YAP */
    button[data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"] {
        opacity: 0 !important;
        position: absolute !important;
        top: -9999px !important;
        left: -9999px !important;
        pointer-events: none !important;
        z-index: -1 !important;
    }

    /* HEADER şeffaf */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* ANA KONTEYNER */
    .block-container { 
        padding-top: 3.5rem !important; 
        max-width: 850px !important; 
        margin: 0 auto !important; 
    }

    /* SİDEBAR STİL */
    [data-testid="stSidebar"] { 
        background-color: #F8FAFC !important; 
        border-right: 1px solid #E2E8F0 !important;
        z-index: 1000000 !important;
    }

    /* BAŞLIK */
    .portal-title {
        text-align: center;
        font-weight: 800;
        font-size: 2.2rem;
        color: #0F172A;
        margin-top: 1rem;
    }

    /* SOHBET LİSTESİ BUTONLARI */
    div[data-testid="stVerticalBlock"] div.stButton > button {
        text-align: left !important;
        width: 100% !important;
        border: none !important;
        background: transparent !important;
        padding: 8px 12px !important;
        border-radius: 10px !important;
        color: #475569 !important;
        transition: all 0.2s !important;
    }
    div[data-testid="stVerticalBlock"] div.stButton > button:hover {
        background-color: #F1F5F9 !important;
        color: #1E293B !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. KALICI FLOATING MENU BUTONU (KESİN ÇÖZÜM)
# ==========================================
components.html("""
<script>
    const parentDoc = window.parent.document;
    
    if (!parentDoc.getElementById('cyber-menu-btn')) {
        const btn = parentDoc.createElement('button');
        btn.id = 'cyber-menu-btn';
        btn.innerHTML = '<svg viewBox="0 0 24 24" width="22" height="22" fill="white"><path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/></svg>';
        
        Object.assign(btn.style, {
            position: 'fixed',
            top: '14px',
            left: '14px',
            zIndex: '9999999',
            width: '44px',
            height: '44px',
            backgroundColor: '#3B82F6',
            border: 'none',
            borderRadius: '12px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 14px rgba(59,130,246,0.5)',
            transition: 'all 0.2s ease'
        });

        btn.onmouseover = () => { btn.style.backgroundColor = '#2563EB'; btn.style.transform = 'scale(1.08)'; };
        btn.onmouseout = () => { btn.style.backgroundColor = '#3B82F6'; btn.style.transform = 'scale(1)'; };

        btn.onclick = () => {
            const sidebar = parentDoc.querySelector('[data-testid="stSidebar"]');
            const isExpanded = sidebar && sidebar.getAttribute('aria-expanded') === 'true';

            if (isExpanded) {
                // Sidebar açıksa kapatma butonunu bul ve tıkla
                const closeBtn = parentDoc.querySelector('[data-testid="stSidebarCollapseButton"]');
                if (closeBtn) closeBtn.click();
            } else {
                // Sidebar kapalıysa açma butonunu bul ve tıkla
                const openContainer = parentDoc.querySelector('[data-testid="collapsedControl"]');
                if (openContainer) {
                    const openBtn = openContainer.querySelector('button') || openContainer;
                    openBtn.click();
                }
            }
        };
        parentDoc.body.appendChild(btn);
    }
</script>
""", height=0)

# ==========================================
# 5. API VE MODEL
# ==========================================
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-3-flash') 
except:
    st.error("API Secret Hatası! Lütfen Streamlit ayarlarını kontrol edin.")
    st.stop()

# ==========================================
# 6. DATA & SESSION STATE
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
# 7. SOL MENÜ (SİDEBAR) İÇERİĞİ
# ==========================================
with st.sidebar:
    st.markdown("<h3 style='color:#0F172A; margin-top:20px;'>⚖️ Siber Asistan</h3>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.85rem; color:#3B82F6; font-style:italic; margin-bottom:20px;'>Dijital dünyada adaletin rehberi.</p>", unsafe_allow_html=True)
    
    st.markdown("<p style='font-size:0.7rem; color:#94A3B8; font-weight:700; margin-bottom:5px;'>PROJE SAHİBİ</p>", unsafe_allow_html=True)
    st.markdown("👤 **Merve [Soyadı]**")
    
    st.divider()
    
    if st.button("➕ Yeni Analiz Başlat", type="primary", use_container_width=True):
        st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.messages = []
        st.session_state.chat_session = model.start_chat(history=[])
        st.rerun()

    st.markdown("<p style='font-size:0.7rem; color:#94A3B8; font-weight:700; margin-top:20px; margin-bottom:10px;'>GEÇMİŞ ANALİZLER</p>", unsafe_allow_html=True)
    
    t_db = db.copy()
    for cid in sorted(t_db.keys(), reverse=True):
        if st.session_state.edit_id == cid:
            new_val = st.text_input("Düzenle", value=t_db[cid][0].get("title", t_db[cid][0]["content"][:15]), key=f"r_{cid}", label_visibility="collapsed")
            if st.button("💾", key=f"s_{cid}"):
                t_db[cid][0]["title"] = new_val
                save_db(t_db)
                st.session_state.edit_id = None
                st.rerun()
        else:
            c1, c2, c3 = st.columns([0.70, 0.15, 0.15])
            with c1:
                display_t = t_db[cid][0].get("title", t_db[cid][0]["content"][:18] + "...")
                if st.button(f"💬 {display_t}", key=f"ch_{cid}", use_container_width=True):
                    st.session_state.current_chat_id = cid
                    st.session_state.messages = t_db[cid]
                    st.rerun()
            with c2:
                if st.button("✏️", key=f"e_{cid}"):
                    st.session_state.edit_id = cid
                    st.rerun()
            with c3:
                if st.button("🗑️", key=f"d_{cid}"):
                    del t_db[cid]
                    save_db(t_db)
                    if st.session_state.current_chat_id == cid: 
                        st.session_state.messages = []
                    st.rerun()

# ==========================================
# 8. ANA EKRAN
# ==========================================
if not st.session_state.messages:
    st.markdown('<h1 class="portal-title">Siber Hukuk Portalı</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#64748B;">Hukuki vakayı veya sormak istediğiniz dijital hakları aşağıya yazın.</p>', unsafe_allow_html=True)

for msg in st.session_state.messages:
    av = "👤" if msg["role"] == "user" else "⚖️"
    with st.chat_message(msg["role"], avatar=av):
        st.markdown(msg["content"])

# ==========================================
# 9. SOHBET & ANALİZ SÜRECİ
# ==========================================
if prompt := st.chat_input("Hukuki vakayı yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚖️"):
        try:
            res = st.session_state.chat_session.send_message(prompt, stream=True)
            
            full_res = ""
            message_placeholder = st.empty()
            
            for chunk in res:
                full_res += chunk.text
                message_placeholder.markdown(full_res + "▌")
                time.sleep(0.01) # Soft yazma animasyonu
            
            message_placeholder.markdown(full_res)
            
            if len(st.session_state.messages) == 1:
                st.session_state.messages[0]["title"] = prompt[:25]
                
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            db[st.session_state.current_chat_id] = st.session_state.messages
            save_db(db)
            
        except Exception as e:
            st.error("Model bağlantısında bir hata oluştu.")
