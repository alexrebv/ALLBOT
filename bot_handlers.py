import os
import uuid
import bcrypt
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from db import SessionLocal
from models import User, Session as DBSession

MENU_KEYS = [
    ("Данные о точке", "point_info"),
    ("Заказы", "orders"),
    ("Не принятые накладные", "not_accepted"),
    ("Вычерки (фиксация)", "crossouts_fix"),
    ("Вычерки Есалукова", "crossouts_esalukov"),
    ("Расписание заказов", "orders_schedule"),
    ("Расписание заказа воды", "water_order_schedule"),
    ("Информация о поставщике", "supplier_info"),
]

def build_main_menu():
    buttons = []
    row = []
    for i, (label, key) in enumerate(MENU_KEYS, start=1):
        row.append(InlineKeyboardButton(label, callback_data=f"menu:{key}"))
        if i % 2 == 0:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("❌ Закрыть", callback_data="menu:close")])
    return InlineKeyboardMarkup(buttons)

def build_back_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="menu:main")]])

def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    text = "Главное меню"
    keyboard = build_main_menu()
    context.bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)

def handle_menu_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    query.answer()
    if not data.startswith("menu:"):
        return
    key = data.split(":", 1)[1]
    if key == "main":
        query.edit_message_text(text="Главное меню", reply_markup=build_main_menu())
        return
    if key == "close":
        try:
            query.message.delete()
        except Exception:
            query.edit_message_text(text="Закрыто.")
        return
    submenu_texts = {
        "point_info": "Информация о точке:\n(заглушка — сюда выводим данные о точке)",
        "orders": "Заказы:\n(заглушка — список или фильтры заказов)",
        "not_accepted": "Не принятые накладные:\n(заглушка)",
        "crossouts_fix": "Вычерки (фиксация):\n(заглушка)",
        "crossouts_esalukov": "Вычерки Есалукова:\n(заглушка)",
        "orders_schedule": "Расписание заказов:\n(заглушка)",
        "water_order_schedule": "Расписание заказа воды:\n(заглушка)",
        "supplier_info": "Информация о поставщике:\n(заглушка)",
    }
    text = submenu_texts.get(key, "Раздел в разработке.")
    query.edit_message_text(text=text, reply_markup=build_back_keyboard())

# --- Simple auth handlers (command-style) ---
def cmd_login(update: Update, context: CallbackContext):
    # Usage: /login username password
    args = context.args
    if len(args) < 2:
        update.message.reply_text("Использование: /login <username> <password>")
        return
    username = args[0]
    password = args[1].encode('utf-8')
    db = SessionLocal()
    user = db.query(User).filter(User.login == username).first()
    if not user:
        update.message.reply_text("Пользователь не найден.")
        db.close()
        return
    # verify password
    if not bcrypt.checkpw(password, user.password_hash.encode('utf-8')):
        update.message.reply_text("Неверный пароль.")
        db.close()
        return
    # bind telegram id
    tg_id = str(update.effective_user.id)
    user.telegram_id = tg_id
    # create session token
    token = str(uuid.uuid4())
    expires_at = DBSession.make_expires_at(ttl_seconds=7200)
    sess = DBSession(user_id=user.id, token=token, expires_at=expires_at)
    db.add(sess)
    db.commit()
    update.message.reply_text(f"Успешно вошли. Сессия создана (TTL 2 часа). Telegram ID привязан: {tg_id}")
    db.close()

def cmd_logout(update: Update, context: CallbackContext):
    tg_id = str(update.effective_user.id)
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == tg_id).first()
    if not user:
        update.message.reply_text("Вы не привязаны или не авторизованы.")
        db.close()
        return
    # remove sessions for user
    db.query(DBSession).filter(DBSession.user_id == user.id).delete()
    user.telegram_id = None
    db.commit()
    update.message.reply_text("Вышли и отвязали Telegram ID.")
    db.close()

def cmd_whoami(update: Update, context: CallbackContext):
    tg_id = str(update.effective_user.id)
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == tg_id).first()
    if not user:
        update.message.reply_text("Вы не авторизованы.")
        db.close()
        return
    update.message.reply_text(f"Вы: {user.login} (роль id: {user.role_id})")
    db.close()
