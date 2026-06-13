import subprocess
import time
import json
from datetime import datetime
from ultralytics import YOLO

KAMERA_URL = "https://livestream.ibb.gov.tr/cam_turistik/b_kadikoy.stream/chunklist.m3u8"
MODEL = YOLO("yolov8n.pt")

def yogunluk_hesapla(kisi_sayisi):
    if kisi_sayisi <= 5:
        return "Sakin"
    elif kisi_sayisi <= 15:
        return "Orta"
    else:
        return "Yoğun"

def goruntu_al(dosya_yolu):
    komut = [
        "ffmpeg",
        "-y",
        "-i", KAMERA_URL,
        "-frames:v", "1",
        dosya_yolu
    ]
    subprocess.run(komut, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def analiz_et(dosya_yolu):
    results = MODEL(dosya_yolu, save=True)
    kisi_sayisi = 0

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            if class_id == 0:
                kisi_sayisi += 1

    return kisi_sayisi

sonuclar = []

for i in range(3):
    zaman = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dosya_yolu = f"../screenshots/kadikoy_{zaman}.jpg"

    print(f"{i+1}. analiz başlıyor...")

    goruntu_al(dosya_yolu)
    kisi_sayisi = analiz_et(dosya_yolu)
    yogunluk = yogunluk_hesapla(kisi_sayisi)

    sonuc = {
        "mekan": "Kadıköy",
        "zaman": zaman,
        "kisi_sayisi": kisi_sayisi,
        "yogunluk": yogunluk,
        "gorsel": dosya_yolu
    }

    sonuclar.append(sonuc)

    print("Mekan:", sonuc["mekan"])
    print("Kişi sayısı:", kisi_sayisi)
    print("Yoğunluk:", yogunluk)
    print("-" * 40)

    time.sleep(60)

with open("../data/analiz_sonuclari.json", "w", encoding="utf-8") as file:
    json.dump(sonuclar, file, ensure_ascii=False, indent=4)

print("Analiz sonuçları kaydedildi.")
