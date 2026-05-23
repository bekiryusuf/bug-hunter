import streamlit as st
import requests
from difflib import SequenceMatcher

# 1. Başlık Analizi - Profesyonel Standart
def check_headers(url):
    try:
        if not url.startswith("http"): url = "https://" + url
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=5)
        required = ['Content-Security-Policy', 'X-XSS-Protection', 'X-Content-Type-Options', 'X-Frame-Options']
        return [h for h in required if h not in response.headers]
    except Exception as e:
        return [f"Bağlantı Hatası: {e}"]

# 2. Gelişmiş Tarama - Benzerlik Analizi ile
def scan_directories(url):
    common_files = ["/admin", "/.env", "/config", "/.git", "/backup", "/wp-admin", "/uploads"]
    found = []
    base_url = url if url.startswith("http") else "https://" + url
    
    try:
        # Ana sayfa içeriğini referans al
        home_resp = requests.get(base_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=3)
        home_content = home_resp.text
    except:
        return ["Hata: Siteye ulaşılamadı."]

    for path in common_files:
        full_url = base_url + path
        try:
            resp = requests.get(full_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=2)
            
            # İçerik benzerlik oranı hesapla
            similarity = SequenceMatcher(None, home_content, resp.text).ratio()
            
            # Eğer sayfa 200 dönüyor ve ana sayfadan %90 farklıysa, bu şüphelidir!
            if resp.status_code == 200 and similarity < 0.9:
                found.append(f"❌ KRİTİK: {full_url} (Erişilebilir - Gerçek İçerik Tespit Edildi!)")
            elif resp.status_code == 403:
                found.append(f"⚠️ Kısıtlı: {full_url} (Dizin mevcut)")
        except:
            continue
    return found

# Streamlit UI
st.set_page_config(page_title="BugHunter Pro", page_icon="🛡️")
st.title("🛡️ BugHunter AI - Profesyonel")
target = st.text_input("Taranacak Site (Örn: example.com):")

if st.button("🚀 Derin Taramayı Başlat"):
    with st.spinner('Analiz ediliyor...'):
        missing = check_headers(target)
        # ... [UI kodları buraya devam edecek]
