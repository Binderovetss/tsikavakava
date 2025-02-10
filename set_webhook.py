import requests

# Ваш публичный URL для webhook
WEBHOOK_URL = "https://tsikavakava.fly.dev"  # Ваш публичный URL на Fly.io
BOT_TOKEN = "7368319072:AAGRGJU9NqchsjSMGHdVSrKGZEXYfyyRiUE"  # Ваш токен бота

# Устанавливаем webhook
webhook_url = f"https://api.telegram.org/bot{7368319072:AAGRGJU9NqchsjSMGHdVSrKGZEXYfyyRiUE}/setWebhook?url={https://tsikavakava.fly.dev}/{7368319072:AAGRGJU9NqchsjSMGHdVSrKGZEXYfyyRiUE}"
response = requests.get(webhook_url)
print(response.json())  # Это покажет, успешна ли настройка webhook
