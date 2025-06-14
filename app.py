import os
import asyncio
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Bot
from datetime import datetime
import traceback

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN")
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME", "@testedtesticle")

bot = Bot(BOT_TOKEN)
scheduler = BackgroundScheduler()
scheduler.start()

async def send_text_async(chat_id, text):
    print(f"[LOG] Отправляю текст: {text}")
    await bot.send_message(chat_id=chat_id, text=text)
    print(f"[LOG] Текст успешно отправлен: {text}")

def schedule_send(chat_id, text, scheduled_time):
    def callback():
        try:
            print(f"[LOG] Вызван callback для '{text}' на {scheduled_time}")
            asyncio.run(send_text_async(chat_id, text))
        except Exception as e:
            print("=== ERROR in callback ===")
            print(f"Exception: {e}")
            traceback.print_exc()
    scheduler.add_job(
        callback,
        trigger='date',
        run_date=scheduled_time
    )
    print(f"[LOG] Задача добавлена: '{text}' на {scheduled_time}")

@app.route("/send_text", methods=["POST"])
def send_text():
    try:
        text = request.form['text']
        scheduled_time = request.form['scheduled_time']  # "2025-06-15 13:00"
        chat_id = CHANNEL_USERNAME
        dt = datetime.strptime(scheduled_time, "%Y-%m-%d %H:%M")
        schedule_send(chat_id, text, dt)
        print(f"[LOG] Принят текст для отправки: '{text}'")
        return "OK"
    except Exception as e:
        print("=== ERROR in /send_text ===")
        print(f"Exception: {e}")
        traceback.print_exc()
        return f"ERROR: {e}", 500

@app.route("/", methods=["GET"])
def hello():
    return "Telegram Scheduler работает!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
