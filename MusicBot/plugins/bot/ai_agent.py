"""
AI Agent Plugin — Gemini powered
Triggers: /ask, @mention, DM, reply to bot
"""
import asyncio
from collections import defaultdict, deque
from pyrogram import Client, filters
from pyrogram.types import Message
import google.generativeai as genai

from MusicBot import app
import config

# ── Setup Gemini ──────────────────────────────────────────────
if config.GEMINI_API_KEY:
    genai.configure(api_key=config.GEMINI_API_KEY)
    _model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=(
            f"You are {config.MUSIC_BOT_NAME}, a smart and friendly Telegram assistant. "
            "You manage music in voice chats and help group members. "
            "Keep replies concise. Support Hindi, English, and Hinglish naturally. "
            "Music commands: /play, /vplay, /pause, /resume, /skip, /stop, /queue, /np. "
            "Admin commands: /ban, /kick, /mute, /warn, /promote, /demote, /pin."
        ),
    )
else:
    _model = None

# ── Per-user conversation memory ─────────────────────────────
_history: dict[int, deque] = defaultdict(lambda: deque(maxlen=20))


def _add(user_id, role, text):
    _history[user_id].append({"role": role, "parts": [{"text": text}]})


def _get_history(user_id):
    return list(_history[user_id])


async def ask_ai(user_id: int, text: str, ctx: str = "") -> str:
    if not _model:
        return "⚠️ AI is not configured. Please set `GEMINI_API_KEY`."
    try:
        full = f"{ctx}\n\n{text}".strip() if ctx else text
        _add(user_id, "user", full)
        response = _model.generate_content(_get_history(user_id))
        reply = response.text.strip()
        _add(user_id, "model", reply)
        return reply
    except Exception as e:
        return f"⚠️ AI error: `{str(e)[:200]}`"


# ── /ask ──────────────────────────────────────────────────────
@app.on_message(filters.command("ask"))
async def ask_cmd(client: Client, message: Message):
    if not config.AI_ENABLED:
        return
    if len(message.command) < 2:
        return await message.reply("💬 **Usage:** `/ask <your question>`")
    query = " ".join(message.command[1:])
    ctx = f"[Group: {message.chat.title}]" if message.chat.type != "private" else ""
    await client.send_chat_action(message.chat.id, "typing")
    reply = await ask_ai(message.from_user.id, query, ctx)
    await message.reply(reply)


# ── /resetai ──────────────────────────────────────────────────
@app.on_message(filters.command("resetai"))
async def resetai_cmd(_, message: Message):
    _history[message.from_user.id].clear()
    await message.reply("🔄 **Conversation memory cleared!**")


# ── DM auto reply ─────────────────────────────────────────────
@app.on_message(
    filters.private
    & filters.text
    & ~filters.command(["start", "help", "ask", "resetai"])
)
async def dm_reply(client: Client, message: Message):
    if not config.AI_ENABLED:
        return
    await client.send_chat_action(message.chat.id, "typing")
    reply = await ask_ai(message.from_user.id, message.text)
    await message.reply(reply)


# ── Group mention / reply to bot ──────────────────────────────
SKIP_CMDS = [
    "ask", "play", "vplay", "pause", "resume", "skip", "stop",
    "queue", "np", "ban", "kick", "mute", "unmute", "warn", "warns",
    "promote", "demote", "pin", "unpin", "info", "gban", "ungban",
    "setwelcome", "antilinks", "resetai", "start", "help", "stats"
]

@app.on_message(filters.group & filters.text & ~filters.command(SKIP_CMDS))
async def group_mention(client: Client, message: Message):
    if not config.AI_ENABLED:
        return

    bot_me = await client.get_me()
    text = message.text or ""

    is_mention = (
        message.entities
        and any(
            e.type.value == "mention"
            and text[e.offset:e.offset + e.length].lstrip("@").lower()
            == (bot_me.username or "").lower()
            for e in message.entities
        )
    )
    is_reply = (
        message.reply_to_message
        and message.reply_to_message.from_user
        and message.reply_to_message.from_user.id == bot_me.id
    )

    if not (is_mention or is_reply):
        return

    query = text.replace(f"@{bot_me.username}", "").strip() if bot_me.username else text
    if not query:
        return await message.reply("Haan bolo! Kya help chahiye? 😊")

    await client.send_chat_action(message.chat.id, "typing")
    reply = await ask_ai(
        message.from_user.id,
        query,
        f"[Group: {message.chat.title}]"
    )
    await message.reply(reply)
