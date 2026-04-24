import os
from dotenv import load_dotenv

# Load env vars in priority order:
# 1) .env (local development default)
# 2) sample.env (legacy name used by older guides)
load_dotenv(".env")
load_dotenv("sample.env")

def _int(key, default=0):
    try:
        return int(os.environ.get(key, default))
    except ValueError:
        return default

def _bool(key, default=False):
    return os.environ.get(key, str(default)).lower() == "true"

# ── Required ──────────────────────────────────────────────────
API_ID              = _int("API_ID")
API_HASH            = os.environ.get("API_HASH", "")
BOT_TOKEN           = os.environ.get("BOT_TOKEN", "")
MONGO_DB_URI        = os.environ.get("MONGO_DB_URI", "")
LOG_GROUP_ID        = _int("LOG_GROUP_ID")
OWNER_ID            = _int("OWNER_ID")
STRING_SESSION      = os.environ.get("STRING_SESSION", "")

# ── Bot Settings ──────────────────────────────────────────────
MUSIC_BOT_NAME          = os.environ.get("MUSIC_BOT_NAME", "MusicBot")
BOT_USERNAME            = os.environ.get("BOT_USERNAME", "")
DURATION_LIMIT          = _int("DURATION_LIMIT", 60)
PLAYLIST_FETCH_LIMIT    = _int("PLAYLIST_FETCH_LIMIT", 25)
PRIVATE_BOT_MODE        = _bool("PRIVATE_BOT_MODE", False)
CLEANMODE_DELETE_MINS   = _int("CLEANMODE_DELETE_MINS", 5)

# ── AI ────────────────────────────────────────────────────────
GEMINI_API_KEY  = os.environ.get("GEMINI_API_KEY", "")
AI_ENABLED      = _bool("AI_ENABLED", True)

# ── Spotify ───────────────────────────────────────────────────
SPOTIFY_CLIENT_ID     = os.environ.get("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET", "")

# ── File Limits ───────────────────────────────────────────────
TG_AUDIO_FILESIZE_LIMIT = _int("TG_AUDIO_FILESIZE_LIMIT", 104857600)
TG_VIDEO_FILESIZE_LIMIT = _int("TG_VIDEO_FILESIZE_LIMIT", 1073741824)

# ── Banned Users (loaded from DB at runtime) ──────────────────
BANNED_USERS = []
