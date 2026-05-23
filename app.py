import streamlit as st
import requests

# Güvenlik Başlıklarını Kontrol Eden Fonksiyon
def check_headers(url):
    try:
        response = requests.get(url, timeout=5)
        headers = response.headers
        missing = []
        # Kontrol edilecek başlıklar listesi
        required_headers = [
            'Content-Security-Policy', 'X-XSS-Protection', 'X-Content-Type-Options',
            'X-Frame-Options', 'Strict-Transport-Security'
        ]
        for header in required_headers:
            if header not in headers:
                missing.append(header)
        return missing
    except Exception as e:
        return [str(e)]

# Yeni Dizin Avcısı Fonksiyonu
def scan_directories(url):
    common_files = ["/admin", "/.env", "/config", "/.git", "/backup", "/wp-admin", "/uploads"]
    found = []
    base_url = url if url.startswith("http") else "https://" + url
    
    for path in common_files:
        try:
            full_url = base_url + path
            response = requests.get(full_url, timeout=2)
            if response.status_code == 200:
                found.append(f"❌ KRİTİK: {full_url} (Erişilebilir!)")
            elif response.status_code == 403:
                found.append(f"⚠️ Kısıtlı: {full_url} (Dizin mevcut)")
        except:
            continue
    return found

# Streamlit Arayüzü
st.title("🛡️ BugHunter AI - Siber Güvenlik Laboratuvarı")
target = st.text_input("Taranacak Site (Örn: example.com):")

if st.button("🚀 Taramayı Başlat"):
    if target:
        st.write(f"### {target} taranıyor...")
        
        # 1. Başlık Taraması
        missing_headers = check_headers("https://" + target)
        st.write("#### 🛡️ Güvenlik Başlıkları Analizi")
        if not missing_headers:
            st.success("Tüm güvenlik başlıkları yerinde!")
        else:
            for m in missing_headers:
                st.error(f"❌ Eksik: {m}")
        
        # 2. Dizin Taraması (Yeni Modül)
        st.write("#### 🔍 Dizin ve Dosya Analizi")
        risks = scan_directories(target)
        if not risks:
            st.info("Kritik dizin ifşası bulunamadı.")
        else:
            for r in risks:
                st.warning(r)
    else:
        st.warning("Lütfen bir URL girin!")
