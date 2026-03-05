from telebot import TeleBot
from utils.processing import process_url
import os
import json
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_IDS_JSON = os.getenv("TELEGRAM_USER_IDS", "[]")

# parsowanie JSON
ALLOWED_USERS = set(json.loads(ALLOWED_IDS_JSON))

bot = TeleBot(TOKEN)


@bot.message_handler(func=lambda m: True)
def handle_message(message):
    user_id = message.from_user.id

    # 🔐 whitelist
    if user_id not in ALLOWED_USERS:
        return

    text = message.text.strip()

    if not text.startswith("BOT "):
        return

    url = text.replace("BOT ", "").strip()

    bot.reply_to(message, "Przetwarzam link...")

    try:
        summary = process_url(url)
        bot.reply_to(message, summary)
    except Exception as e:
        bot.reply_to(message, f"Błąd: {str(e)}")


if __name__ == "__main__":
    bot.polling()