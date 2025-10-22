import os
from flask import Flask, request, abort
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler
from dotenv import load_dotenv

load_dotenv()

from db import init_db
import bot_handlers as handlers

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN not set in environment")

app = Flask(__name__)
bot = Bot(token=TOKEN)

dispatcher = Dispatcher(bot=bot, update_queue=None, workers=0, use_context=True)

# register handlers
dispatcher.add_handler(CommandHandler("start", handlers.start))
dispatcher.add_handler(CommandHandler("login", handlers.cmd_login))
dispatcher.add_handler(CommandHandler("logout", handlers.cmd_logout))
dispatcher.add_handler(CommandHandler("whoami", handlers.cmd_whoami))
dispatcher.add_handler(CallbackQueryHandler(handlers.handle_menu_callback))

init_db()

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    if request.method == "POST":
        update_json = request.get_json(force=True)
        update = Update.de_json(update_json, bot)
        dispatcher.process_update(update)
        return "OK", 200
    else:
        abort(403)

@app.route("/")
def index():
    return "Telegram bot is running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
