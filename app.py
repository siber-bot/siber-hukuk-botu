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
    initial_sidebar_state="expanded" # Sol menünün her zaman açık başlamasını sağlar
)

# ==========================================
# 2. AYDINLIK VE KURUMSAL CSS TASARIMI
# ==========================================
st.markdown("""
<style>
/* Ana Arkaplan */
.stApp, [data-testid="stAppViewContainer"] { background-color: #F8FAFC !important; color: #1E293B !important; }

/* Üst barı şeffaf yap ama menü açma tuşunu GİZLEME! */
[data-testid="stHeader"] { background-color: transparent !important; }
[data-testid="stToolbar"] { display: none !important; } /* Sadece sağ üstteki gereksiz 'Deploy' yazısını gizle */

/* Yan Menü (Sol Menü) */
[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0 !important; }

/* Ortalama ve Boşluklar */
.block-container { max-width: 800px !important; padding-top: 2rem !important; padding-bottom: 7rem !important; margin: 0 auto !important; }

/* Başlıklar */
.legal-title { text-align: center; font-size: 2.8rem; font-weight: 800; color: #0F172A; margin-bottom: 0.2rem; letter-spacing: -0.5px; }
.legal-subtitle { text-align: center; color: #64748B; font-size: 1.1rem; margin-bottom: 3rem; }

/* Mesaj Balonları */
[data-testid="stChatMessage"] { background-color: transparent !important; border: none !important; padding: 0 !important; margin-bottom: 20px !important; }

/* Kullanıcı Mesajı (Açık Mavi, Sağ) */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown { background-color: #EFF6FF !important; color: #0F172A !important; border: 1px solid #BFDBFE !important; border-radius: 12px 12px 0 12px !important; padding: 15px 20px !important; display: inline-block !important; }

/* AI Mesajı (Beyaz, Sol) */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown { background-color: #FFFFFF !important; color: #1E293B !important; border: 1px solid #E2E8F0 !important; border-radius: 12px 12px 12px 0 !important; padding: 15px 20px !important; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important; display: inline-block !important; }

/* Chat Giriş Kutusu */
[data-testid="stChatFloatingInputContainer"], [data-testid="stBottom"] { background-color: transparent !important; }
[data-testid="stChatInput"] { background-color: #FFFFFF !important; border: 1px solid #CBD5E1 !important; border-radius: 12px !important; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important; }
[data-testid="stChatInput"]:focus-within { border-color: #3B82F6 !important; }
textarea { color: #0F172A !important; }

/* Sol Menü Bilgi Kutuları */
.info-box { background: #F1F5F9; padding: 12px; border-radius: 8px; border-left: 3px solid #3B82F6; font-size: 0.85rem; margin-bottom: 10px; color: #334155; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. KORUNAN API VE MODEL AYARLARI (DOKUNULMADI)
# ==========================================
SISTEM_PROMPTU = """Sen uzman bir Siber Hukuk Asistanısın.
Görevin siber vakaları (KVKK ihlalleri, dolandırıcılık, hesap çalınması) TCK mevzuatına göre analiz etmektir.
Yanıtlarını resmi, net, madde işaretli ve tamamen Türkiye yasalarına dayandırarak ver."""

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    
    # Kilitli Motorumuz: Gemini 3 Flash Preview
    model = genai.GenerativeModel('gemini-3-flash-preview') 
except Exception as e:
    st.error(f"Sistem Başlatılamadı! Detay: {str(e)}")
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
with st.sidebar:
    st.markdown("## ⚖️ Siber Hukuk Asistanı")
    st.markdown("<span style='color: #64748B; font-size: 0.9rem;'>Sürüm 7.0 (Soft UI)</span>", unsafe_allow_html=True)
    st.divider()
    
    st.markdown("""
    <div class='info-box'>
    <b>Proje Geliştiricileri:</b><br>
    👤 Merve [Soyadı]<br>
    👤 [Senin Adın]
    </div>
    <div class='info-box' style='border-left-color: #10B981;'>
    <b>Aktif Model:</b> Gemini 3 Flash<br>
    <b>Durum:</b> Çevrimiçi & Hazır
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    
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

# Önceki mesajları ekrana çiz
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "⚖️"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ==========================================
# 7. SOHBET MANTIĞI VE YAZMA ANİMASYONU (STREAMING)
# ==========================================
if prompt := st.chat_input("Hukuki bir soru sorun veya vakayı anlatın..."):
    
    # 1. Kullanıcının mesajını ekle ve göster
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # 2. Asistanın mesajını "Yazma Animasyonu" ile göster
    with st.chat_message("assistant", avatar="⚖️"):
        try:
            tam_prompt = f"GİZLİ SİSTEM KOMUTU: {SISTEM_PROMPTU}\n\nKULLANICI VAKASI/SORUSU: {prompt}"
            
            # stream=True komutu ile yapay zekanın cevabı parça parça göndermesini sağlıyoruz
            response = st.session_state.chat_session.send_message(tam_prompt, stream=True)
            
            # st.write_stream() fonksiyonu bu parçaları alıp daktilo/yazma animasyonuna çevirir
            def stream_data():
                for chunk in response:
                    yield chunk.text
            
            full_response = st.write_stream(stream_data())
            
            # Tamamlanan metni hafızaya kaydet
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            if "429" in str(e):
                st.warning("⚠️ Çok hızlı soru sordunuz. Lütfen birkaç saniye bekleyip tekrar deneyin.")
            else:
                st.error(f"🚨 BEKLENMEYEN HATA: {str(e)}")
