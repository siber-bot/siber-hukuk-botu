import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. SAYFA AYARLARI (EN BAŞTA OLMALI)
# ==========================================
st.set_page_config(
    page_title="Siber Hukuk Asistanı",
    page_icon="⚖️",
    layout="centered", # Okumayı kolaylaştırmak için ortalandı
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. AYDINLIK VE KURUMSAL (LIGHT MODE) CSS TASARIMI
# ==========================================
st.markdown("""
<style>
/* Ana Arkaplan (Ferah Açık Gri/Beyaz) */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { 
    background-color: #F8FAFC !important; 
    color: #1E293B !important; 
}

/* Sağ üstteki gereksiz menüyü gizle */
[data-testid="stToolbar"] { display: none !important; } 

/* YAN MENÜ (Sidebar) Tasarımı (Tam Beyaz) */
[data-testid="stSidebar"] { 
    background-color: #FFFFFF !important; 
    border-right: 1px solid #E2E8F0 !important; 
}

/* ORTALAMA VE EKRAN DÜZENİ */
.block-container {
    max-width: 800px !important;
    padding-top: 2rem !important;
    padding-bottom: 7rem !important;
    margin: 0 auto !important;
}

/* KURUMSAL BAŞLIK TASARIMI */
.legal-title {
    text-align: center;
    font-size: 2.8rem;
    font-weight: 800;
    color: #0F172A;
    margin-bottom: 0.2rem;
    letter-spacing: -0.5px;
}
.legal-subtitle {
    text-align: center; 
    color: #64748B; 
    font-size: 1.1rem; 
    margin-bottom: 3rem; 
}

/* MESAJ BALONLARI (Ferah ve Okunaklı) */
[data-testid="stChatMessage"] {
    background-color: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin-bottom: 20px !important;
}

/* Kullanıcı Mesajı (Açık Mavi Tonu, Sağa Dayalı Hissi) */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown {
    background-color: #EFF6FF !important; 
    color: #0F172A !important;
    border: 1px solid #BFDBFE !important;
    border-radius: 12px 12px 0 12px !important;
    padding: 15px 20px !important;
    display: inline-block !important;
}

/* AI Mesajı (Tam Beyaz, Hafif Gölgeli, Resmi Hissiyat) */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown {
    background-color: #FFFFFF !important; 
    color: #1E293B !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px 12px 12px 0 !important;
    padding: 15px 20px !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
    display: inline-block !important;
}

/* CHAT GİRİŞ KUTUSU (Temiz ve Belirgin) */
[data-testid="stChatFloatingInputContainer"], [data-testid="stBottom"] { 
    background-color: transparent !important; 
}
[data-testid="stChatInput"] { 
    background-color: #FFFFFF !important; 
    border: 1px solid #CBD5E1 !important; 
    border-radius: 12px !important; 
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
}
[data-testid="stChatInput"]:focus-within { 
    border-color: #3B82F6 !important; 
}
textarea { color: #0F172A !important; }

/* BİLGİ KUTULARI (Sol Menü İçin) */
.info-box {
    background: #F1F5F9; padding: 12px; border-radius: 8px; 
    border-left: 3px solid #3B82F6; font-size: 0.85rem; margin-bottom: 10px; color: #334155;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. API VE GEMINI 3 FLASH MODELİ
# ==========================================
SISTEM_PROMPTU = """Sen uzman bir Siber Hukuk Asistanısın.
Görevin siber vakaları (KVKK ihlalleri, dolandırıcılık, hesap çalınması) TCK mevzuatına göre analiz etmektir.
Yanıtlarını çok resmi, net, madde işaretli ve tamamen Türkiye yasalarına dayandırarak ver.
Kullanıcıya avukat olmadığını ve bilginin tavsiye niteliğinde olduğunu hissettir."""

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    # Model Gemini 3 Flash olarak güncellendi!
    model = genai.GenerativeModel('gemini-3.0-flash') 
except Exception as e:
    st.error("⚠️ API Anahtarı eksik veya model yüklenemedi. Secrets ayarlarını kontrol edin.")
    st.stop()

# ==========================================
# 4. HAFIZA VE OTURUM
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# ==========================================
# 5. YAN MENÜ (SOL PANEL)
# ==========================================
with st.sidebar:
    st.markdown("## ⚖️ Siber Hukuk Asistanı")
    st.markdown("<span style='color: #64748B; font-size: 0.9rem;'>Sürüm 5.0 (Light)</span>", unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("""
    <div class='info-box'>
    <b>Proje Geliştiricileri:</b><br>
    👤 Merve [Soyadı]<br>
    👤 [Senin Adın]
    </div>
    <div class='info-box' style='border-left-color: #10B981;'>
    <b>Aktif Model:</b> Gemini 3 Flash<br>
    <b>Veritabanı:</b> TCK & KVKK
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    if st.button("🔄 Yeni Analiz Başlat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_session = model.start_chat(history=[])
        st.rerun()
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.warning("⚠️ Bu sistem sadece bilgilendirme amaçlıdır. Resmi hukuki danışmanlık yerine geçmez.")

# ==========================================
# 6. ANA EKRAN VE SOHBET (DİNAMİK)
# ==========================================

# Sadece sohbet boşken ana başlığı göster
if len(st.session_state.messages) == 0:
    st.markdown('<div class="legal-title">Siber Hukuk Asistanı</div>', unsafe_allow_html=True)
    st.markdown('<div class="legal-subtitle">Bilişim Suçları ve Veri İhlali Danışma Merkezi</div>', unsafe_allow_html=True)

# Mesajları Ekrana Çiz
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "⚖️"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ==========================================
# 7. SOHBET MANTIĞI VE API İSTEĞİ
# ==========================================
if prompt := st.chat_input("Hukuki bir soru sorun veya vakayı anlatın..."):
    
    # Kullanıcı mesajını ekle
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # AI Yanıtı
    with st.chat_message("assistant", avatar="⚖️"):
        with st.spinner("Hukuki analiz yapılıyor..."):
            try:
                # Modeli çökertmeden gizli sistem promptunu soruya entegre ediyoruz
                tam_prompt = f"GİZLİ SİSTEM KOMUTU: {SISTEM_PROMPTU}\n\nKULLANICI VAKASI/SORUSU: {prompt}"
                
                response = st.session_state.chat_session.send_message(tam_prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error("Sunucularımızda anlık bir yoğunluk yaşanıyor. Lütfen sayfayı yenileyip tekrar deneyin.")
