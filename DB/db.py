from pymongo import MongoClient
import os
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB", "gold_loan_agent")

if not MONGO_URI:
    raise RuntimeError("❌ MONGO_URI not set. Check your .env file")

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000
)
db = client[DB_NAME]

sessions = db.sessions
messages = db.messages

def save_message(thread_id: str, role: str, content: str):
    messages.insert_one({
        "thread_id": thread_id,
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow()
    })

def get_session(thread_id: str):
    return sessions.find_one({"thread_id": thread_id})


def upsert_session(state: dict):
    sessions.update_one(
        {"thread_id": state["thread_id"]},
        {"$set": state},
        upsert=True
    )