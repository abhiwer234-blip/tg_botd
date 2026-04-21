"""
Music Plugin — /play /vplay /pause /resume /skip /stop /queue /np /playlist
"""
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from MusicBot import app
from MusicBot.core.call import (
    add_to_queue, get_queue, get_now_playing,
    clear_queue, play_next, now_playing
)
from MusicBot.utils.platforms import search, get_playlist_tracks
from MusicBot.utils.database import db
import config


def is_url(text: str) -> bool:
    return text.startswith("http://") or text.startswith("https://")


async def _play(message: Message, video=False):
    if len(message.command) < 2:
        await message.reply(
            f"❓ **Usage:** `{'/' + message.command[0]} <song name or URL>`\n\n"
            "Supports: YouTube, Spotify, SoundCloud"
        )
        return

    query = " ".join(message.command[1:])
    chat_id = message.chat.id
    by = message.from_user.mention

    msg = await message.reply("🔍 **Searching...**")

    # Playlist check
    if "playlist" in query and is_url(query):
        tracks = await get_playlist_tracks(query, limit=config.PLAYLIST_FETCH_LIMIT)
        if not tracks:
            await msg.edit("❌ Could not fetch playlist.")
            return
        for t in tracks:
            t["by"] = by
            add_to_queue(chat_id, t)
        if chat_id not in now_playing:
            await play_next(chat_id)
        await msg.edit(f"✅ Added **{len(tracks)} tracks** from playlist to queue!")
        return

    track = await search(query, video=video)
    if not track or not track.get("url"):
        await msg.edit("❌ **Track not found.** Try a different query.")
        return

    duration_mins = track["duration"] // 60
    if duration_mins > config.DURATION_LIMIT:
        await msg.edit(f"❌ Track exceeds **{config.DURATION_LIMIT} min** limit.")
        return

    track["by"] = by
    add_to_queue(chat_id, track)

    if chat_id not in now_playing:
        await msg.delete()
        await play_next(chat_id)
    else:
        q_len = len(get_queue(chat_id))
        mins, secs = divmod(track["duration"], 60)
        await msg.edit(
            f"✅ **Added to Queue** #{q_len}\n\n"
            f"**{track['title']}**\n"
            f"⏱ `{mins}:{secs:02d}` | 🎧 {track['source']}"
        )

    await db.add_user(message.from_user.id)
    await db.add_chat(chat_id)


# ── /play ──────────────────────────────────────────────────────
@app.on_message(filters.command(["play", "p"]) & filters.group)
async def play_cmd(client: Client, message: Message):
    await _play(message, video=False)


# ── /vplay (video) ─────────────────────────────────────────────
@app.on_message(filters.command(["vplay", "vp"]) & filters.group)
async def vplay_cmd(client: Client, message: Message):
    await _play(message, video=True)


# ── /pause ─────────────────────────────────────────────────────
@app.on_message(filters.command("pause") & filters.group)
async def pause_cmd(_, message: Message):
    from MusicBot import call_py
    try:
        await call_py.pause_stream(message.chat.id)
        await message.reply("⏸ **Paused.**")
    except Exception as e:
        await message.reply(f"❌ {e}")


# ── /resume ────────────────────────────────────────────────────
@app.on_message(filters.command("resume") & filters.group)
async def resume_cmd(_, message: Message):
    from MusicBot import call_py
    try:
        await call_py.resume_stream(message.chat.id)
        await message.reply("▶️ **Resumed.**")
    except Exception as e:
        await message.reply(f"❌ {e}")


# ── /skip ──────────────────────────────────────────────────────
@app.on_message(filters.command(["skip", "s"]) & filters.group)
async def skip_cmd(_, message: Message):
    chat_id = message.chat.id
    if chat_id not in now_playing:
        await message.reply("❌ Nothing is playing.")
        return
    await message.reply("⏭ **Skipping...**")
    await play_next(chat_id)


# ── /stop ──────────────────────────────────────────────────────
@app.on_message(filters.command("stop") & filters.group)
async def stop_cmd(_, message: Message):
    from MusicBot import call_py
    chat_id = message.chat.id
    clear_queue(chat_id)
    try:
        await call_py.leave_group_call(chat_id)
    except Exception:
        pass
    await message.reply("⏹ **Stopped and left VC.**")


# ── /queue ─────────────────────────────────────────────────────
@app.on_message(filters.command(["queue", "q"]) & filters.group)
async def queue_cmd(_, message: Message):
    chat_id = message.chat.id
    tracks = get_queue(chat_id)
    np = get_now_playing(chat_id)

    if not np and not tracks:
        await message.reply("📭 **Queue is empty.**")
        return

    text = ""
    if np:
        mins, secs = divmod(np.get("duration", 0), 60)
        text += f"▶️ **Now Playing:**\n`{np['title']}` — `{mins}:{secs:02d}`\n\n"

    if tracks:
        text += "📋 **Up Next:**\n"
        for i, t in enumerate(tracks[:10], 1):
            mins, secs = divmod(t.get("duration", 0), 60)
            text += f"`{i}.` {t['title']} — `{mins}:{secs:02d}`\n"
        if len(tracks) > 10:
            text += f"\n_...and {len(tracks) - 10} more_"

    await message.reply(text)


# ── /np (now playing) ──────────────────────────────────────────
@app.on_message(filters.command(["np", "now"]) & filters.group)
async def np_cmd(_, message: Message):
    np = get_now_playing(message.chat.id)
    if not np:
        await message.reply("❌ Nothing is playing right now.")
        return
    mins, secs = divmod(np.get("duration", 0), 60)
    await message.reply(
        f"🎵 **Now Playing**\n\n"
        f"**{np['title']}**\n"
        f"⏱ `{mins}:{secs:02d}` | 👤 {np.get('by', 'Unknown')}\n"
        f"🎧 Source: `{np.get('source', 'Unknown')}`"
    )
