import json
import os
from datetime import datetime

TASKS_FILE = "scheduled_tasks.json"

def load_all_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return []

def save_all_tasks(tasks):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

def add_task(task):
    tasks = load_all_tasks()
    tasks.append(task)
    save_all_tasks(tasks)

def remove_task(job_id):
    tasks = load_all_tasks()
    tasks = [t for t in tasks if t["job_id"] != job_id]
    save_all_tasks(tasks)

def clear_all_tasks():
    save_all_tasks([])
