import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram.ext import ContextTypes

# 📌 Замените на свой API URL (Render) или оставьте как есть
API_URL = "https://text-corrector-wubj.onrender.com"  # Вставьте свою ссылку с Render!

# 📌 Замените на свой Telegram Bot Token
BOT_TOKEN = "7368319072:AAGRGJU9NqchsjSMGHdVSrKGZEXYfyyRiUE"

# 📌 Ваш публичный URL
WEBHOOK_URL = "https://tsikavakava.fly.dev"  # Замените на ваш публичный URL от Fly.io

# 📌 Порт для прослушивания webhook (обычно 8443 для HTTPS)
PORT = 8443

# 📌 Функция для создания базы данных (если её нет)
def create_database():
    conn = sqlite3.connect("knowledge_base.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            photo TEXT
        )
    ''')
    conn.commit()
    conn.close()

# 📌 Функция для сохранения данных в базу
def save_to_db(text, photo_path=None):
    conn = sqlite3.connect("knowledge_base.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO knowledge (text, photo) VALUES (?, ?)", (text, photo_path))
    conn.commit()
    conn.close()

# 📌 Стартовое меню
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📝 Добавить информацию", callback_data="add_info")],
        [InlineKeyboardButton("🔍 Найти информацию", callback_data="search_info")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🔹 Выберите действие:", reply_markup=reply_markup)

# 📌 Обработчик нажатий на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "add_info":
        context.user_data["waiting_for_info"] = True
        await query.message.reply_text("📌 Отправьте текст (и фото, если нужно).")
    
    elif query.data == "search_info":
        context.user_data["waiting_for_search"] = True
        await query.message.reply_text("🔍 Введите ключевое слово для поиска.")

# 📌 Обработчик текстовых сообщений (Добавление информации)
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "waiting_for_info" in context.user_data and context.user_data["waiting_for_info"]:
        text = update.message.text

        # 📌 Отправляем текст в API на Render
        response = requests.post(API_URL, json={"text": text})
        if response.status_code == 200:
            corrected_text = response.json().get("corrected_text", text)
        else:
            corrected_text = text

        # 📌 Сохраняем исправленный текст в базу
        save_to_db(corrected_text)
        await update.message.reply_text(f"✅ Текст добавлен в базу знаний:\n\n{corrected_text}")

        # 📌 Сбрасываем флаг
        context.user_data["waiting_for_info"] = False

    elif "waiting_for_search" in context.user_data and context.user_data["waiting_for_search"]:
        keyword = update.message.text
        results = search_in_db(keyword)

        if results:
            await update.message.reply_text("🔍 Вот результаты поиска:")
            for text, photo in results:
                if photo:
                    await update.message.reply_photo(photo=open(photo, "rb"), caption=text)
                else:
                    await update.message.reply_text(text)
        else:
            await update.message.reply_text("❌ Ничего не найдено.")

        context.user_data["waiting_for_search"] = False

# 📌 Функция поиска в базе данных
def search_in_db(keyword):
    conn = sqlite3.connect("knowledge_base.db")
    cursor = conn.cursor()
    cursor.execute("SELECT text, photo FROM knowledge WHERE text LIKE ?", ('%' + keyword + '%',))
    results = cursor.fetchall()
    conn.close()
    return results

# 📌 Обработчик фото (Добавление информации с фото)
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "waiting_for_info" in context.user_data and context.user_data["waiting_for_info"]:
        if update.message.caption:
            text = update.message.caption

            # 📌 Отправляем текст в API для проверки
            response = requests.post(API_URL, json={"text": text})
            if response.status_code == 200:
                corrected_text = response.json().get("corrected_text", text)
            else:
                corrected_text = text

            # 📌 Получаем файл
            photo_file = await update.message.photo[-1].get_file()

            # Указываем путь для сохранения файла
            photo_path = f"photos/{photo_file.file_id}.jpg"
            
            # 📌 Скачиваем файл
            await photo_file.download(destination_file=photo_path)

            # 📌 Сохраняем текст и фото в базу
            save_to_db(corrected_text, photo_path)
            await update.message.reply_text(f"✅ Текст и фото сохранены:\n\n{corrected_text}")

        else:
            await update.message.reply_text("❌ Пожалуйста, добавьте подпись к фото!")

        context.user_data["waiting_for_info"] = False

# 📌 Настроим бота
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # 📌 Команда /start
    app.add_handler(CommandHandler("start", start))

    # 📌 Обработчики сообщений и фото
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(CallbackQueryHandler(button_handler))

    # 📌 Запускаем бота
    print("✅ Бот запущен!")
    app.run_webhook(
        listen="0.0.0.0",  # Прослушиваем все IP-адреса
        port=PORT,  # Порт для получения запросов
        url_path=BOT_TOKEN,  # Используем токен для уникальности пути
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}",  # Формируем URL для webhook
    )

# 📌 Создаём базу данных перед запуском
if __name__ == "__main__":
    create_database()
    main()
