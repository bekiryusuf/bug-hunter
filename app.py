import streamlit as st
import requests

# 1. Güvenlik Başlıkları Kontrolü
def check_headers(url):
    try:
        if not url.startswith("http"): url = "https://" + url
        response = requests.get(url, timeout=5)
        headers = response.headers
        required = [
            'Content-Security-Policy', 'X-XSS-Protection', 'X-Content-Type-Options',
            'X-Frame-Options', 'Strict-Transport-Security'
        ]
        return [h for h in required if h not in headers]
    except Exception as e:
        return [f"Bağlantı Hatası: {e}"]

# 2. Gelişmiş Dizin Avcısı (İçerik Karşılaştırmalı)
def scan_directories(url):
    common_files = ["/admin", "/.env", "/config", "/.git", "/backup", "/wp-admin", "/uploads"]
    found = []
    base_url = url if url.startswith("http") else "https://" + url
    
    # Ana sayfa içeriğini al (Yanlış alarmı engellemek için)
    try:
        home_content = requests.get(base_url, timeout=3).text
    except:
        home_content = ""

    for path in common_files:
        try:
            full_url = base_url + path
            response = requests.get(full_url, timeout=2)
            
            # İçerik ana sayfadan farklıysa ve 200 OK ise, bu gerçek bir bulgudur
            if response.status_code == 200 and response.text != home_content:
                found.append(f"❌ KRİTİK: {full_url} (Erişilebilir - Gerçek İçerik Tespit Edildi!)")
            elif response.status_code == 403:
                found.append(f"⚠️ Kısıtlı: {full_url} (Dizin mevcut)")
        except:
            continue
    return found

# Arayüz
st.set_page_config(page_title="BugHunter AI", page_icon="🛡️")
st.title("🛡️ BugHunter AI - Profesyonel Tarayıcı")
target = st.text_input("Taranacak Site (Örn: example.com):")

if st.button("🚀 Taramayı Başlat"):
    if target:
        with st.spinner('Derin analiz yapılıyor...'):
            # 1. Başlık Analizi
            st.write("#### 🛡️ Güvenlik Başlıkları")
            missing = check_headers(target)
            if not missing:
                st.success("Tüm güvenlik başlıkları yerinde!")
            else:
                for m in missing:
                    st.error(f"❌ Eksik: {m}")
            
            # 2. Dizin Analizi
            st.write("#### 🔍 Dizin ve Dosya Analizi")
            risks = scan_directories(target)
            if not risks:
                st.info("Kritik dizin ifşası bulunamadı.")
            else:
                for r in risks:
                    st.warning(r)
    else:
        st.warning("Lütfen bir URL girin!")
