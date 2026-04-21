import logging
import sys
from pyrogram import Client
from pytgcalls import PyTgCalls
import config

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
LOGGER = logging.getLogger("MusicBot")

# ── Bot client ────────────────────────────────────────────────
app = Client(
    "MusicBot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
)

# ── Userbot client (for VC streaming) ────────────────────────
userbot = Client(
    "MusicUserbot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    session_string=config.STRING_SESSION,
)

# ── PyTgCalls ─────────────────────────────────────────────────
call_py = PyTgCalls(userbot)
