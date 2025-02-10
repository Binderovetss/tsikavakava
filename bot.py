from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import logging

# Устанавливаем уровень логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Замените на ваш токен бота
BOT_TOKEN = "7368319072:AAGRGJU9NqchsjSMGHdVSrKGZEXYfyyRiUE"
WEBHOOK_URL = "https://tsikavakava.fly.dev"  # Ваш публичный URL от Fly.io

# Создайте объект приложения
application = Application.builder().token(BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправить сообщение при вызове команды /start"""
    await update.message.reply_text("Привет, я бот!")

def main():
    # Добавьте обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # Настройка вебхука
    application.run_webhook(
        listen="0.0.0.0",  # Прослушиваем все IP-адреса
        port=8080,  # Порт, на котором будет работать вебхук
        url_path=BOT_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}",  # Формируем URL для webhook
        secret_token="your_secret_token",  # Можно установить секретный токен
    )

if __name__ == "__main__":
    main()
