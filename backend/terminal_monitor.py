from coklu_kamera_analiz import canli_analiz_yap
import time
from datetime import datetime

BEKLEME_SURESI = 180  # 3 dk


def metrikleri_hesapla(sonuclar):
    toplam_kamera = len(sonuclar)
    toplam_kisi = sum(s.get("kisi_sayisi", 0) for s in sonuclar)
    toplam_arac = sum(
        s.get("araba_sayisi", 0)
        + s.get("motor_sayisi", 0)
        + s.get("otobus_sayisi", 0)
        + s.get("kamyon_sayisi", 0)
        for s in sonuclar
    )

    sakin = sum(1 for s in sonuclar if s.get("yogunluk") == "Sakin")
    orta = sum(1 for s in sonuclar if s.get("yogunluk") == "Orta")
    yogun = sum(1 for s in sonuclar if s.get("yogunluk") == "Yoğun")

    ortalama_kisi = toplam_kisi / toplam_kamera if toplam_kamera > 0 else 0

    en_yogun = max(
        sonuclar,
        key=lambda s: s.get("kisi_sayisi", 0),
        default=None
    )

    return {
        "toplam_kamera": toplam_kamera,
        "toplam_kisi": toplam_kisi,
        "toplam_arac": toplam_arac,
        "sakin": sakin,
        "orta": orta,
        "yogun": yogun,
        "ortalama_kisi": round(ortalama_kisi, 2),
        "en_yogun": en_yogun
    }


def panel_yazdir(sonuclar):
    zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    metrikler = metrikleri_hesapla(sonuclar)

    print("\n" + "=" * 60)
    print("İSTANBULVISION AI - CANLI ANALİZ PANELİ")
    print("=" * 60)
    print("Analiz zamanı:", zaman)
    print("Toplam kamera:", metrikler["toplam_kamera"])
    print("Toplam kişi:", metrikler["toplam_kisi"])
    print("Toplam araç:", metrikler["toplam_arac"])
    print("Ortalama kişi:", metrikler["ortalama_kisi"])
    print("Sakin kamera sayısı:", metrikler["sakin"])
    print("Orta kamera sayısı:", metrikler["orta"])
    print("Yoğun kamera sayısı:", metrikler["yogun"])

    if metrikler["en_yogun"]:
        print(
            "En yoğun nokta:",
            metrikler["en_yogun"]["mekan"],
            "-",
            metrikler["en_yogun"].get("kisi_sayisi", 0),
            "kişi"
        )

    print("-" * 60)

    for sonuc in sonuclar:
        print(
            f"{sonuc['mekan']} | "
            f"Kişi: {sonuc.get('kisi_sayisi', 0)} | "
            f"Araç: {sonuc.get('araba_sayisi', 0) + sonuc.get('motor_sayisi', 0) + sonuc.get('otobus_sayisi', 0) + sonuc.get('kamyon_sayisi', 0)} | "
            f"Yoğunluk: {sonuc.get('yogunluk', '-')}"
        )

    print("=" * 60)


while True:
    sonuclar = canli_analiz_yap()
    panel_yazdir(sonuclar)

    print(f"{BEKLEME_SURESI} saniye sonra tekrar analiz yapılacak...")
    time.sleep(BEKLEME_SURESI)
