import streamlit as st
import google.generativeai as genai

# 1. BÖLÜM: BEYNİ BAĞLAMA
# Kopyaladığın o uzun API Key'i aşağıdaki tırnak işaretlerinin içine yapıştır.
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-3-flash-preview')

# 2. BÖLÜM: WEB SİTESİNİN GÖRÜNÜMÜ
st.set_page_config(page_title="Siber Hukuk Asistanı", page_icon="⚖️")
st.title("Siber Hukuk Ajanı ⚖️")
st.markdown("Merhaba! Siber güvenlik hukuku, KVKK ve yapay zeka etiği hakkında sorularınızı sorabilirsiniz.")

# Geçmiş mesajları hatırlama hafızası
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. BÖLÜM: SOHBET KISMI
if prompt := st.chat_input("Hukuki sorunuzu buraya yazın..."):
    # Senin yazdığın mesajı ekrana basar
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Ajanın arka plandaki kuralları (Sistemi hukukta tutmak için)
    sistem_kurallari = "Sen uzman bir siber hukuk asistanısın. Sadece hukuk ve siber güvenlik sorularına cevap ver. Avukat olmadığını belirt. Açıklamalarını akademik ama anlaşılır yap. Kullanıcının sorusu şu: "
    
    # Yapay zekadan cevap isteme
    with st.chat_message("assistant"):
        cevap = model.generate_content(sistem_kurallari + prompt)
        st.markdown(cevap.text)
    st.session_state.messages.append({"role": "assistant", "content": cevap.text})