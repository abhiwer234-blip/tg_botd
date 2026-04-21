"""
Multi-platform downloader:
  - YouTube (search + URL)
  - Spotify (converts to YT search)
  - Telegram audio/video files
  - SoundCloud
"""
import asyncio
import re
import yt_dlp

try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    import config as _cfg
    _sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=_cfg.SPOTIFY_CLIENT_ID,
        client_secret=_cfg.SPOTIFY_CLIENT_SECRET,
    )) if _cfg.SPOTIFY_CLIENT_ID else None
except ImportError:
    _sp = None

YDL_OPTS_AUDIO = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": True,
    "geo_bypass": True,
    "nocheckcertificate": True,
    "default_search": "ytsearch",
    "source_address": "0.0.0.0",
}

YDL_OPTS_VIDEO = {
    "format": "best[height<=720]",
    "quiet": True,
    "noplaylist": True,
    "geo_bypass": True,
    "nocheckcertificate": True,
    "default_search": "ytsearch",
}

SPOTIFY_RE = re.compile(r"open\.spotify\.com/(track|album|playlist)/([a-zA-Z0-9]+)")
YOUTUBE_RE = re.compile(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+")


async def _ytdl_extract(query: str, video=False) -> dict | None:
    opts = YDL_OPTS_VIDEO if video else YDL_OPTS_AUDIO
    loop = asyncio.get_event_loop()

    def _run():
        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                info = ydl.extract_info(query, download=False)
                if "entries" in info:
                    info = info["entries"][0]
                return {
                    "title":     info.get("title", "Unknown"),
                    "url":       info.get("url"),
                    "duration":  info.get("duration", 0),
                    "thumbnail": info.get("thumbnail", ""),
                    "source":    "YouTube",
                    "video":     video,
                    "yt_url":    info.get("webpage_url", ""),
                }
            except Exception:
                return None

    return await loop.run_in_executor(None, _run)


async def get_spotify_track_name(url: str) -> str | None:
    if not _sp:
        return None
    match = SPOTIFY_RE.search(url)
    if not match:
        return None
    kind, sid = match.groups()
    loop = asyncio.get_event_loop()
    try:
        if kind == "track":
            data = await loop.run_in_executor(None, lambda: _sp.track(sid))
            artists = ", ".join(a["name"] for a in data["artists"])
            return f"{data['name']} {artists}"
    except Exception:
        return None


async def search(query: str, video=False) -> dict | None:
    """
    Universal search. Accepts:
      - Plain text query
      - YouTube URL
      - Spotify track URL
    """
    # Spotify → convert to YT search
    if "spotify.com" in query:
        name = await get_spotify_track_name(query)
        if name:
            query = name
        else:
            return None

    return await _ytdl_extract(query, video=video)


async def get_playlist_tracks(url: str, limit: int = 25) -> list[dict]:
    """Returns first `limit` tracks from a YouTube playlist."""
    opts = {**YDL_OPTS_AUDIO, "noplaylist": False, "playlistend": limit}
    loop = asyncio.get_event_loop()

    def _run():
        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                tracks = []
                for entry in info.get("entries", []):
                    if entry:
                        tracks.append({
                            "title":    entry.get("title", "Unknown"),
                            "url":      entry.get("url"),
                            "duration": entry.get("duration", 0),
                            "source":   "YouTube Playlist",
                            "video":    False,
                        })
                return tracks
            except Exception:
                return []

    return await loop.run_in_executor(None, _run)
