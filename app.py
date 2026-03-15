import streamlit as st
import google.generativeai as genai

st.title("🔍 Google API Model Tarayıcı")

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    
    st.success("API Anahtarı başarıyla bağlandı! Google sunucularındaki modeller taranıyor...")
    
    # Senin API anahtarının yetkisi olan tüm modelleri listele
    calisan_modeller = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            calisan_modeller.append(m.name)
            
    st.write("✅ **Senin API anahtarınla çalışan modellerin tam listesi:**")
    st.write(calisan_modeller)

except Exception as e:
    st.error(f"TARAMA HATASI: {str(e)}")
