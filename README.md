# 🎵 MusicBot — Telegram Music & AI Group Manager

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/Pyrogram-2.0.106-green?style=for-the-badge&logo=telegram" />
  <img src="https://img.shields.io/badge/PyTgCalls-3.0.0-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/MongoDB-Motor-brightgreen?style=for-the-badge&logo=mongodb" />
  <img src="https://img.shields.io/badge/AI-Gemini_1.5_Flash-purple?style=for-the-badge&logo=google" />
</p>

<p align="center">
  A powerful Telegram bot that streams music/video in Voice Chats, manages groups, and chats using Google Gemini AI.
  <br/>
  Supports <b>YouTube • Spotify • SoundCloud</b>
</p>

---

## ✨ Features

- 🎵 **Music Streaming** — Play audio/video in Telegram Voice Chats
- 📋 **Queue System** — Add multiple songs, skip, pause, resume
- 🎬 **Video Support** — Stream YouTube videos in VC
- 🤖 **AI Agent** — Powered by Google Gemini 1.5 Flash
- 🛡️ **Group Management** — Ban, kick, mute, warn, promote, gban
- 🔗 **Anti-Links** — Auto-delete links in groups
- 👋 **Welcome Messages** — Custom welcome with variables
- 🌐 **Multi-platform** — YouTube, Spotify, SoundCloud support
- 🗄️ **MongoDB** — Persistent storage for users, chats, warns

---

## 📋 Commands

### 🎵 Music
| Command | Description |
|--------|-------------|
| `/play <song/URL>` | Play audio in Voice Chat |
| `/vplay <song/URL>` | Play video in Voice Chat |
| `/pause` | Pause playback |
| `/resume` | Resume playback |
| `/skip` | Skip current track |
| `/stop` | Stop and leave VC |
| `/queue` | View song queue |
| `/np` | Now playing info |

### 🛡️ Admin
| Command | Description |
|--------|-------------|
| `/ban` | Ban a user |
| `/unban` | Unban a user |
| `/kick` | Kick a user |
| `/mute` | Mute a user |
| `/unmute` | Unmute a user |
| `/warn` | Warn a user (auto-ban at 3) |
| `/warns` | Check user warns |
| `/promote` | Promote to admin |
| `/demote` | Remove admin |
| `/pin` | Pin a message |
| `/unpin` | Unpin message |
| `/info` | User info |
| `/setwelcome` | Set welcome message |
| `/antilinks` | Toggle anti-link filter |

### 🤖 AI
| Command | Description |
|--------|-------------|
| `/ask <question>` | Ask AI anything |
| `/resetai` | Clear conversation memory |
| `@mention` | Mention bot in group |
| DM the bot | Private AI chat |

### 👑 Owner Only
| Command | Description |
|--------|-------------|
| `/gban` | Global ban a user |
| `/ungban` | Remove global ban |
| `/stats` | Bot statistics |

---

## ⚙️ Required Variables

Create a `sample.env` file or set these as environment variables:

```env
# ── Required ──────────────────────────────
API_ID=12345678
API_HASH=your_api_hash_here
BOT_TOKEN=your_bot_token_here
MONGO_DB_URI=mongodb+srv://...
STRING_SESSION=your_string_session
OWNER_ID=123456789

# ── Optional ──────────────────────────────
LOG_GROUP_ID=           # Group ID to log bot events
MUSIC_BOT_NAME=MusicBot
BOT_USERNAME=your_bot_username
DURATION_LIMIT=60       # Max song duration in minutes
PLAYLIST_FETCH_LIMIT=25

# ── AI ────────────────────────────────────
GEMINI_API_KEY=your_gemini_api_key
AI_ENABLED=True

# ── Spotify ───────────────────────────────
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
```

### How to get these values:

