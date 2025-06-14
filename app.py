import os
import asyncio
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
import json
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN")
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME", "@testedtesticle")
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

bot = Bot(BOT_TOKEN)
scheduler = BackgroundScheduler()
scheduler.start()

async def send_audio_async(chat_id, file_path, track_name, performer, links):
    keyboard = [[
        InlineKeyboardButton("Паблик", url="https://vk.com/ic_beatz"),
        InlineKeyboardButton("Сайт", url=links[0]),
        InlineKeyboardButton("Beatchain", url=links[1])
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    with open(file_path, "rb") as audio_file:
        await bot.send_audio(
            chat_id=chat_id,
            audio=audio_file,
            title=track_name,
            performer=performer,
            reply_markup=reply_markup
        )
    print(f"[LOG] Отправлен: {file_path}")

def schedule_send(chat_id, file_path, track_name, performer, links, scheduled_time):
    def callback():
        asyncio.run(send_audio_async(chat_id, file_path, track_name, performer, links))
    scheduler.add_job(
        callback,
        trigger='date',
        run_date=scheduled_time
    )
    print(f"[LOG] Задача добавлена: {track_name} на {scheduled_time}")

@app.route("/send_post", methods=["POST"])
def send_post():
    audio = request.files['audio']
    track_name = request.form['track_name']
    performer = request.form['performer']
    links = json.loads(request.form['links'])
    scheduled_time = request.form['scheduled_time']  # "2024-06-11 23:59"
    chat_id = CHANNEL_USERNAME

    file_path = os.path.join(UPLOAD_FOLDER, audio.filename)
    audio.save(file_path)
    dt = datetime.strptime(scheduled_time, "%Y-%m-%d %H:%M")
    schedule_send(chat_id, file_path, track_name, performer, links, dt)
    return "OK"

@app.route("/", methods=["GET"])
def hello():
    return "Telegram Scheduler работает!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
