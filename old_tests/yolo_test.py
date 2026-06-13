from ultralytics import YOLO

model = YOLO("yolov8n.pt")

image_path = "../screenshots/kadikoy_test.jpg"

results = model(image_path, save=True)

person_count = 0

for result in results:
    for box in result.boxes:
        class_id = int(box.cls[0])

        # YOLO'da person sınıfı 0'dır
        if class_id == 0:
            person_count += 1

print("Tespit edilen kişi sayısı:", person_count)

if person_count <= 5:
    density = "Sakin"
elif person_count <= 15:
    density = "Orta"
else:
    density = "Yoğun"

print("Yoğunluk durumu:", density)
