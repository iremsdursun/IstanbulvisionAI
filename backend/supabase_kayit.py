from supabase import create_client

url = ""
key = ""

supabase = create_client(url, key)

veri = {
    "mekan": "Kadıköy",
    "zaman": "2026-04-25 16:50",
    "kisi_sayisi": 12,
    "araba_sayisi": 1,
    "motor_sayisi": 0,
    "otobus_sayisi": 0,
    "kamyon_sayisi": 0,
    "yogunluk": "Orta",
    "gorsel": "kadikoy.jpg"
}

supabase.table("analiz_sonuclari").insert(veri).execute()

print("Supabase kayıt başarılı")
