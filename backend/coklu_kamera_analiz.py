import subprocess
import json
import os
import cv2
import supervision as sv
from datetime import datetime
from ultralytics import YOLO
from supabase import create_client

MODEL = YOLO("yolo11n.pt")

SCREENSHOT_DIR = "../screenshots"
DATA_DIR = "../data"
RESULT_FILE = "../data/coklu_kamera_sonuclari.json"
RESULT_IMAurll"
SUPABASE_KEY = "key"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

KAMERALAR = [
    {"ad": "Kadıköy", "url": "https://livestream.ibb.gov.tr/cam_turistik/b_kadikoy.stream/chunklist.m3u8"},
    {"ad": "Mısır Çarşısı", "url": "https://livestream.ibb.gov.tr/cam_turistik/b_misircarsisi.stream/chunklist.m3u8"},
    {"ad": "Üsküdar", "url": "https://livestream.ibb.gov.tr/cam_turistik/b_uskudar.stream/chunklist.m3u8"},
    {"ad": "Saraçhane", "url": "https://livestream.ibb.gov.tr/cam_turistik/b_sarachane.stream/chunklist.m3u8"},
    {"ad": "Taksim Meydanı", "url": "https://livestream.ibb.gov.tr/cam_turistik/b_taksim_meydan.stream/chunklist.m3u8"},
    {"ad": "Kız Kulesi", "url": "https://livestream.ibb.gov.tr/cam_turistik/new_K%C4%B1zkulesi.stream/playlist.m3u8"},
    {"ad": "Kapalı Çarşı", "url": "https://livestream.ibb.gov.tr/cam_turistik/b_kapalicarsi.stream/playlist.m3u8"},
    {"ad": "Eyüp Sultan", "url": "https://livestream.ibb.gov.tr/cam_turistik/b_kapalicarsi.stream/playlist.m3u8"}
]


def klasorleri_hazirla():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(RESULT_IMAGE_DIR, exist_ok=True)

def temiz_ad(ad):
    cevir = str.maketrans("çğıöşüÇĞİÖŞÜ ", "cgiosuCGIOSU_")
    return ad.translate(cevir).lower()


def yogunluk_hesapla(kisi_sayisi):
    if kisi_sayisi <= 5:
        return "Sakin"
    elif kisi_sayisi <= 15:
        return "Orta"
    else:
        return "Yoğun"


def goruntu_al(kamera_url, dosya_yolu):
    komut = [
        "ffmpeg",
        "-y",
        "-loglevel", "error",
        "-i", kamera_url,
        "-frames:v", "1",
        dosya_yolu
    ]

    sonuc = subprocess.run(komut)
    return sonuc.returncode == 0

def analiz_et(dosya_yolu, sonuc_gorsel_yolu):
    if not os.path.exists(dosya_yolu):
        return {
            "kisi_sayisi": 0,
            "araba_sayisi": 0,
            "motor_sayisi": 0,
            "otobus_sayisi": 0,
            "kamyon_sayisi": 0
        }

    results = MODEL(
        dosya_yolu,
        conf=0.25,
        imgsz=1280,
        save=False,
        verbose=False
    )

    sayim = {
        "kisi_sayisi": 0,
        "araba_sayisi": 0,
        "motor_sayisi": 0,
        "otobus_sayisi": 0,
        "kamyon_sayisi": 0
    }

    image = cv2.imread(dosya_yolu)

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])

            if class_id == 0:
                sayim["kisi_sayisi"] += 1
            elif class_id == 2:
                sayim["araba_sayisi"] += 1
            elif class_id == 3:
                sayim["motor_sayisi"] += 1
            elif class_id == 5:
                sayim["otobus_sayisi"] += 1
            elif class_id == 7:
                sayim["kamyon_sayisi"] += 1

        detections = sv.Detections.from_ultralytics(result)

        box_annotator = sv.BoxAnnotator()
        label_annotator = sv.LabelAnnotator()

        labels = [
            f"{MODEL.names[class_id]} {confidence:.2f}"
            for class_id, confidence in zip(
                detections.class_id,
                detections.confidence
            )
        ]

        annotated_image = box_annotator.annotate(
            scene=image.copy(),
            detections=detections
        )

        annotated_image = label_annotator.annotate(
            scene=annotated_image,
            detections=detections,
            labels=labels
        )

        cv2.imwrite(sonuc_gorsel_yolu, annotated_image)

    return sayim
def supabase_kaydet(sonuclar):
    try:
        temiz_sonuclar = []

        for sonuc in sonuclar:
            if "hata" in sonuc:
                print(f"{sonuc.get('mekan')} kaydedilmedi: {sonuc.get('hata')}")
                continue

            temiz_sonuclar.append({
                "mekan": sonuc.get("mekan"),
                "zaman": sonuc.get("zaman"),
                "kisi_sayisi": sonuc.get("kisi_sayisi", 0),
                "araba_sayisi": sonuc.get("araba_sayisi", 0),
                "motor_sayisi": sonuc.get("motor_sayisi", 0),
                "otobus_sayisi": sonuc.get("otobus_sayisi", 0),
                "kamyon_sayisi": sonuc.get("kamyon_sayisi", 0),
                "yogunluk": sonuc.get("yogunluk"),
                "gorsel": sonuc.get("gorsel"),
                "sonuc_gorsel": sonuc.get("sonuc_gorsel")
            })

        if temiz_sonuclar:
            supabase.table("analiz_sonuclari").insert(temiz_sonuclar).execute()
            print("Supabase kayıt başarılı.")
        else:
            print("Supabase'e kaydedilecek geçerli veri yok.")

    except Exception as e:
        print("Supabase kayıt hatası:", e)


def tek_kamera_analiz_et(kamera):
    ad = kamera["ad"]
    url = kamera["url"]

    zaman = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dosya_adi = temiz_ad(ad)

    gorsel_yolu = f"{SCREENSHOT_DIR}/{dosya_adi}_{zaman}.jpg"
    sonuc_gorsel_yolu = f"{RESULT_IMAGE_DIR}/{dosya_adi}_{zaman}_annotated.jpg"

    print(f"{ad} kamerası analiz ediliyor...")

    if not goruntu_al(url, gorsel_yolu):
        return {
            "mekan": ad,
            "zaman": zaman,
            "hata": "Görüntü alınamadı"
        }

    sayim = analiz_et(gorsel_yolu, sonuc_gorsel_yolu)
    yogunluk = yogunluk_hesapla(sayim["kisi_sayisi"])

    return {
        "mekan": ad,
        "zaman": zaman,
        "kisi_sayisi": sayim["kisi_sayisi"],
        "araba_sayisi": sayim["araba_sayisi"],
        "motor_sayisi": sayim["motor_sayisi"],
        "otobus_sayisi": sayim["otobus_sayisi"],
        "kamyon_sayisi": sayim["kamyon_sayisi"],
        "yogunluk": yogunluk,
        "gorsel": gorsel_yolu,
        "sonuc_gorsel": sonuc_gorsel_yolu
    }
    
def canli_analiz_yap():
    klasorleri_hazirla()

    sonuclar = []

    for kamera in KAMERALAR:
        sonuc = tek_kamera_analiz_et(kamera)
        sonuclar.append(sonuc)

    with open(RESULT_FILE, "w", encoding="utf-8") as file:
        json.dump(sonuclar, file, ensure_ascii=False, indent=4)

    supabase_kaydet(sonuclar)

    return sonuclar

if __name__ == "__main__":
    sonuclar = canli_analiz_yap()

    for sonuc in sonuclar:
        print(sonuc)

    print("Canlı analiz tamamlandı.")
