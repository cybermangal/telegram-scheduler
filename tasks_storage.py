import os
from pymongo import MongoClient

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("MONGO_DB", "telegram_scheduler")

client = MongoClient(MONGO_URL)
db = client[DB_NAME]
tasks_collection = db["scheduled_tasks"]

def load_all_tasks():
    tasks = list(tasks_collection.find({}, {"_id": 0}))
    return tasks

def save_all_tasks(tasks):
    tasks_collection.delete_many({})
    if tasks:
        tasks_collection.insert_many(tasks)

def add_task(task):
    tasks_collection.insert_one(task)

def remove_task(job_id):
    tasks_collection.delete_many({"job_id": job_id})

def clear_all_tasks():
    tasks_collection.delete_many({})
