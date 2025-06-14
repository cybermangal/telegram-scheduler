import os
import asyncio
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Bot
from datetime import datetime
import traceback

app = Flask(__name__)

# Логируем переменные окружения (без вывода токена!)
BOT_TOKEN = os.environ.get("BOT_TOKEN", None)
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME", None)
if BOT_TOKEN:
    print("[LOG] BOT_TOKEN найден в окружении.")
else:
    print("[ERROR] BOT_TOKEN отсутствует в окружении!")
if CHANNEL_USERNAME:
    print(f"[LOG] CHANNEL_USERNAME из окружения: {CHANNEL_USERNAME}")
else:
    print("[ERROR] CHANNEL_USERNAME отсутствует в окружении!")

bot = Bot(BOT_TOKEN)
scheduler = BackgroundScheduler()
scheduler.start()

async def send_text_async(chat_id, text):
    print(f"[LOG] Попытка отправки в Telegram: chat_id={chat_id}, text='{text}'")
    await bot.send_message(chat_id=chat_id, text=text)
    print(f"[LOG] Текст успешно отправлен: '{text}' в {chat_id}")

def schedule_send(chat_id, text, scheduled_time):
    def callback():
        try:
            print(f"[LOG] Вызван callback для '{text}' на {scheduled_time}")
            asyncio.run(send_text_async(chat_id, text))
        except Exception as e:
            print("=== ERROR in callback ===")
            print(f"Exception: {e}")
            traceback.print_exc()
    print(f"[LOG] Планируем задачу: '{text}' на {scheduled_time}")
    scheduler.add_job(
        callback,
        trigger='date',
        run_date=scheduled_time
    )
    print(f"[LOG] Задача добавлена: '{text}' на {scheduled_time}")

@app.route("/send_text", methods=["POST"])
def send_text():
    try:
        print("[LOG] POST /send_text вызван")
        print(f"[LOG] form data: {request.form}")

        text = request.form['text']
        scheduled_time = request.form['scheduled_time']  # "2025-06-15 14:10"
        chat_id = CHANNEL_USERNAME
        print(f"[LOG] Получен запрос: text='{text}', scheduled_time='{scheduled_time}', chat_id='{chat_id}'")
        dt = datetime.strptime(scheduled_time, "%Y-%m-%d %H:%M")
        schedule_send(chat_id, text, dt)
        print(f"[LOG] Принят текст для отправки: '{text}' на {dt}")
        return "OK"
    except Exception as e:
        print("=== ERROR in /send_text ===")
        print(f"Exception: {e}")
        traceback.print_exc()
        return f"ERROR: {e}", 500

@app.route("/", methods=["GET"])
def hello():
    print("[LOG] GET / (проверка работоспособности)")
    return "Telegram Scheduler работает!"

if __name__ == '__main__':
    print("[LOG] Запуск Flask приложения...")
    app.run(host='0.0.0.0', port=8080)
