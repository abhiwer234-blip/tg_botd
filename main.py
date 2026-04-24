"""
MusicBot — Entry Point
Loads all plugins and starts bot + userbot + PyTgCalls
"""
import asyncio
import importlib
import os

from aiohttp import web
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


async def _start_health_server():
    """
    Start a tiny HTTP server for platforms that require a bound PORT
    (e.g., Azure App Service / Railway Web Service).
    """
    try:
        port = int(os.environ.get("PORT", "0") or 0)
    except ValueError:
        LOGGER.warning("Invalid PORT value; skipping health server startup.")
        return None
    if not port:
        return None

    web_app = web.Application()

    async def root(_request):
        return web.json_response({"status": "ok", "service": config.MUSIC_BOT_NAME})

    async def healthz(_request):
        return web.Response(text="ok")

    web_app.router.add_get("/", root)
    web_app.router.add_get("/healthz", healthz)

    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()
    LOGGER.info(f"✅ Health server started on 0.0.0.0:{port}")
    return runner


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

    web_runner = None
    userbot_started = False
    app_started = False
    call_started = False
    try:
        # Start clients
        web_runner = await _start_health_server()

        await userbot.start()
        userbot_started = True
        LOGGER.info("✅ Userbot started")

        await app.start()
        app_started = True
        me = await app.get_me()
        LOGGER.info(f"✅ Bot started: @{me.username}")

        await call_py.start()
        call_started = True
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
    finally:
        # Cleanup
        if call_started:
            await call_py.stop()
        if app_started:
            await app.stop()
        if userbot_started:
            await userbot.stop()
        if web_runner:
            await web_runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
