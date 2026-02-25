import google.generativeai as genai
import json

# 1. API Anahtarını Tanımla 
# (Google AI Studio'dan ücretsiz bir API key alıp buraya yapıştırmalısın)
API_KEY = "SENIN_API_ANAHTARIN_BURAYA_GELECEK"
genai.configure(api_key=API_KEY)

def cv_analiz_llm(cv_metni):
    """
    CV metnini LLM'e gönderir ve yapılandırılmış JSON verisi olarak geri alır.
    """
    # Hızlı ve veri analizi için çok iyi olan flash modelini seçiyoruz
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Sistemin beyni: PROMPT (Komut)
    prompt = f"""
    Sen uzman bir İnsan Kaynakları asistanısın. Aşağıda bir adayın CV'sinden çıkarılmış ham metin bulunuyor. 
    Lütfen bu metni analiz et ve KESİNLİKLE sadece aşağıdaki JSON formatında çıktı ver. Başka hiçbir açıklama metni ekleme.
    Eğer bir bilgi CV'de yoksa 'null' veya boş liste '[]' bırak.
    
    Beklenen JSON Formatı:
    {{
        "kisisel_bilgiler": {{
            "ad_soyad": "",
            "eposta": "",
            "telefon": ""
        }},
        "ozet_bilgiler": {{
            "toplam_deneyim_yili": 0,  # Sadece sayı
            "son_unvan": "",
            "egitim_seviyesi": "" # Örn: Lisans, Yüksek Lisans
        }},
        "teknik_yetenekler": [],
        "sosyal_yetenekler": []
    }}

    CV Ham Metni:
    -----------------
    {cv_metni}
    -----------------
    """
    
    print("Yapay Zeka CV'yi analiz ediyor, lütfen bekleyin...")
    
    try:
        # LLM'e isteği gönder
        response = model.generate_content(prompt)
        sonuc_metni = response.text
        
        # LLM bazen JSON kod bloğu markdown'ı (```json ... ```) ile yanıt verebilir, onu temizleyelim
        sonuc_metni = sonuc_metni.replace("```json", "").replace("```", "").strip()
        
        # Metni Python Sözlüğüne (Dictionary) çevir
        analiz_sonucu = json.loads(sonuc_metni)
        return analiz_sonucu
        
    except Exception as e:
        return {"hata": f"Analiz sırasında bir hata oluştu: {e}"}

# === SİSTEMİ TEST EDELİM ===
if __name__ == "__main__":
    # Örnek bir CV metni (Gerçek senaryoda bu PDF'ten gelecek)
    ornek_cv_metni = """
    Adım Ahmet Yılmaz. 1995 İstanbul doğumluyum. 
    ahmet.yilmaz@email.com adresinden veya 555-1234567 numarasından bana ulaşabilirsiniz.
    Boğaziçi Üniversitesi Bilgisayar Mühendisliği bölümünden 2018'de mezun oldum (Lisans).
    Kariyerime Trendyol'da Backend Developer olarak başladım ve 3 yıl çalıştım. 
    Ardından Getir'de Senior Backend Developer olarak 2 yıl daha görev yaptım.
    Python, Django, PostgreSQL, Docker, AWS ve Kubernetes teknolojilerine çok iyi derecede hakimim.
    Ayrıca takım çalışmasına yatkınım ve çevik (agile) yöntemlerle proje yönetimi konusunda tecrübeliyim.
    """
    
    # LLM Analizini Çalıştır
    # NOT: Kodu çalıştırmadan önce geçerli bir API KEY girmeyi unutma!
    sonuc = cv_analiz_llm(ornek_cv_metni)
    
    # Çıktıyı güzel ve okunabilir formatta yazdır
    print("\n--- YAPAY ZEKA ANALİZ SONUCU ---")
    print(json.dumps(sonuc, indent=4, ensure_ascii=False))
