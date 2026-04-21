"""
Admin Plugin — ban/unban/kick/mute/unmute/warn/promote/demote/pin/info/gban
"""
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions, ChatPrivileges
from pyrogram.errors import UserAdminInvalid

from MusicBot import app
from MusicBot.utils.database import db
import config

MAX_WARNS = 3


# ── Admin check ───────────────────────────────────────────────
async def is_admin(client, chat_id, user_id) -> bool:
    try:
        m = await client.get_chat_member(chat_id, user_id)
        return m.status in ("administrator", "creator")
    except Exception:
        return False


def admin_cmd(func):
    async def wrapper(client: Client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply("🚫 **Admins only.**")
        await func(client, message)
    wrapper.__name__ = func.__name__
    return wrapper


def get_target(message: Message):
    reason = " ".join(message.command[2:]) if len(message.command) > 2 else "No reason"
    if message.reply_to_message:
        return message.reply_to_message.from_user.id, reason
    if len(message.command) > 1:
        return message.command[1], reason
    return None, reason


# ── /ban ──────────────────────────────────────────────────────
@app.on_message(filters.command("ban") & filters.group)
@admin_cmd
async def ban(client, message):
    target, reason = get_target(message)
    if not target:
        return await message.reply("❓ Reply to a user or provide username.")
    try:
        await client.ban_chat_member(message.chat.id, target)
        await message.reply(f"🔨 **Banned** `{target}`\n📝 {reason}")
    except Exception as e:
        await message.reply(f"❌ {e}")


# ── /unban ────────────────────────────────────────────────────
@app.on_message(filters.command("unban") & filters.group)
@admin_cmd
async def unban(client, message):
    target, _ = get_target(message)
    if not target:
        return await message.reply("❓ Provide username or reply.")
    try:
        await client.unban_chat_member(message.chat.id, target)
        await message.reply(f"✅ **Unbanned** `{target}`")
    except Exception as e:
        await message.reply(f"❌ {e}")


# ── /kick ─────────────────────────────────────────────────────
@app.on_message(filters.command("kick") & filters.group)
@admin_cmd
async def kick(client, message):
    target, reason = get_target(message)
    if not target:
        return await message.reply("❓ Reply to a user.")
    try:
        await client.ban_chat_member(message.chat.id, target)
        await client.unban_chat_member(message.chat.id, target)
        await message.reply(f"👢 **Kicked** `{target}`\n📝 {reason}")
    except Exception as e:
        await message.reply(f"❌ {e}")


# ── /mute ─────────────────────────────────────────────────────
@app.on_message(filters.command("mute") & filters.group)
@admin_cmd
async def mute(client, message):
    target, reason = get_target(message)
    if not target:
        return await message.reply("❓ Reply to a user.")
    try:
        await client.restrict_chat_member(
            message.chat.id, target,
            ChatPermissions(can_send_messages=False)
        )
        await message.reply(f"🔇 **Muted** `{target}`\n📝 {reason}")
    except Exception as e:
        await message.reply(f"❌ {e}")


# ── /unmute ───────────────────────────────────────────────────
@app.on_message(filters.command("unmute") & filters.group)
@admin_cmd
async def unmute(client, message):
    target, _ = get_target(message)
    if not target:
        return await message.reply("❓ Reply to a user.")
    try:
        await client.restrict_chat_member(
            message.chat.id, target,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            )
        )
        await message.reply(f"🔊 **Unmuted** `{target}`")
    except Exception as e:
        await message.reply(f"❌ {e}")


# ── /warn ─────────────────────────────────────────────────────
@app.on_message(filters.command("warn") & filters.group)
@admin_cmd
async def warn(client, message):
    target, reason = get_target(message)
    if not target or not message.reply_to_message:
        return await message.reply("❓ Reply to a user to warn.")
    user_id = message.reply_to_message.from_user.id
    count = await db.add_warn(message.chat.id, user_id, reason)
    if count >= MAX_WARNS:
        try:
            await client.ban_chat_member(message.chat.id, user_id)
            await db.reset_warns(message.chat.id, user_id)
            await message.reply(f"🔨 **Auto-banned** after {count} warnings!")
        except Exception as e:
            await message.reply(f"❌ Auto-ban failed: {e}")
    else:
        await message.reply(
            f"⚠️ **Warned** `{user_id}` ({count}/{MAX_WARNS})\n📝 {reason}"
        )


# ── /warns ────────────────────────────────────────────────────
@app.on_message(filters.command("warns") & filters.group)
async def warns(client, message):
    if not message.reply_to_message:
        return await message.reply("❓ Reply to a user.")
    user_id = message.reply_to_message.from_user.id
    count = await db.get_warns(message.chat.id, user_id)
    await message.reply(f"📊 **Warns:** `{count}/{MAX_WARNS}`")


# ── /promote ──────────────────────────────────────────────────
@app.on_message(filters.command("promote") & filters.group)
@admin_cmd
async def promote(client, message):
    target, _ = get_target(message)
    if not target:
        return await message.reply("❓ Reply to a user.")
    try:
        await client.promote_chat_member(
            message.chat.id, target,
            privileges=ChatPrivileges(
                can_delete_messages=True,
                can_restrict_members=True,
                can_pin_messages=True,
                can_invite_users=True,
            )
        )
        await message.reply(f"⬆️ **Promoted** `{target}`")
    except Exception as e:
        await message.reply(f"❌ {e}")


