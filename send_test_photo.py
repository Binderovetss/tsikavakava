import asyncio
from telegram import Bot

TOKEN = "7368319072:AAEqEa3DWGdgA0HsqrfcTlSJaPYeCGCj52A"
CHAT_ID = "294154587"

async def send_photo():
    bot = Bot(TOKEN)
    with open("photos/test.jpg", "rb") as photo:
        await bot.send_photo(chat_id=CHAT_ID, photo=photo, caption="📸 Тестовое фото")

asyncio.run(send_photo())