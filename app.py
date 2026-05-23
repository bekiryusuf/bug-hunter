import streamlit as st
import requests
import sqlite3
from datetime import datetime

# --- KATEGORİ TANIMLARI (Genişletilmiş) ---
CATEGORIES = {
    "İçerik ve XSS Güvenliği": [
        'Content-Security-Policy', 'X-XSS-Protection', 'X-Content-Type-Options', 
        'Content-Type', 'X-Download-Options'
    ],
    "Tarayıcı ve Çerçeve Politikaları": [
        'X-Frame-Options', 'Referrer-Policy', 'Permissions-Policy', 
        'Cross-Origin-Opener-Policy', 'Cross-Origin-Embedder-Policy', 'Cross-Origin-Resource-Policy'
    ],
    "İletişim ve Sertifika": [
        'Strict-Transport-Security', 'Expect-CT', 'Public-Key-Pins', 'NEL'
    ],
    "Diğer": [
        'X-Content-Duration', 'X-Powered-By', 'Server', 'X-AspNet-Version'
    ]
}

# --- ARAYÜZ VE AYARLAR ---
st.set_page_config(page_title="BugHunter AI - Ultimate", layout="wide")
st.title("🎯 BugHunter AI - Ultimate Güvenlik Denetimi")

# Sol tarafa genişletilmiş kategorileri ekle
st.sidebar.header("🛡️ Güvenlik Kütüphanesi")
for cat, headers in CATEGORIES.items():
    with st.sidebar.expander(f"📁 {cat} ({len(headers)})"):
        for h in headers:
            st.write(f"• {h}")

def init_db():
    conn = sqlite3.connect('scanner_history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scans 
                 (url TEXT, score INTEGER, date TEXT, missing_count INTEGER)''')
    conn.commit()
    conn.close()

init_db()

def perform_scan(url):
    url = url.strip()
    if not url.startswith('http'): url = 'https://' + url
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/120.0.0.0'}
    
    missing = []
    all_headers = [h for sublist in CATEGORIES.values() for h in sublist]
    
    try:
        resp = requests.get(url, headers=headers, timeout=5, verify=False)
        for h in all_headers:
            if h not in resp.headers:
                missing.append(h)
        # Skor hesaplaması: Toplam header sayısına göre oranla
        score = int(((len(all_headers) - len(missing)) / len(all_headers)) * 100)
        return score, missing
    except:
        return 0, ["Bağlantı Hatası: Siteye erişilemedi."]

# --- ARAYÜZ ---
target_url = st.text_input("🔍 Denetlenecek Web Sitesi:", placeholder="https://orneksite.com")

if st.button("🚀 Kapsamlı Taramayı Başlat"):
    score, missing = perform_scan(target_url)
    
    st.markdown(f"## 🛡️ Güvenlik Skoru: {score} / 100")
    
    for cat, headers in CATEGORIES.items():
        cat_missing = [h for h in headers if h in missing]
        if cat_missing:
            st.error(f"⚠️ {cat} ({len(cat_missing)} eksik):")
            for m in cat_missing:
                st.write(f"❌ {m}")
        else:
            st.success(f"✅ {cat}: Tüm başlıklar mevcut.")

    if missing and "Bağlantı" not in missing[0]:
        st.subheader("💡 Uygulamanız Gereken Kodlar:")
        for m in missing:
            st.code(f"add_header {m} \"[DEĞER_BURAYA]\";", language="bash")

    # Veritabanına kayıt
    conn = sqlite3.connect('scanner_history.db')
    c = conn.cursor()
    c.execute("INSERT INTO scans (url, score, date, missing_count) VALUES (?, ?, ?, ?)", 
              (target_url, score, datetime.now().strftime("%Y-%m-%d %H:%M"), len(missing)))
    conn.commit()
    conn.close()

st.subheader("📋 Geçmiş Taramalar")
conn = sqlite3.connect('scanner_history.db')
c = conn.cursor()
c.execute("SELECT * FROM scans ORDER BY date DESC LIMIT 10")
for row in c.fetchall():
    st.write(f"🌐 **{row[0]}** | 🛡️ Skor: {row[1]} | 📅 {row[2]} | ❌ Eksik: {row[3]}")
conn.close()