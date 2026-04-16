import cv2
import face_recognition
import os
import serial
import pandas as pd
from datetime import datetime

# --- НАСТРОЙКИ ---
PORT = 'COM3'  # ЗАМЕНИ НА СВОЙ (посмотри в Arduino IDE)
arduino = None

try:
    arduino = serial.Serial(PORT, 9600, timeout=1)
    print(f"Подключено к {PORT}")
except:
    print("Ошибка: Ардуино не найдена. Проверь порт!")

# Создаем папку для лиц, если её нет
if not os.path.exists('kurators'):
    os.makedirs('kurators')

# Загружаем базу данных лиц
known_face_encodings = []
known_face_names = []

def load_faces():
    known_face_encodings.clear()
    known_face_names.clear()
    for filename in os.listdir('kurators'):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image = face_recognition.load_image_file(f"kurators/{filename}")
            encoding = face_recognition.face_encodings(image)[0]
            known_face_encodings.append(encoding)
            known_face_names.append(os.path.splitext(filename)[0])

load_faces()

video_capture = cv2.VideoCapture(0)

print("Система запущена. Нажми 'R' для регистрации нового лица, 'Q' для выхода.")

while True:
    ret, frame = video_capture.read()
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Находим лица
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]
            
            # Если узнали лицо — шлем команду в Ардуино
            if arduino:
                arduino.write(b'START_SESSION\n')

        # Рисуем рамку
        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    cv2.imshow('Face ID Eco-Box', frame)

    key = cv2.waitKey(1) & 0xFF
    
    # Регистрация нового лица на клавишу R
    if key == ord('r'):
        new_name = input("Введите имя и класс (например, Ivanov_9A): ")
        img_path = f"kurators/{new_name}.jpg"
        cv2.imwrite(img_path, frame)
        print(f"Пользователь {new_name} сохранен!")
        load_faces()

    # Если Ардуино что-то прислала (батарейка упала)
    if arduino and arduino.in_waiting > 0:
        data = arduino.readline().decode('utf-8').strip()
        if "BATT_OK" in data:
            print(f"Батарейка засчитана для: {name}")
            
            # Подготовка данных
            log_data = {
                'Время': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")], 
                'Имя': [name], 
                'Событие': ['Сдана батарейка']
            }
            df = pd.DataFrame(log_data)
            
            file_name = 'protocol.csv'
            
            # Если файла нет — создаем с заголовками, если есть — дописываем без заголовков
            if not os.path.isfile(file_name):
                df.to_csv(file_name, index=False, encoding='utf-8')
            else:
                df.to_csv(file_name, mode='a', index=False, header=False, encoding='utf-8')
            
            print("Данные успешно сохранены в protocol.csv!")

    if key == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