# ── /demote ───────────────────────────────────────────────────
@app.on_message(filters.command("demote") & filters.group)
@admin_cmd
async def demote(client, message):
    target, _ = get_target(message)
    if not target:
        return await message.reply("❓ Reply to a user.")
    try:
        await client.promote_chat_member(
            message.chat.id, target,
            privileges=ChatPrivileges()
        )
        await message.reply(f"⬇️ **Demoted** `{target}`")
    except Exception as e:
        await message.reply(f"❌ {e}")


# ── /pin ──────────────────────────────────────────────────────
@app.on_message(filters.command("pin") & filters.group)
@admin_cmd
async def pin(client, message):
    if not message.reply_to_message:
        return await message.reply("❓ Reply to message to pin.")
    try:
        await client.pin_chat_message(message.chat.id, message.reply_to_message.id)
        await message.reply("📌 **Pinned.**")
    except Exception as e:
        await message.reply(f"❌ {e}")


# ── /unpin ────────────────────────────────────────────────────
@app.on_message(filters.command("unpin") & filters.group)
@admin_cmd
async def unpin(client, message):
    try:
        await client.unpin_chat_message(message.chat.id)
        await message.reply("📌 **Unpinned.**")
    except Exception as e:
        await message.reply(f"❌ {e}")


# ── /info ─────────────────────────────────────────────────────
@app.on_message(filters.command("info"))
async def info(client, message):
    user = (
        message.reply_to_message.from_user
        if message.reply_to_message
        else message.from_user
    )
    try:
        member = await client.get_chat_member(message.chat.id, user.id)
        joined = member.joined_date.strftime("%d %b %Y") if member.joined_date else "Unknown"
        status = str(member.status).split(".")[-1].capitalize()
    except Exception:
        joined = "Unknown"
        status = "Unknown"
    await message.reply(
        f"👤 **User Info**\n\n"
        f"**Name:** {user.first_name} {user.last_name or ''}\n"
        f"**Username:** @{user.username or 'None'}\n"
        f"**ID:** `{user.id}`\n"
        f"**Status:** {status}\n"
        f"**Joined:** {joined}"
    )


# ── /gban (owner only) ────────────────────────────────────────
@app.on_message(filters.command("gban") & filters.user(config.OWNER_ID))
async def gban(client, message):
    target, reason = get_target(message)
    if not target:
        return await message.reply("❓ Reply to a user.")
    user_id = message.reply_to_message.from_user.id if message.reply_to_message else target
    await db.gban_user(int(user_id), reason)
    await message.reply(f"🌐 **GBanned** `{user_id}`\n📝 {reason}")


# ── /ungban (owner only) ──────────────────────────────────────
@app.on_message(filters.command("ungban") & filters.user(config.OWNER_ID))
async def ungban(client, message):
    target, _ = get_target(message)
    if not target:
        return await message.reply("❓ Reply to a user.")
    user_id = message.reply_to_message.from_user.id if message.reply_to_message else target
    await db.ungban_user(int(user_id))
    await message.reply(f"✅ **Un-GBanned** `{user_id}`")


# ── Welcome ───────────────────────────────────────────────────
@app.on_message(filters.new_chat_members)
async def welcome(client, message):
    text = await db.get_welcome(message.chat.id)
    for member in message.new_chat_members:
        if member.is_bot:
            continue
        msg = text or (
            f"👋 Welcome **{member.mention}** to **{message.chat.title}**!\n\n"
            f"🎵 Play music: `/play <song>`\n"
            f"🤖 Talk to AI: `/ask <question>` or mention me!"
        )
        await message.reply(
            msg.replace("{name}", member.mention)
               .replace("{group}", message.chat.title)
        )


@app.on_message(filters.command("setwelcome") & filters.group)
@admin_cmd
async def setwelcome(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "**Usage:** `/setwelcome Welcome {name} to {group}!`\n"
            "Variables: `{name}` `{group}`"
        )
    text = message.text.split(None, 1)[1]
    await db.set_welcome(message.chat.id, text)
    await message.reply("✅ **Welcome message updated!**")


# ── Anti-links ────────────────────────────────────────────────
@app.on_message(filters.group & filters.text)
async def anti_links(client, message):
    setting = await db.get_setting(message.chat.id, "anti_links", False)
    if not setting:
        return
    if await is_admin(client, message.chat.id, message.from_user.id):
        return
    text = message.text or ""
    if any(p in text for p in ["t.me/", "http://", "https://", "www."]):
        try:
            await message.delete()
            await client.send_message(
                message.chat.id,
                f"🚫 {message.from_user.mention}, links are not allowed here!"
            )
        except Exception:
            pass


@app.on_message(filters.command("antilinks") & filters.group)
@admin_cmd
async def toggle_antilinks(client, message):
    current = await db.get_setting(message.chat.id, "anti_links", False)
    await db.set_setting(message.chat.id, "anti_links", not current)
    status = "✅ Enabled" if not current else "❌ Disabled"
    await message.reply(f"🔗 **Anti-Links:** {status}")