- **API_ID & API_HASH** → [my.telegram.org](https://my.telegram.org)
- **BOT_TOKEN** → [@BotFather](https://t.me/BotFather) on Telegram
- **MONGO_DB_URI** → [mongodb.com/atlas](https://www.mongodb.com/atlas) (Free tier)
- **STRING_SESSION** → Run `python3 generate_session.py` locally
- **GEMINI_API_KEY** → [aistudio.google.com](https://aistudio.google.com)
- **SPOTIFY** → [developer.spotify.com](https://developer.spotify.com/dashboard)

---

## 🚀 Deploy Guide

---

### ☁️ Deploy on Heroku

> ⚠️ Heroku free tier is discontinued. You need a paid plan ($5/month).

**Step 1 — Create Heroku App**
1. Go to [heroku.com](https://heroku.com) → New → Create new app
2. Give it a name → Click **Create app**

**Step 2 — Set Environment Variables**
1. Go to **Settings** → **Reveal Config Vars**
2. Add all variables from the table above one by one

**Step 3 — Deploy**
```bash
# Install Heroku CLI first from heroku.com/cli
heroku login
heroku git:remote -a your-app-name
git push heroku main
```

**Step 4 — Start the bot**
```bash
heroku ps:scale worker=1
```

Or go to **Resources** tab → Enable the `worker` dyno.

> 💡 Make sure your `Procfile` contains:
> ```
> worker: python main.py
> ```

---

### 🎨 Deploy on Render

> ✅ Render has a free tier (spins down after inactivity — use paid for 24/7)

**Step 1 — Create account**
Go to [render.com](https://render.com) → Sign up with GitHub

**Step 2 — New Web Service**
1. Click **New** → **Web Service**
2. Connect your GitHub repo `tg_botd`
3. Fill in:
   - **Name:** MusicBot
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`

**Step 3 — Add Environment Variables**
Scroll to **Environment** section → Add all variables from the table above

**Step 4 — Deploy**
Click **Create Web Service** — Render will auto-deploy!

> 💡 For 24/7 uptime, choose **Starter** plan ($7/month)

---

### 🚂 Deploy on Railway

> ✅ Railway gives $5 free credit monthly — good for small bots

**Step 1 — Create account**
Go to [railway.app](https://railway.app) → Login with GitHub

**Step 2 — New Project**
1. Click **New Project** → **Deploy from GitHub repo**
2. Select your `tg_botd` repo

**Step 3 — Add Variables**
1. Click on your service → **Variables** tab
2. Click **New Variable** and add all env variables

**Step 4 — Set Start Command**
Go to **Settings** → **Deploy** → Set:
```
python main.py
```

**Step 5 — Deploy**
Railway auto-deploys on every push to main! ✅

> 💡 Add a MongoDB service directly in Railway:
> New → Database → MongoDB → Copy the connection URL

---

### 🖥️ Deploy on VPS (Ubuntu/Debian)

> ✅ Best option for 24/7 uptime and full control

**Step 1 — Connect to your VPS**
```bash
ssh root@your_server_ip
```

**Step 2 — Install dependencies**
```bash
apt update && apt upgrade -y
apt install python3 python3-pip git ffmpeg -y
```

**Step 3 — Clone your repo**
```bash
git clone https://github.com/abhiwer234-blip/tg_botd
cd tg_botd
```

**Step 4 — Install Python packages**
```bash
pip3 install -r requirements.txt
```

**Step 5 — Create .env file**
```bash
nano sample.env
```
Paste all your variables, save with `Ctrl+X → Y → Enter`

**Step 6 — Run with screen (stays running after disconnect)**
```bash
apt install screen -y
screen -S musicbot
python3 main.py
```
Press `Ctrl+A` then `D` to detach — bot keeps running!

To come back: `screen -r musicbot`

**Step 6 (Alternative) — Run with systemd (auto-restart)**
```bash
nano /etc/systemd/system/musicbot.service
```

Paste this:
```ini
[Unit]
Description=MusicBot Telegram
After=network.target

[Service]
User=root
WorkingDirectory=/root/tg_botd
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
systemctl daemon-reload
systemctl enable musicbot
systemctl start musicbot
systemctl status musicbot  # check if running
```

---

## 🐳 Deploy with Docker

```bash
# Build image
docker build -t musicbot .

# Run container
docker run -d \
  --name musicbot \
  --restart always \
  -e API_ID=your_api_id \
  -e API_HASH=your_api_hash \
  -e BOT_TOKEN=your_bot_token \
  -e MONGO_DB_URI=your_mongo_uri \
  -e STRING_SESSION=your_session \
  -e OWNER_ID=your_owner_id \
  -e GEMINI_API_KEY=your_gemini_key \
  musicbot
```

---

## 📦 Local Setup (Testing)

```bash
# Clone repo
git clone https://github.com/abhiwer234-blip/tg_botd
cd tg_botd

# Install dependencies
pip3 install -r requirements.txt

# Create env file
cp sample.env .env
# Edit .env with your values

# Run bot
python3 main.py
```

---

## 🛠️ Tech Stack

| Library | Purpose |
|--------|---------|
| `pyrogram` | Telegram Bot & Userbot client |
| `pytgcalls` | Voice Chat streaming |
| `yt-dlp` | YouTube download |
| `motor` | Async MongoDB driver |
| `google-generativeai` | Gemini AI |
| `spotipy` | Spotify API |
| `aiohttp` | Async HTTP |

---

## 📝 Notes

- Bot needs to be **admin** in the group
- Userbot (STRING_SESSION) needs to be **in the group** for VC streaming
- For Spotify, only **track URLs** work (not albums/playlists directly)
- Queue is **in-memory** — resets on bot restart

---

## 🤝 Contributing

Pull requests are welcome! For major changes, open an issue first.

---

<p align="center">Made with ❤️ by <b>abhiwer234-blip</b></p>
