import os
import requests
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# 📌 Замените на свой API URL (Render)
API_URL = "https://text-corrector-wubj.onrender.com"  # 🔹 Вставь свою ссылку с Render!

# 📌 Замените на свой Telegram Bot Token
BOT_TOKEN = "7368319072:AAGRGJU9NqchsjSMGHdVSrKGZEXYfyyRiUE"

# 📌 Подключаем базу данных SQLite
DB_FILE = "knowledge_base.db"

# 📌 Функция для создания базы данных (если её нет)
def create_database():
    conn = sqlite3.connect(DB_FILE)
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
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO knowledge (text, photo) VALUES (?, ?)", (text, photo_path))
    conn.commit()
    conn.close()

# 📌 Стартовое меню
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📝 Додати інформацію", callback_data="add_info")],
        [InlineKeyboardButton("🔍 Знайти інформацію", callback_data="search_info")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🔹 Виберіть дію:", reply_markup=reply_markup)

# 📌 Обработчик нажатий на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "add_info":
        context.user_data["waiting_for_info"] = True
        await query.message.reply_text("📌 Надішліть текст (і фото, якщо потрібно).")
    
    elif query.data == "search_info":
        context.user_data["waiting_for_search"] = True
        await query.message.reply_text("🔍 Введіть ключове слово для пошуку.")

# 📌 Обработчик сообщений (Добавление информации)
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
        await update.message.reply_text(f"✅ Текст додано до бази знань:\n\n{corrected_text}")

        # 📌 Сбрасываем флаг
        context.user_data["waiting_for_info"] = False

    elif "waiting_for_search" in context.user_data and context.user_data["waiting_for_search"]:
        keyword = update.message.text
        results = search_in_db(keyword)

        if results:
            await update.message.reply_text("🔍 Ось результати пошуку:")
            for text, photo in results:
                if photo:
                    await update.message.reply_photo(photo=open(photo, "rb"), caption=text)
                else:
                    await update.message.reply_text(text)
        else:
            await update.message.reply_text("❌ Нічого не знайдено.")

        context.user_data["waiting_for_search"] = False

# 📌 Функция поиска в базе данных
def search_in_db(keyword):
    conn = sqlite3.connect(DB_FILE)
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

            # 📌 Загружаем фото
            photo_file = await update.message.photo[-1].get_file()
            photo_path = f"photos/{photo_file.file_id}.jpg"
            await photo_file.download(photo_path)

            # 📌 Сохраняем текст и фото в базу
            save_to_db(corrected_text, photo_path)
            await update.message.reply_text(f"✅ Текст і фото збережені:\n\n{corrected_text}")

        else:
            await update.message.reply_text("❌ Будь ласка, додайте підпис до фото!")

        context.user_data["waiting_for_info"] = False

# 📌 Настраиваем бота
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # 📌 Команда /start
    app.add_handler(CommandHandler("start", start))

    # 📌 Обработчики сообщений и фото
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(CallbackQueryHandler(button_handler))

    # 📌 Запускаем бота
    print("✅ Бот запущений!")
    app.run_polling()

# 📌 Создаём базу данных перед запуском
if __name__ == "__main__":
    create_database()
    main()
