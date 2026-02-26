import streamlit as st
import google.generativeai as genai
import pdfplumber
import docx
import json
import os

# API anahtarı (tercihen environment variable kullan)
genai.configure(api_key="API_ANAHTARIN")

# -----------------------------
# CV DOSYASINI METNE ÇEVİRME
# -----------------------------

def pdf_to_text(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def docx_to_text(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

# -----------------------------
# CV METNİNİ JSON'A ÇEVİRME
# -----------------------------

def cv_analiz_et(cv_text):
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = f"""
    Aşağıdaki CV metnini analiz et ve şu JSON formatında çıkar:

    {{
        "kisisel_bilgiler": {{
            "ad_soyad": ""
        }},
        "ozet_bilgiler": {{
            "toplam_deneyim_yili": 0,
            "son_unvan": "",
            "egitim_seviyesi": ""
        }},
        "teknik_yetenekler": [],
        "sosyal_yetenekler": []
    }}

    CV METNİ:
    {cv_text}
    """

    response = model.generate_content(prompt)
    temiz = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(temiz)

# -----------------------------
# CV - İLAN EŞLEŞTİRME
# -----------------------------

def cv_ilan_eslestir(cv_json, is_ilani):
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
    Sen kıdemli bir Talent Acquisition uzmanısın.

    Aday CV:
    {json.dumps(cv_json, ensure_ascii=False)}

    İş İlanı:
    {is_ilani}

    0-100 arası uygunluk_skoru üret.

    SADECE JSON DÖN:
    {{
        "uygunluk_skoru": 0,
        "eslesen_kriterler": [],
        "eksik_veya_zayif_yonler": [],
        "ik_uzmanina_not": ""
    }}
    """

    response = model.generate_content(prompt)
    temiz = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(temiz)

# -----------------------------
# STREAMLIT ARAYÜZÜ
# -----------------------------

st.title("🤖 AI Destekli CV Reader & Sıralama Sistemi")

is_ilani = st.text_area("📌 İş İlanını Girin")

uploaded_files = st.file_uploader(
    "📂 CV Dosyalarını Yükleyin (PDF/DOCX)",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

if st.button("🔍 Analizi Başlat"):

    if not is_ilani:
        st.warning("Lütfen iş ilanını girin.")
        st.stop()

    if not uploaded_files:
        st.warning("Lütfen en az bir CV yükleyin.")
        st.stop()

    sonuclar = []

    for file in uploaded_files:

        st.write(f"İşleniyor: {file.name}")

        # 1️⃣ CV Metne Çevir
        if file.name.endswith(".pdf"):
            cv_text = pdf_to_text(file)
        else:
            cv_text = docx_to_text(file)

        # 2️⃣ CV Analizi
        cv_json = cv_analiz_et(cv_text)

        # 3️⃣ Eşleştirme
        eslesme = cv_ilan_eslestir(cv_json, is_ilani)

        sonuclar.append({
            "Ad Soyad": cv_json["kisisel_bilgiler"]["ad_soyad"],
            "Skor": eslesme["uygunluk_skoru"],
            "Not": eslesme["ik_uzmanina_not"]
        })

    # 4️⃣ Skora Göre Sırala
    sirali = sorted(sonuclar, key=lambda x: x["Skor"], reverse=True)

    st.subheader("📊 Sıralı Aday Listesi")
    st.table(sirali)