from flask import Flask, request, jsonify
from flask_cors import CORS  # Подключаем поддержку CORS
import requests
import time

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для всех запросов

TELEGRAM_BOT_TOKEN = "7368319072:AAEqEa3DWGdgA0HsqrfcTlSJaPYeCGCj52A"
CHAT_ID = "294154587"

redirects = {}  # Временное хранилище для редиректов

@app.route('/send-to-telegram', methods=['POST', 'OPTIONS'])
def send_to_telegram():
    """Принимает данные от клиента и отправляет их в Telegram"""
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()  # Разрешаем CORS preflight

    data = request.json
    user_id = int(time.time())
    choice = data.get("choice", "")

    keyboard = {
        "inline_keyboard": [
            [{"text": "Перенаправить на зелёную", "callback_data": f"{user_id}:green"}],
            [{"text": "Перенаправить на красную", "callback_data": f"{user_id}:red"}]
        ]
    }

    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": f"Пользователь выбрал: {choice}",
        "reply_markup": keyboard
    }

    response = requests.post(telegram_url, json=payload)
    print(f"📩 Отправка в Telegram: {response.status_code}, {response.text}")

    for _ in range(30):
        if user_id in redirects:
            return jsonify({"redirect_url": redirects.pop(user_id)})
        time.sleep(2)

    return jsonify({"message": "Оператор ещё не ответил, попробуйте позже."})

@app.route('/telegram-callback', methods=['POST'])
def telegram_callback():
    """Обрабатывает выбор оператора и сохраняет ссылку для редиректа"""
    data = request.json
    print(f"📩 Получены данные от Telegram: {data}")  # Логируем данные

    if "callback_query" not in data:
        print("🚨 Ошибка: в запросе нет 'callback_query'!")
        return jsonify({"error": "Invalid request format"}), 400

    callback_data = data["callback_query"].get("data")
    if not callback_data:
        print("🚨 Ошибка: в callback_query нет 'data'!")
        return jsonify({"error": "Missing 'data' in callback_query"}), 400

    user_id, color = callback_data.split(":")

    redirect_url = "http://127.0.0.1:8000/green.html" if color == "green" else "http://127.0.0.1:8000/red.html"
    redirects[int(user_id)] = redirect_url

    print(f"✅ Перенаправление пользователя {user_id} на {redirect_url}")

    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
    requests.post(telegram_url, json={"callback_query_id": data["callback_query"]["id"], "text": "Ссылка выбрана!"})

    return jsonify({"status": "success"})

def _build_cors_preflight_response():
    """Обрабатывает CORS preflight-запрос"""
    response = jsonify({"message": "CORS OK"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)