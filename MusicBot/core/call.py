"""
Core call handler — manages active streams, queue, play/skip logic.
"""
import asyncio
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import (
    HighQualityAudio, MediumQualityAudio,
    HighQualityVideo, MediumQualityVideo,
)
from pytgcalls.exceptions import NoActiveGroupCall

from MusicBot import app, call_py, LOGGER
from MusicBot.utils.database import db

# chat_id -> list of track dicts
queues: dict[int, list] = {}
# chat_id -> current track
now_playing: dict[int, dict] = {}


def get_queue(chat_id: int) -> list:
    return queues.get(chat_id, [])


def add_to_queue(chat_id: int, track: dict):
    if chat_id not in queues:
        queues[chat_id] = []
    queues[chat_id].append(track)


def pop_from_queue(chat_id: int) -> dict | None:
    q = queues.get(chat_id, [])
    if q:
        return q.pop(0)
    return None


def clear_queue(chat_id: int):
    queues.pop(chat_id, None)
    now_playing.pop(chat_id, None)


def get_now_playing(chat_id: int) -> dict | None:
    return now_playing.get(chat_id)


async def play_next(chat_id: int):
    """Play next track in queue or leave VC if empty."""
    track = pop_from_queue(chat_id)
    if not track:
        now_playing.pop(chat_id, None)
        try:
            await call_py.leave_group_call(chat_id)
        except Exception:
            pass
        return

    now_playing[chat_id] = track
    stream = (
        AudioVideoPiped(
            track["url"],
            audio_parameters=HighQualityAudio(),
            video_parameters=HighQualityVideo(),
        )
        if track.get("video")
        else AudioPiped(track["url"], audio_parameters=HighQualityAudio())
    )

    try:
        await call_py.change_stream(chat_id, stream)
    except NoActiveGroupCall:
        try:
            await call_py.join_group_call(chat_id, stream, stream_type=track.get("stream_type"))
        except Exception as e:
            LOGGER.error(f"[CALL] Join failed: {e}")
            await app.send_message(chat_id, f"❌ **Error joining VC:** `{e}`")
            clear_queue(chat_id)
            return
    except Exception as e:
        LOGGER.error(f"[CALL] Stream change failed: {e}")
        await play_next(chat_id)
        return

    mins, secs = divmod(track.get("duration", 0), 60)
    await app.send_message(
        chat_id,
        f"🎵 **Now Playing**\n\n"
        f"**{track['title']}**\n"
        f"⏱ `{mins}:{secs:02d}` | 👤 {track['by']}\n"
        f"🎧 Source: `{track.get('source', 'Unknown')}`",
    )


@call_py.on_stream_end()
async def stream_end_handler(_, update):
    await play_next(update.chat_id)
