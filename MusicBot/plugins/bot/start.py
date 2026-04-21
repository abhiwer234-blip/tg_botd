from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from MusicBot import app
from MusicBot.utils.database import db
import config

START_TEXT = """
🎵 **{bot_name}** — Music + AI Group Manager

**Music Commands**
`/play` `<song/URL>` — Play audio in VC
`/vplay` `<song/URL>` — Play video in VC
`/pause` — Pause playback
`/resume` — Resume playback
`/skip` — Skip current track
`/stop` — Stop & leave VC
`/queue` — View song queue
`/np` — Now playing

**Group Admin Commands**
`/ban` `/unban` `/kick`
`/mute` `/unmute`
`/warn` `/warns`
`/promote` `/demote`
`/pin` `/unpin` `/info`
`/setwelcome` `/antilinks`

**AI Agent**
`/ask <question>` — Ask me anything
`@{username} <text>` — Mention me in group
Reply to my message — I'll continue the chat
DM me — Private AI chat
`/resetai` — Clear my memory

**Owner Commands**
`/gban` `/ungban` `/stats`
"""

@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    me = await client.get_me()
    await message.reply(
        START_TEXT.format(bot_name=config.MUSIC_BOT_NAME, username=me.username or ""),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Support", url="https://t.me/"),
             InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{me.username}?startgroup=true")]
        ])
    )


@app.on_message(filters.command("help"))
async def help_cmd(client: Client, message: Message):
    await start(client, message)


@app.on_message(filters.command("stats") & filters.user(config.OWNER_ID))
async def stats(client: Client, message: Message):
    users = await db.total_users()
    chats = await db.total_chats()
    await message.reply(
        f"📊 **Bot Stats**\n\n"
        f"👤 Total Users: `{users}`\n"
        f"💬 Total Chats: `{chats}`"
    )
