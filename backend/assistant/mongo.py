import os
import uuid
import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# =====================================================
# ENV + DB CONNECTION
# =====================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise Exception("MONGO_URI not found in environment variables")
try:
    # attempt to connect (short timeout) to fail fast in dev
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    db = client["thingone"]
except Exception as e:
    import warnings
    warnings.warn(f"Could not connect to MongoDB ({e}); using in-memory fallback.")

    class InMemoryCollection:
        def __init__(self):
            self._data = []

        def insert_one(self, doc):
            self._data.append(doc.copy())

        def update_one(self, q, u, upsert=False):
            for doc in self._data:
                if all(doc.get(k) == v for k, v in q.items()):
                    if "$push" in u:
                        for field, val in u["$push"].items():
                            doc.setdefault(field, []).append(val)
                    if "$inc" in u:
                        for field, val in u["$inc"].items():
                            doc[field] = doc.get(field, 0) + val
                    return
            if upsert:
                new = q.copy()
                if "$push" in u:
                    for field, val in u["$push"].items():
                        new[field] = [val]
                if "$inc" in u:
                    for field, val in u["$inc"].items():
                        new[field] = val
                self._data.append(new)

        def find(self, q, proj=None):
            for doc in self._data:
                if all(doc.get(k) == v for k, v in q.items()):
                    yield doc.copy()

        def find_one(self, q, proj=None):
            for doc in self._data:
                if all(doc.get(k) == v for k, v in q.items()):
                    return doc.copy()

        def delete_one(self, q):
            for i, doc in enumerate(self._data):
                if all(doc.get(k) == v for k, v in q.items()):
                    self._data.pop(i)
                    return

        def delete_many(self, q):
            self._data = [d for d in self._data if not all(d.get(k) == v for k, v in q.items())]

    class InMemoryDB:
        def __init__(self):
            self.chats = InMemoryCollection()
            self.user_stats = InMemoryCollection()

    db = InMemoryDB()
    client = None

# =====================================================
# CHAT HISTORY HELPERS
# =====================================================

def create_new_chat(user_id, first_message):
    chat_id = str(uuid.uuid4())
    db.chats.insert_one({
        "user_id": user_id,
        "chat_id": chat_id,
        "title": first_message[:40],
        "messages": [],
        "created_at": datetime.datetime.utcnow()
    })
    return chat_id

def add_message(user_id, chat_id, role, content):
    db.chats.update_one(
        {"user_id": user_id, "chat_id": chat_id},
        {
            "$push": {
                "messages": {
                    "role": role,
                    "content": content,
                    "timestamp": datetime.datetime.utcnow()
                }
            }
        }
    )

def get_user_chats(user_id):
    return list(
        db.chats.find(
            {"user_id": user_id},
            {"_id": 0, "chat_id": 1, "title": 1}
        ).sort("created_at", -1)
    )

def get_chat_messages(user_id, chat_id):
    chat = db.chats.find_one(
        {"user_id": user_id, "chat_id": chat_id},
        {"_id": 0, "messages": 1}
    )
    return chat["messages"] if chat else []

def delete_chat(user_id, chat_id):
    db.chats.delete_one({"user_id": user_id, "chat_id": chat_id})

def delete_all_user_chats(user_id):
    db.chats.delete_many({"user_id": user_id})

# =====================================================
# ✅ NEW: MESSAGE LIMIT LOGIC (Phase 1)
# =====================================================

def get_message_count(user_id):
    """
    MongoDB se user ke total messages ka count nikalna
    """
    stats = db.user_stats.find_one({"user_id": user_id})
    return stats.get("count", 0) if stats else 0

def increment_message_count(user_id):
    """
    Har message ke baad count ko +1 karna
    """
    db.user_stats.update_one(
        {"user_id": user_id},
        {"$inc": {"count": 1}},
        upsert=True  # Agar user ka record nahi hai toh naya banao
    )