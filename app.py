import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. SAYFA AYARLARI (EN BAŞTA OLMALI)
# ==========================================
st.set_page_config(
    page_title="Siber Hukuk AI",
    page_icon="🤖",
    layout="wide", # Geniş ve ferah AI ekranı
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. CYBER-AI KONSEPTLİ CSS TASARIMI
# ==========================================
st.markdown("""
<style>
/* Ana Arkaplan (Koyu Siber Uzay Rengi) */
.stApp { background-color: #0A0E17 !important; color: #E2E8F0 !important; }

/* HEADER DÜZELTMESİ: Menü tuşu kalsın ama arka planı şeffaf olsun */
[data-testid="stHeader"] { background-color: transparent !important; }
[data-testid="stToolbar"] { display: none !important; } /* Sağ üstteki gereksiz menüyü gizle */

/* YAN MENÜ (Sidebar) Tasarımı */
[data-testid="stSidebar"] { background-color: #111827 !important; border-right: 1px solid #1E293B !important; }

/* ORTALAMA VE EKRAN DÜZENİ */
.block-container {
    max-width: 900px !important;
    padding-top: 2rem !important;
    padding-bottom: 7rem !important;
    margin: 0 auto !important;
}

/* SİBER BAŞLIK TASARIMI (Neon Geçişli) */
.cyber-title {
    text-align: center;
    font-size: 3.2rem;
    font-weight: 900;
    background: linear-gradient(90deg, #00F0FF, #5773FF, #BC13FE);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
    letter-spacing: -1px;
}
.cyber-subtitle {
    text-align: center; color: #94A3B8; font-size: 1.1rem; margin-bottom: 3rem; letter-spacing: 1px;
}

/* MESAJ BALONLARI (Holografik AI Hissi) */
[data-testid="stChatMessage"] {
    background-color: transparent !important;
    border: 1px solid #1E293B !important;
    border-radius: 12px;
    margin-bottom: 15px;
    padding: 15px;
}
/* Kullanıcı Mesajı */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background-color: #1E293B !important; 
    border-color: #334155 !important; 
}
/* AI Mesajı (Neon Mavi Çizgili) */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background-color: #0F172A !important; 
    border-left: 3px solid #00F0FF !important; 
}

/* CHAT GİRİŞ KUTUSU */
[data-testid="stChatFloatingInputContainer"], [data-testid="stBottom"] { background-color: transparent !important; }
[data-testid="stChatInput"] { 
    background-color: #1E293B !important; 
    border: 1px solid #334155 !important; 
    border-radius: 16px !important; 
}
[data-testid="stChatInput"]:focus-within { 
    border-color: #00F0FF !important; 
    box-shadow: 0 0 15px rgba(0, 240, 255, 0.2) !important; 
}
textarea { color: #F8FAFC !important; }

/* SİSTEM DURUM KUTULARI (Sol Menü İçin) */
.status-box {
    background: #1E293B; padding: 12px; border-radius: 8px; 
    border-left: 3px solid #10B981; font-size: 0.85rem; margin-bottom: 10px; color: #E2E8F0;
}
.warning-box {
    background: #450A0A; padding: 12px; border-radius: 8px; 
    border-left: 3px solid #EF4444; font-size: 0.8rem; color: #FCA5A5;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. API VE MODEL (404 Hatası Çözüldü)
# ==========================================
SISTEM_PROMPTU = """Sen bir Siber Hukuk ve Yapay Zeka Ajanısın.
Görevin siber zorbalık, KVKK ihlalleri, hacklenme ve dijital dolandırıcılık vakalarını TCK mevzuatına göre analiz etmektir.
Yanıtlarını profesyonel, siber güvenlik terminolojisine uygun ve madde işaretli ver.
Doğrudan bilgi sun, gereksiz cümle kurma. Atılması gereken adımları (USOM, Savcılık, BTK) net olarak belirt."""

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    # 404 hatasını çözen garantili model isimlendirmesi:
    model = genai.GenerativeModel('gemini-1.5-flash-latest') 
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
# 5. YAN MENÜ (SİBER KONTROL PANELİ)
# ==========================================
with st.sidebar:
    st.markdown("## 🤖 SİBER KONTROL PANELİ")
    
    # AI Konseptli Durum Göstergeleri
    st.markdown("""
    <div class='status-box'>
    🟢 <b>Sistem:</b> Çevrimiçi<br>
    ⚡ <b>Yapay Zeka:</b> Aktif<br>
    📚 <b>Veritabanı:</b> TCK & KVKK Entegre
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("### 👨‍💻 Geliştirici Ekip")
    st.caption("Merve & [Adın] | Sürüm 4.0")
    
    st.divider()
    
    if st.button("🔄 Hafızayı Temizle / Reset", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_session = model.start_chat(history=[])
        st.rerun()
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='warning-box'>⚠️ <b>Yasal Uyarı:</b> Bu sistem yapay zeka tabanlı bir asistandır. Resmi avukat danışmanlığı yerine geçmez.</div>", unsafe_allow_html=True)

# ==========================================
# 6. ANA EKRAN VE SOHBET (DİNAMİK)
# ==========================================

# Sadece sohbet boşken siber başlığı göster
if len(st.session_state.messages) == 0:
    st.markdown('<div class="cyber-title">SİBER HUKUK AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="cyber-subtitle">Bilişim Suçları ve Veri İhlali Erken Uyarı Sistemi</div>', unsafe_allow_html=True)

# Mesajları Ekrana Çiz
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ==========================================
# 7. SOHBET MANTIĞI VE API İSTEĞİ
# ==========================================
if prompt := st.chat_input("Vakayı analiz et veya hukuki bir soru sor..."):
    
    # Kullanıcı mesajını ekle
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # AI Yanıtı
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Siber veritabanı taranıyor..."):
            try:
                # Modeli çökertmeden gizli sistem promptunu soruya entegre ediyoruz
                tam_prompt = f"GİZLİ SİSTEM KOMUTU: {SISTEM_PROMPTU}\n\nKULLANICI VAKASI/SORUSU: {prompt}"
                
                response = st.session_state.chat_session.send_message(tam_prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Sistem Hatası: {str(e)}")
