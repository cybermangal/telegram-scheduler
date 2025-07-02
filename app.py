import os
import asyncio
<<<<<<< HEAD
import threading
=======
>>>>>>> 805c0bbecf49e72affdd87d00beddb9ed6cf2445
from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
import json
from datetime import datetime
import traceback
import threading

from tasks_storage import load_all_tasks, add_task, remove_task, clear_all_tasks

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME")
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

bot = Bot(BOT_TOKEN)
scheduler = BackgroundScheduler()
scheduler.start()

<<<<<<< HEAD
loop = asyncio.new_event_loop()
threading.Thread(target=loop.run_forever, daemon=True).start()

# Для хранения info о текущих тасках в памяти
=======
loop = asyncio.new_event_loop()  # Важно: создаём отдельный loop!
threading.Thread(target=loop.run_forever, daemon=True).start()

# Для хранения info о задачах
>>>>>>> 805c0bbecf49e72affdd87d00beddb9ed6cf2445
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
<<<<<<< HEAD
    # После успешной отправки удаляем таску
    if job_id in scheduled_tasks:
        del scheduled_tasks[job_id]
    remove_task(job_id)
=======
    # После успешной отправки удаляем таску из списка
    if job_id in scheduled_tasks:
        del scheduled_tasks[job_id]
>>>>>>> 805c0bbecf49e72affdd87d00beddb9ed6cf2445
    try:
        os.remove(file_path)
        print(f"[LOG] mp3 файл удалён: {file_path}")
    except Exception:
        pass

<<<<<<< HEAD
def schedule_send(chat_id, file_path, track_name, performer, links, scheduled_time, save_to_file=True):
=======
def schedule_send(chat_id, file_path, track_name, performer, links, scheduled_time):
>>>>>>> 805c0bbecf49e72affdd87d00beddb9ed6cf2445
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
<<<<<<< HEAD
        "job_id": job_id,
        "chat_id": chat_id
    }
    if save_to_file:
        add_task(scheduled_tasks[job_id])
=======
        "job_id": job_id
    }
>>>>>>> 805c0bbecf49e72affdd87d00beddb9ed6cf2445
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
<<<<<<< HEAD
        schedule_send(chat_id, file_path, track_name, performer, links, dt, save_to_file=True)
=======
        schedule_send(chat_id, file_path, track_name, performer, links, dt)
>>>>>>> 805c0bbecf49e72affdd87d00beddb9ed6cf2445
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
<<<<<<< HEAD
    tasks = load_all_tasks()
    return jsonify(tasks)

@app.route("/clear_tasks", methods=["POST"])
def clear_tasks_api():
=======
    return jsonify(list(scheduled_tasks.values()))

@app.route("/clear_tasks", methods=["POST"])
def clear_tasks():
>>>>>>> 805c0bbecf49e72affdd87d00beddb9ed6cf2445
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
<<<<<<< HEAD
    clear_all_tasks()
=======
>>>>>>> 805c0bbecf49e72affdd87d00beddb9ed6cf2445
    return "CLEARED"

@app.route("/", methods=["GET"])
def hello():
    print("[LOG] GET / (проверка работоспособности)")
    return "Telegram Scheduler работает!"

def restore_all_tasks_on_start():
    print("[LOG] Восстановление задач из файла...")
    tasks = load_all_tasks()
    now = datetime.utcnow()
    for t in tasks:
        run_time = datetime.strptime(t["run_time"], "%Y-%m-%d %H:%M")
        if run_time > now:
            schedule_send(
                t.get("chat_id", CHANNEL_USERNAME),
                t["file_path"],
                t["track_name"],
                t["performer"],
                t["links"],
                run_time,
                save_to_file=False  # Чтобы не дублировать таск в файле!
            )
    print(f"[LOG] Восстановлено задач: {len(tasks)}")

if __name__ == '__main__':
    print("[LOG] Запуск Flask приложения...")
    restore_all_tasks_on_start()
    app.run(host='0.0.0.0', port=8080)
