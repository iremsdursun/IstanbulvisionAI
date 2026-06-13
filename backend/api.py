from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler
from collections import defaultdict
from supabase import create_client
import json
import os

from coklu_kamera_analiz import canli_analiz_yap

app = FastAPI(
    title="IstanbulVision AI API",
    description="Istanbul kamera yogunluk analiz sonuclarini sunan RESTful API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/results", StaticFiles(directory="../results"), name="results")
app.mount(
    "/screenshots",
    StaticFiles(directory="../screenshots"),
    name="screenshots"
)

RESULT_FILE = "../data/coklu_kamera_sonuclari.json"
SUPABASE_URL = "url"
SUPABASE_KEY = "key"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def json_response(data):
    return Response(
        content=json.dumps(data, ensure_ascii=False),
        media_type="application/json; charset=utf-8"
    )


def otomatik_analiz_gorevi():
    print("Otomatik analiz başlatıldı...")
    canli_analiz_yap()
    print("Otomatik analiz tamamlandı.")


scheduler = BackgroundScheduler()

scheduler.add_job(
    otomatik_analiz_gorevi,
    "interval",
    minutes=3,
    id="otomatik_kamera_analizi",
    replace_existing=True
)

scheduler.start()


@app.get("/")
def home():
    return {
        "message": "IstanbulVision AI API calisiyor",
        "endpoints": [
            "/son-durum",
            "/kamera-sonuclari",
            "/canli-analiz",
            "/docs"
        ],
        "otomatik_analiz": "Her 3 dakikada bir calisir"
    }


@app.get("/kamera-sonuclari")
def kamera_sonuclari():
    if not os.path.exists(RESULT_FILE):
        return json_response({
            "hata": "Henuz analiz sonucu bulunamadi."
        })

    with open(RESULT_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    return json_response(data)


@app.get("/son-durum")
def son_durum():
    if not os.path.exists(RESULT_FILE):
        return json_response({
            "hata": "Henuz analiz sonucu bulunamadi."
        })

    with open(RESULT_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    return json_response(data)


@app.get("/canli-analiz")
def canli_analiz():
    data = canli_analiz_yap()
    return json_response(data)

@app.get("/tahmin")
def tahmin():
    if not os.path.exists(RESULT_FILE):
        return json_response({"hata": "Tahmin için analiz verisi bulunamadı."})

    with open(RESULT_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    tahminler = []

    for item in data:
        if "hata" in item:
            continue

        mekan = item.get("mekan", "-")
        kisi = item.get("kisi_sayisi", 0)
        arac = item.get("araba_sayisi", 0) + item.get("motor_sayisi", 0) + item.get("otobus_sayisi", 0) + item.get("kamyon_sayisi", 0)
        yogunluk = item.get("yogunluk", "Sakin")

        toplam_skor = kisi + (arac * 2)

        if toplam_skor >= 25:
            tahmin = "Bugün 17:00 - 19:00 arasında yoğun olabilir."
            olasilik = 82
            durum = "Yüksek"
        elif toplam_skor >= 10:
            tahmin = "Bugün 14:00 - 16:00 arasında orta yoğunluk bekleniyor."
            olasilik = 61
            durum = "Orta"
        else:
            tahmin = "Bugün genel olarak sakin olabilir."
            olasilik = 35
            durum = "Düşük"

        tahminler.append({
            "mekan": mekan,
            "mevcut_kisi": kisi,
            "mevcut_arac": arac,
            "mevcut_yogunluk": yogunluk,
            "tahmin": tahmin,
            "tahmin_olasiligi": f"%{olasilik}",
            "risk_seviyesi": durum
        })

    tahminler = sorted(
        tahminler,
        key=lambda x: int(x["tahmin_olasiligi"].replace("%", "")),
        reverse=True
    )

    return json_response(tahminler)
