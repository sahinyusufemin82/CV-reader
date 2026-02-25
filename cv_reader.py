import google.generativeai as genai
import json

# API anahtarını tanımladığını varsayıyoruz (Önceki adımdaki gibi)
# genai.configure(api_key="API_ANAHTARIN")

def cv_ilan_eslestir(cv_verisi_json, is_ilani_metni):
    """
    Çıkarılan CV verisi ile İş İlanını karşılaştırıp detaylı bir uygunluk puanı üretir.
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Sen kıdemli bir İşe Alım (Talent Acquisition) Uzmanısın. 
    Aşağıda bir adayın analiz edilmiş CV verileri (JSON formatında) ve açık bir pozisyonun iş ilanı (Job Description) metni bulunuyor.
    
    Görevin: Adayın bu role ne kadar uygun olduğunu analiz edip 0 ile 100 arasında genel bir "uygunluk_skoru" belirlemek. 
    Analiz yaparken deneyim yıllarını, eğitim seviyesini ve özellikle teknik yetenekleri göz önünde bulundur. Benzer teknolojileri eşdeğer veya yakın kabul edebilirsin (Örn: İlan AWS istiyorsa, adayda GCP varsa kısmi puan ver).
    
    Lütfen KESİNLİKLE ve SADECE aşağıdaki JSON formatında çıktı ver:
    
    {{
        "uygunluk_skoru": 0,
        "eslesen_kriterler": ["kriter 1", "kriter 2"],
        "eksik_veya_zayif_yonler": ["eksik 1", "eksik 2"],
        "ik_uzmanina_not": "Adayın profili hakkında 2-3 cümlelik kısa ve net bir değerlendirme özeti."
    }}

    --- ADAYIN CV VERİSİ ---
    {json.dumps(cv_verisi_json, ensure_ascii=False)}
    
    --- İŞ İLANI METNİ ---
    {is_ilani_metni}
    """
    
    print("Aday iş ilanı ile eşleştiriliyor, puan hesaplanıyor...")
    
    try:
        response = model.generate_content(prompt)
        sonuc_metni = response.text.replace("```json", "").replace("```", "").strip()
        
        eslestirme_sonucu = json.loads(sonuc_metni)
        return eslestirme_sonucu
        
    except Exception as e:
        return {"hata": f"Eşleştirme sırasında bir hata oluştu: {e}"}

# === SİSTEMİ TEST EDELİM ===
if __name__ == "__main__":
    
    # 1. Önceki adımdan gelen sahte CV verimiz (Sistemin çıkardığı JSON)
    aday_cv = {
        "kisisel_bilgiler": {
            "ad_soyad": "Ahmet Yılmaz"
        },
        "ozet_bilgiler": {
            "toplam_deneyim_yili": 5,
            "son_unvan": "Senior Backend Developer",
            "egitim_seviyesi": "Lisans"
        },
        "teknik_yetenekler": ["Python", "Django", "PostgreSQL", "Docker", "AWS", "Kubernetes"],
        "sosyal_yetenekler": ["Takım çalışması", "Çevik proje yönetimi (Agile)"]
    }
    
    # 2. İK departmanının girdiği İş İlanı Metni
    ornek_is_ilani = """
    Şirketimize Senior Software Engineer arıyoruz.
    - En az 4 yıl backend geliştirme tecrübesi,
    - Python ve FastAPI veya Flask konusunda uzman (Django da kabul edilebilir),
    - Microservis mimarisi ve Docker/Kubernetes tecrübesi,
    - Bulut sistemleri (Tercihen Google Cloud - GCP) kullanmış,
    - NoSQL (MongoDB vb.) veritabanlarına aşina olmak artı puandır.
    """
    
    # Analizi çalıştır
    eslestirme_raporu = cv_ilan_eslestir(aday_cv, ornek_is_ilani)
    
    # Sonucu ekrana yazdır
    print("\n=== ADAY DEĞERLENDİRME RAPORU ===")
    print(f"Uygunluk Skoru: % {eslestirme_raporu.get('uygunluk_skoru', 'Hesaplanamadı')}")
    print("\n✅ Eşleşen Kriterler:")
    for kriter in eslestirme_raporu.get('eslesen_kriterler', []):
        print(f"  - {kriter}")
        
    print("\n⚠️ Eksik veya Zayıf Yönler:")
    for eksik in eslestirme_raporu.get('eksik_veya_zayif_yonler', []):
        print(f"  - {eksik}")
        
    print(f"\n💡 İK Uzmanına Not:\n{eslestirme_raporu.get('ik_uzmanina_not', '')}")
