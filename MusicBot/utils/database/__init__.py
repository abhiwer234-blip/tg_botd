"""
MongoDB async database layer.
Collections: users, chats, gbans, warns, welcome, settings
"""
import time
from motor.motor_asyncio import AsyncIOMotorClient
import config

_client = AsyncIOMotorClient(config.MONGO_DB_URI)
_db = _client["MusicBot"]

users_col    = _db["users"]
chats_col    = _db["chats"]
gbans_col    = _db["gbans"]
warns_col    = _db["warns"]
welcome_col  = _db["welcome"]
settings_col = _db["settings"]


class db:
    # ── Users ──────────────────────────────────────────────
    @staticmethod
    async def add_user(user_id: int):
        if not await users_col.find_one({"user_id": user_id}):
            await users_col.insert_one({"user_id": user_id, "joined": time.time()})

    @staticmethod
    async def get_all_users():
        return [u["user_id"] async for u in users_col.find()]

    @staticmethod
    async def total_users() -> int:
        return await users_col.count_documents({})

    # ── Chats ──────────────────────────────────────────────
    @staticmethod
    async def add_chat(chat_id: int):
        if not await chats_col.find_one({"chat_id": chat_id}):
            await chats_col.insert_one({"chat_id": chat_id, "joined": time.time()})

    @staticmethod
    async def get_all_chats():
        return [c["chat_id"] async for c in chats_col.find()]

    @staticmethod
    async def total_chats() -> int:
        return await chats_col.count_documents({})

    # ── GBan ───────────────────────────────────────────────
    @staticmethod
    async def gban_user(user_id: int, reason: str = ""):
        await gbans_col.update_one(
            {"user_id": user_id},
            {"$set": {"user_id": user_id, "reason": reason, "time": time.time()}},
            upsert=True,
        )

    @staticmethod
    async def ungban_user(user_id: int):
        await gbans_col.delete_one({"user_id": user_id})

    @staticmethod
    async def is_gbanned(user_id: int) -> bool:
        return bool(await gbans_col.find_one({"user_id": user_id}))

    @staticmethod
    async def get_gbanned() -> list:
        return [u["user_id"] async for u in gbans_col.find()]

    # ── Warns ──────────────────────────────────────────────
    @staticmethod
    async def add_warn(chat_id: int, user_id: int, reason: str = "") -> int:
        doc = await warns_col.find_one({"chat_id": chat_id, "user_id": user_id})
        count = (doc["count"] + 1) if doc else 1
        await warns_col.update_one(
            {"chat_id": chat_id, "user_id": user_id},
            {"$set": {"count": count, "last_reason": reason}},
            upsert=True,
        )
        return count

    @staticmethod
    async def get_warns(chat_id: int, user_id: int) -> int:
        doc = await warns_col.find_one({"chat_id": chat_id, "user_id": user_id})
        return doc["count"] if doc else 0

    @staticmethod
    async def reset_warns(chat_id: int, user_id: int):
        await warns_col.delete_one({"chat_id": chat_id, "user_id": user_id})

    # ── Welcome ────────────────────────────────────────────
    @staticmethod
    async def set_welcome(chat_id: int, text: str):
        await welcome_col.update_one(
            {"chat_id": chat_id},
            {"$set": {"text": text}},
            upsert=True,
        )

    @staticmethod
    async def get_welcome(chat_id: int) -> str | None:
        doc = await welcome_col.find_one({"chat_id": chat_id})
        return doc["text"] if doc else None

    # ── Settings ───────────────────────────────────────────
    @staticmethod
    async def get_setting(chat_id: int, key: str, default=None):
        doc = await settings_col.find_one({"chat_id": chat_id})
        return doc.get(key, default) if doc else default

    @staticmethod
    async def set_setting(chat_id: int, key: str, value):
        await settings_col.update_one(
            {"chat_id": chat_id},
            {"$set": {key: value}},
            upsert=True,
        )
