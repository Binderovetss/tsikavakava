import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os

# Your webhook URL, replace with your Fly.io URL
WEBHOOK_URL = "https://tsikavakava.fly.dev"
BOT_TOKEN = "your_bot_token_here"  # Replace with your bot token

# Configure logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Command handler for the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hello! I am your bot.')

async def main():
    # Set up the application and add a command handler
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handler
    application.add_handler(CommandHandler("start", start))

    # Set the webhook
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    
    # Run the webhook listener
    app.run_webhook(
        listen="0.0.0.0",  # Make sure the bot listens on all available IPs
        port=int(os.environ.get('PORT', 8080)),  # Use port 8080 for Fly.io
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}",  # Full webhook URL
        secret_token="your_secret_token_here",  # Optional: Set a secret token for security
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
