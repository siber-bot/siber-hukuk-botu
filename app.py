import streamlit as st
import google.generativeai as genai
import time

# ==========================================
# 1. SAYFA AYARLARI
# ==========================================
st.set_page_config(
    page_title="Siber Hukuk Asistanı",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="expanded" # Menüyü zorla açık başlatır
)

# ==========================================
# 2. AYDINLIK, KURUMSAL VE ZORLAYICI CSS
# ==========================================
st.markdown("""
<style>
/* Ana Arkaplan */
.stApp { background-color: #F8FAFC !important; }

/* SOL MENÜYÜ GÖRÜNÜR KILAN ÖZEL AYARLAR */
[data-testid="stSidebar"] { 
    background-color: #FFFFFF !important; 
    border-right: 1px solid #E2E8F0 !important; 
    visibility: visible !important;
}

/* Menü açma butonunu zorla göster (Eğer kapalıysa) */
[data-testid="stSidebarNav"] { visibility: visible !important; }

/* Üst barı şeffaf yap ama menü butonunu gizleme */
[data-testid="stHeader"] { background: rgba(248, 250, 252, 0.8) !important; backdrop-filter: blur(5px); }
[data-testid="stToolbar"] { display: none !important; } 

/* İçerik Genişliği */
.block-container { max-width: 800px !important; padding-top: 1rem !important; }

/* Başlıklar */
.legal-title { text-align: center; font-size: 2.5rem; font-weight: 800; color: #0F172A; margin-bottom: 0px; }
.legal-subtitle { text-align: center; color: #64748B; font-size: 1rem; margin-bottom: 2rem; }

/* Mesaj Balonları */
[data-testid="stChatMessage"] { margin-bottom: 15px !important; }
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown { 
    background-color: #EFF6FF !important; 
    border: 1px solid #BFDBFE !important; 
    border-radius: 12px 12px 0 12px !important; 
    padding: 12px 18px !important; 
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown { 
    background-color: #FFFFFF !important; 
    border: 1px solid #E2E8F0 !important; 
    border-radius: 12px 12px 12px 0 !important; 
    padding: 12px 18px !important; 
    box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important; 
}

/* Sol Menü Bilgi Kutuları */
.info-box { background: #F1F5F9; padding: 12px; border-radius: 8px; border-left: 3px solid #3B82F6; font-size: 0.85rem; margin-bottom: 10px; color: #334155; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. KORUNAN API VE MODEL AYARLARI
# ==========================================
SISTEM_PROMPTU = """Sen uzman bir Siber Hukuk Asistanısın. Yanıtlarını resmi, net ve Türkiye yasalarına dayandırarak ver."""

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-3-flash-preview') 
except Exception as e:
    st.error(f"Sistem Başlatılamadı: {str(e)}")
    st.stop()

# ==========================================
# 4. HAFIZA YÖNETİMİ
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# ==========================================
# 5. YAN MENÜ (SOL PANEL)
# ==========================================
# sidebar fonksiyonu içinde her şeyin olduğundan emin oluyoruz
with st.sidebar:
    st.markdown("## ⚖️ Siber Hukuk Asistanı")
    st.divider()
    
    st.markdown("""
    <div class='info-box'>
    <b>Proje Geliştiricileri:</b><br>
    👤 Merve [Soyadı]<br>
    👤 [Senin Adın]
    </div>
    <div class='info-box' style='border-left-color: #10B981;'>
    <b>Model:</b> Gemini 3 Flash<br>
    <b>Durum:</b> Çevrimiçi
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Yeni Analiz Başlat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_session = model.start_chat(history=[])
        st.rerun()

# ==========================================
# 6. ANA EKRAN
# ==========================================
if len(st.session_state.messages) == 0:
    st.markdown('<div class="legal-title">Siber Hukuk Asistanı</div>', unsafe_allow_html=True)
    st.markdown('<div class="legal-subtitle">Bilişim Suçları ve Veri İhlali Danışma Merkezi</div>', unsafe_allow_html=True)

for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "⚖️"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ==========================================
# 7. SOHBET VE ANİMASYONLU YAZIM
# ==========================================
if prompt := st.chat_input("Hukuki bir soru sorun..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚖️"):
        # Sen istediğin için "Analiz ediliyor..." yazısı geri geldi
        with st.status("🔍 Hukuki analiz yapılıyor...", expanded=True) as status:
            try:
                tam_prompt = f"SİSTEM: {SISTEM_PROMPTU}\n\nSORU: {prompt}"
                response = st.session_state.chat_session.send_message(tam_prompt, stream=True)
                
                # Önce bir placeholder oluşturuyoruz ki yazı oraya aksın
                message_placeholder = st.empty()
                full_response = ""
                
                for chunk in response:
                    full_response += chunk.text
                    # Kelime kelime yazma animasyonu (Soft geçiş)
                    message_placeholder.markdown(full_response + "▌")
                    time.sleep(0.01)
                
                message_placeholder.markdown(full_response)
                # İşlem bitince durumu güncelle
                status.update(label="✅ Analiz Tamamlandı", state="complete", expanded=False)
                
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                status.update(label="🚨 Hata Oluştu", state="error")
                st.error(f"Detay: {str(e)}")
