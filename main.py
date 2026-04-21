"""
MusicBot — Entry Point
Loads all plugins and starts bot + userbot + PyTgCalls
"""
import asyncio
import importlib

from pyrogram import idle

from MusicBot import app, userbot, call_py, LOGGER
from MusicBot.utils.database import db
import config

PLUGINS = [
    "MusicBot.plugins.music.play",
    "MusicBot.plugins.bot.admin",
    "MusicBot.plugins.bot.ai_agent",
    "MusicBot.plugins.bot.start",
    "MusicBot.core.call",
]


async def main():
    LOGGER.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    LOGGER.info(f"  Starting {config.MUSIC_BOT_NAME}")
    LOGGER.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # Validate required vars
    missing = []
    for var in ["API_ID", "API_HASH", "BOT_TOKEN", "MONGO_DB_URI", "STRING_SESSION", "OWNER_ID"]:
        if not getattr(config, var):
            missing.append(var)
    if missing:
        LOGGER.error(f"Missing required vars: {', '.join(missing)}")
        return

    # Load banned users from DB
    try:
        config.BANNED_USERS = await db.get_gbanned()
        LOGGER.info(f"Loaded {len(config.BANNED_USERS)} gbanned users")
    except Exception as e:
        LOGGER.warning(f"Could not load gbanned users: {e}")

    # Load plugins
    LOGGER.info("Loading plugins...")
    for plugin in PLUGINS:
        try:
            importlib.import_module(plugin)
            LOGGER.info(f"  ✅ {plugin.split('.')[-1]}")
        except Exception as e:
            LOGGER.error(f"  ❌ {plugin}: {e}")

    # Start clients
    await userbot.start()
    LOGGER.info("✅ Userbot started")

    await app.start()
    me = await app.get_me()
    LOGGER.info(f"✅ Bot started: @{me.username}")

    await call_py.start()
    LOGGER.info("✅ PyTgCalls started")

    # Notify owner
    try:
        await app.send_message(
            config.LOG_GROUP_ID or config.OWNER_ID,
            f"✅ **{config.MUSIC_BOT_NAME}** started successfully!\n"
            f"👤 Bot: @{me.username}"
        )
    except Exception:
        pass

    LOGGER.info("🚀 Bot is running!")
    await idle()

    # Cleanup
    await app.stop()
    await userbot.stop()


if __name__ == "__main__":
    asyncio.run(main())
