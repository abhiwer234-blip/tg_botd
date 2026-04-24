"""
Utility script to generate a Pyrogram string session for MusicBot.

Usage:
  python generate_session.py
"""

import asyncio

from pyrogram import Client


def _prompt_int(label: str) -> int:
    while True:
        value = input(f"{label}: ").strip()
        try:
            return int(value)
        except ValueError:
            print("Please enter a valid number.")


async def main() -> None:
    print("=== Pyrogram String Session Generator ===")
    api_id = _prompt_int("API_ID")
    api_hash = input("API_HASH: ").strip()

    if not api_hash:
        raise SystemExit("API_HASH is required.")

    async with Client("session_generator", api_id=api_id, api_hash=api_hash, in_memory=True) as app:
        session = await app.export_session_string()

    print("\n✅ Your STRING_SESSION:\n")
    print(session)
    print("\nSave it in .env or sample.env as STRING_SESSION=<value>")


if __name__ == "__main__":
    asyncio.run(main())
