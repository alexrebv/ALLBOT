# Telegram Render Bot
Репозиторий содержит пример Telegram-бота на Flask, готового к деплою на Render с использованием webhook.

Сценарии:
- Главное меню с inline-кнопками, при нажатии меню редактируется (предыдущее скрывается)
- Простой логин: `/login <username> <password>` — привязка Telegram ID и создание сессии TTL=2 часа
- База: SQLAlchemy (по умолчанию sqlite). В продакшне используйте Postgres и DATABASE_URL в переменных окружения.

Как развернуть:
1. Создайте репозиторий на GitHub и загрузите файлы.
2. Подключите репозиторий к Render (Web Service).
3. Добавьте переменные окружения: TELEGRAM_TOKEN, WEBHOOK_URL, DATABASE_URL.
4. После деплоя выполните `python set_webhook.py` локально или через Render Shell.

Команды бота (примеры):
- /start - показать главное меню
- /login username password - авторизация и привязка Telegram ID (создаёт сессию на 2 часа)
- /logout - удалить сессию
- /whoami - показать текущего авторизованного пользователя (по Telegram ID)
