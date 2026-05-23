import streamlit as st
import requests
from difflib import SequenceMatcher

# 1. Profesyonel Başlık Analizi
def check_headers(url):
    results = {}
    try:
        # Protokolü düzelt
        if not url.startswith("http"): url = "https://" + url
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        
        required = ['Content-Security-Policy', 'X-XSS-Protection', 'X-Content-Type-Options', 'X-Frame-Options']
        for h in required:
            results[h] = h in response.headers
        return results, None
    except Exception as e:
        return None, str(e)

# 2. Hata Ayıklamalı Dizin Tarayıcı
def scan_directories(url):
    # Eğer http yoksa ekle
    base_url = url if url.startswith("http") else "https://" + url
    common_files = ["/admin", "/.env", "/config", "/.git", "/backup", "/wp-admin", "/uploads"]
    
    found = []
    try:
        # Ana sayfa referansını al
        resp_home = requests.get(base_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        home_text = resp_home.text
    except Exception as e:
        return [f"Bağlantı Hatası: {e}"]

    for path in common_files:
        try:
            target_url = base_url.rstrip('/') + path
            resp = requests.get(target_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=3)
            
            # Benzerlik analizi (0.9'dan düşükse içerik farklıdır)
            sim = SequenceMatcher(None, home_text, resp.text).ratio()
            
            if resp.status_code == 200 and sim < 0.9:
                found.append(f"❌ KRİTİK: {target_url} (İçerik Farklı!)")
            elif resp.status_code == 403:
                found.append(f"⚠️ Kısıtlı: {target_url} (Erişim Engelli)")
        except:
            continue
    return found

# Arayüz
st.title("🛡️ BugHunter AI - Debug Mod")
target = st.text_input("Taranacak Site (Örn: google.com):")

if st.button("🚀 Taramayı Başlat"):
    if not target:
        st.error("Lütfen bir site gir!")
    else:
        # 1. Başlık Kontrolü
        headers, err = check_headers(target)
        if err:
            st.error(f"SİTEYE ULAŞILAMADI: {err}")
        else:
            st.write("#### 🛡️ Güvenlik Başlıkları")
            for h, status in headers.items():
                if status: st.success(f"✅ {h} Bulundu")
                else: st.error(f"❌ {h} Eksik")

        # 2. Dizin Kontrolü
        st.write("#### 🔍 Dizin Analizi")
        risks = scan_directories(target)
        for r in risks:
            st.warning(r)
