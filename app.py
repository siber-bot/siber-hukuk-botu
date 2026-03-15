import streamlit as st
import google.generativeai as genai

# 1. API Ayarları (Secrets'dan çeker)
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash') # En hızlı ve güncel ücretsiz model

# 2. Sayfa Konfigürasyonu (Tasarım Ayarları)
st.set_page_config(
    page_title="Siber Hukuk Asistanı", 
    page_icon="⚖️", 
    layout="centered"
)

# --- TASARIM: Sidebar (Yan Menü) ---
with st.sidebar:
    st.title("🛡️ Proje Künyesi")
    st.markdown("""
    **Siber Hukuk Asistanı v2.0**
    
    Bu yapay zeka prototipi, siber vakaların hukuki ve teknik analizini yapmak üzere tasarlanmıştır.
    
    **Geliştiriciler:**
    * Merve Havuz
    
    ---
    **⚠️ YASAL UYARI:**
    Bu asistan bir avukat değildir. Sunulan bilgiler bilgilendirme amaçlıdır ve resmi bir tavsiye niteliği taşımaz.
    """)
    st.divider()
    st.write("📌 *Hukuki süreçlerde mutlaka bir avukata danışınız.*")

# --- ANA SAYFA TASARIMI ---
st.title("Siber Hukuk Ajanı ⚖️")
st.subheader("Bilişim Suçları ve KVKK Analiz Sistemi")
st.info("Aşağıdaki kutucuğa siber hukukla ilgili bir soru yazabilir veya başınızdan geçen bir vakayı anlatabilirsiniz.")

# Mesaj Geçmişini Başlat (Hafıza için)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Eski mesajları ekrana bas
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- SOHBET VE ZEKÂ MANTIĞI ---
if prompt := st.chat_input("Hukuki sorunuzu buraya yazın..."):
    # Kullanıcı mesajını ekrana bas ve hafızaya al
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # SİSTEM TALİMATI: Gemini'ye nasıl davranması gerektiğini söylüyoruz
    sistem_mesaji = f"""
    Sen uzman bir Siber Hukuk Asistanısın. Cevaplarını şu kurallara göre ver:
    1. FORMAT: Olay Analizi, Hukuki Risk ve Teknik Çözüm adımlarıyla cevapla.
    2. KISALIK: Cevapları %40 oranında kısalt, öz bilgi ver. Uzun cümlelerden kaçın.
    3. TÜRKİYE ODAKLI: USOM, BTK, KVKK Kurumu ve TCK maddelerine (m. 243, 244 vb.) atıf yap.
    4. TON: Profesyonel, ciddi ve yol gösterici ol.
    5. TEKRAR: Her mesajda 'avukat değilim' deme (sidebar'da zaten yazıyor).
    
    Kullanıcı Sorusu: {prompt}
    """

    with st.chat_message("assistant"):
        with st.spinner("Analiz ediliyor..."):
            try:
                response = model.generate_content(sistem_mesaji)
                full_response = response.text
                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error("Bir hata oluştu. Lütfen tekrar deneyin.")

# Alt Bilgi (Footer)
st.markdown("---")
st.caption("© 2026 Siber Hukuk AI Projesi | Streamlit & Gemini Cloud")
