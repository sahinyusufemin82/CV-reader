import pdfplumber
import google.generativeai as genai
import json
import os

# ==========================================
# 1. AYARLAR VE API KONFİGÜRASYONU
# ==========================================
API_KEY = "SENIN_API_ANAHTARIN_BURAYA_GELECEK"
genai.configure(api_key=API_KEY)
MODEL_ADI = 'gemini-1.5-flash'

# ==========================================
# 2. TEMEL FONKSİYONLAR
# ==========================================

def pdf_metin_cikar(pdf_yolu):
    """PDF'i okur ve metne çevirir."""
    print(f"📄 '{pdf_yolu}' okunuyor...")
    tam_metin = ""
    try:
        with pdfplumber.open(pdf_yolu) as pdf:
            for sayfa in pdf.pages:
                metin = sayfa.extract_text()
                if metin:
                    tam_metin += metin + "\n"
        return tam_metin
    except Exception as e:
        print(f"❌ PDF Okuma Hatası: {e}")
        return None

def cv_yapilandir(cv_metni):
    """Ham metni LLM ile yapılandırılmış JSON verisine dönüştürür."""
    print("🧠 CV metni yapay zeka ile analiz ediliyor...")
    model = genai.GenerativeModel(MODEL_ADI)
    
    prompt = f"""
    Aşağıdaki CV metnini analiz et ve sadece JSON formatında çıktı ver. Başka metin ekleme.
    Format:
    {{
        "kisisel_bilgiler": {{"ad_soyad": "", "eposta": "", "telefon": ""}},
        "ozet_bilgiler": {{"toplam_deneyim_yili": 0, "son_unvan": "", "egitim_seviyesi": ""}},
        "teknik_yetenekler": [],
        "sosyal_yetenekler": []
    }}
    CV Metni: {cv_metni}
    """
    try:
        response = model.generate_content(prompt)
        sonuc = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(sonuc)
    except Exception as e:
        print(f"❌ Veri Çıkarma Hatası: {e}")
        return None

def cv_ilan_eslestir(cv_json, is_ilani_metni):
    """CV verisi ile iş ilanını karşılaştırıp puanlar."""
    print("⚖️ Aday iş ilanı ile eşleştiriliyor...")
    model = genai.GenerativeModel(MODEL_ADI)
    
    prompt = f"""
    Sen bir İK uzmanısın. Aşağıdaki CV JSON verisini ve İş İlanını karşılaştır.
    Sadece JSON formatında çıktı ver.
    Format:
    {{
        "uygunluk_skoru": 0,
        "eslesen_kriterler": [],
        "eksik_veya_zayif_yonler": [],
        "ik_uzmanina_not": ""
    }}
    
    CV Verisi: {json.dumps(cv_json, ensure_ascii=False)}
    İş İlanı: {is_ilani_metni}
    """
    try:
        response = model.generate_content(prompt)
        sonuc = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(sonuc)
    except Exception as e:
        print(f"❌ Eşleştirme Hatası: {e}")
        return None

# ==========================================
# 3. ANA ÇALIŞMA BLOĞU (MAIN)
# ==========================================
if __name__ == "__main__":
    # Test Dosyaları ve Verileri
    pdf_dosyasi = "ornek_cv.pdf" # Kodu çalıştırdığın klasörde bu isimde bir PDF olmalı
    
    aranan_is_ilani = """
    Pozisyon: Python Backend Geliştirici
    - En az 3 yıl Python tecrübesi (Django veya FastAPI)
    - Veritabanı tasarımı ve SQL bilgisi
    - Docker tecrübesi
    - İngilizce döküman okuyabilme
    - Takım çalışmasına yatkınlık
    """
    
    print("=== YAPAY ZEKA DESTEKLİ İŞE ALIM SİSTEMİ BAŞLATILDI ===\n")
    
    if not os.path.exists(pdf_dosyasi):
        print(f"⚠️ HATA: '{pdf_dosyasi}' bulunamadı. Lütfen script ile aynı klasöre bir PDF dosyası koyun.")
    else:
        # 1. Adım: PDF'ten metin çıkar
        ham_metin = pdf_metin_cikar(pdf_dosyasi)
        
        if ham_metin:
            # 2. Adım: Metni JSON'a çevir
            cv_verisi = cv_yapilandir(ham_metin)
            
            if cv_verisi:
                # 3. Adım: İş ilanı ile eşleştir
                rapor = cv_ilan_eslestir(cv_verisi, aranan_is_ilani)
                
                if rapor:
                    # 4. Adım: Sonuçları konsola şık bir şekilde yazdır
                    print("\n" + "="*40)
                    print(f"👤 ADAY: {cv_verisi['kisisel_bilgiler'].get('ad_soyad', 'Bilinmiyor')}")
                    print(f"🎯 UYGUNLUK SKORU: %{rapor.get('uygunluk_skoru', 0)}")
                    print("="*40)
                    
                    print("\n✅ EŞLEŞEN GÜÇLÜ YÖNLER:")
                    for k in rapor.get('eslesen_kriterler', []):
                        print(f"  + {k}")
                        
                    print("\n⚠️ EKSİK/ZAYIF YÖNLER:")
                    for e in rapor.get('eksik_veya_zayif_yonler', []):
                        print(f"  - {e}")
                        
                    print(f"\n💡 İK ÖZETİ:\n{rapor.get('ik_uzmanina_not', '')}")
                    print("="*40 + "\n")
