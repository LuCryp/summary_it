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

    msg_text = message.text.strip()

    if not msg_text.startswith("BOT "):
        return

    url = msg_text.replace("BOT ", "").strip()

    bot.reply_to(message, "Przetwarzam link...")

    try:
        text, summary = process_url(url)
        
        #  dzielenie na fragmenty po 4096 znaków
        MAX_LEN = 4096
        for i in range(0, len(summary), MAX_LEN):
            fragment = summary[i:i + MAX_LEN]
            bot.reply_to(message, fragment)
            
    except Exception as e:
        bot.reply_to(message, f"Błąd: {str(e)}")


if __name__ == "__main__":
    bot.infinity_polling(timeout=20, long_polling_timeout=10)