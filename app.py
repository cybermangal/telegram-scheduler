import os
import asyncio
from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
import json
from datetime import datetime
import traceback
import threading

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME")
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

bot = Bot(BOT_TOKEN)
scheduler = BackgroundScheduler()
scheduler.start()

loop = asyncio.new_event_loop()  # Важно: создаём отдельный loop!
threading.Thread(target=loop.run_forever, daemon=True).start()

# Для хранения info о задачах
scheduled_tasks = {}

async def send_audio_async(chat_id, file_path, track_name, performer, links, job_id):
    print(f"[LOG] Попытка отправки mp3: {file_path}, {track_name}, {performer}, {links}")
    keyboard = [
        [
            InlineKeyboardButton("Паблик", url="https://vk.com/ic_beatz"),
            InlineKeyboardButton("Сайт", url=links[0]),
            InlineKeyboardButton("Beatchain", url=links[1])
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    with open(file_path, "rb") as audio_file:
        await bot.send_audio(
            chat_id=chat_id,
            audio=audio_file,
            title=track_name,
            performer=performer,
            reply_markup=reply_markup
        )
    print(f"[LOG] mp3 отправлен: {track_name}")
    # После успешной отправки удаляем таску из списка
    if job_id in scheduled_tasks:
        del scheduled_tasks[job_id]
    try:
        os.remove(file_path)
        print(f"[LOG] mp3 файл удалён: {file_path}")
    except Exception:
        pass

def schedule_send(chat_id, file_path, track_name, performer, links, scheduled_time):
    job_id = f"{track_name}_{scheduled_time.timestamp()}"
    def callback():
        try:
            print(f"[LOG] Вызван callback для mp3 '{track_name}' на {scheduled_time}")
            fut = asyncio.run_coroutine_threadsafe(
                send_audio_async(chat_id, file_path, track_name, performer, links, job_id), loop
            )
        except Exception as e:
            print("=== ERROR in callback ===")
            print(f"Exception: {e}")
            traceback.print_exc()
    print(f"[LOG] Планируем задачу: '{track_name}' на {scheduled_time}")
    scheduler.add_job(
        callback,
        trigger='date',
        run_date=scheduled_time,
        id=job_id,
        replace_existing=True
    )
    scheduled_tasks[job_id] = {
        "track_name": track_name,
        "performer": performer,
        "links": links,
        "file_path": file_path,
        "run_time": scheduled_time.strftime("%Y-%m-%d %H:%M"),
        "job_id": job_id
    }
    print(f"[LOG] Задача добавлена: '{track_name}' на {scheduled_time}")

@app.route("/send_mp3", methods=["POST"])
def send_mp3():
    try:
        print("[LOG] POST /send_mp3 вызван")
        print(f"[LOG] form data: {request.form}")

        audio = request.files['audio']
        track_name = request.form['track_name']
        performer = request.form['performer']
        links = json.loads(request.form['links'])
        scheduled_time = request.form['scheduled_time']
        chat_id = CHANNEL_USERNAME

        file_path = os.path.join(UPLOAD_FOLDER, audio.filename)
        audio.save(file_path)
        dt = datetime.strptime(scheduled_time, "%Y-%m-%d %H:%M")
        schedule_send(chat_id, file_path, track_name, performer, links, dt)
        print(f"[LOG] Принят mp3 {audio.filename} для '{track_name}' на {dt}")
        return "OK"
    except Exception as e:
        print("=== ERROR in /send_mp3 ===")
        print(f"Exception: {e}")
        traceback.print_exc()
        return f"ERROR: {e}", 500

@app.route("/tasks", methods=["GET"])
def list_tasks():
    # Возвращает список всех текущих задач
    return jsonify(list(scheduled_tasks.values()))

@app.route("/clear_tasks", methods=["POST"])
def clear_tasks():
    print("[LOG] Очистка всех задач!")
    for job_id in list(scheduled_tasks.keys()):
        try:
            scheduler.remove_job(job_id)
        except Exception:
            pass
        del scheduled_tasks[job_id]
    # Почистим папку uploads
    for f in os.listdir(UPLOAD_FOLDER):
        try:
            os.remove(os.path.join(UPLOAD_FOLDER, f))
        except Exception:
            pass
    return "CLEARED"

@app.route("/", methods=["GET"])
def hello():
    print("[LOG] GET / (проверка работоспособности)")
    return "Telegram Scheduler работает!"

if __name__ == '__main__':
    print("[LOG] Запуск Flask приложения...")
    app.run(host='0.0.0.0', port=8080)
