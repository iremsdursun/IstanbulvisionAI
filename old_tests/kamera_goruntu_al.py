import subprocess

kamera_url = "https://livestream.ibb.gov.tr/cam_turistik/b_eminonu.stream/playlist.m3u8"

kayit_yolu = "../screenshots/eminonu_test.jpg"

komut = [
    "ffmpeg",
    "-y",
    "-i",
    kamera_url,
    "-frames:v",
    "1",
    kayit_yolu
]

subprocess.run(komut)

print("Görüntü başarıyla kaydedildi.")
