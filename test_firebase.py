# test_push.py (положить в корень, рядом с docker-compose.yml)
import sys
from pathlib import Path

# const firebaseConfig = {
#   apiKey: "AIzaSyCSSN_vZI2u7tMyUcDxNCxZA7TtiDOWErQ",
#   authDomain: "eventmanager-b7f5c.firebaseapp.com",
#   projectId: "eventmanager-b7f5c",
#   storageBucket: "eventmanager-b7f5c.firebasestorage.app",
#   messagingSenderId: "126978082457",
#   appId: "1:126978082457:web:899c11bbdb9f2b6a3b1a08",
#   measurementId: "G-4PV2V6KE6B"
# };

# BIyYz3ubfj2J1Mt6FINe8-6qqa_ruPaVTugmnUwGjhVCDMAFOWC6yHnmTxHueIiK_XK2zgs4LcqiUgPs-N4cvXM

from app.core.firebase import init_firebase

# Добавляем app в путь
sys.path.insert(0, str(Path(__file__).parent / "app"))

# Проверяем инициализацию
try:
    init_firebase()
    print("✅ Firebase готов к работе")

    # Если у тебя есть реальный FCM токен - раскомментируй и вставь
    # TEST_TOKEN = "ваш_fcm_токен"
    # send_push(TEST_TOKEN, "Тест", "Привет из Firebase!")

except Exception as e:
    print(f"❌ Ошибка: {e}")