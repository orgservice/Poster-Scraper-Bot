# EchoBotz - Telegram Poster Scraper Bot

## Overview
This is a powerful Telegram bot that scrapes movie/show posters from various OTT platforms and bypasses direct download links from cloud sites.

**Status**: Imported to Replit - Ready for setup

## Required Setup

### Environment Variables Needed
Before running the bot, you must provide these environment variables:

**Required:**
- `API_ID` - Get from [my.telegram.org](https://my.telegram.org)
- `API_HASH` - Get from [my.telegram.org](https://my.telegram.org)
- `BOT_TOKEN` - Get from [@BotFather](https://t.me/BotFather)
- `DATABASE_URL` - MongoDB connection string
- `OWNER_ID` - Your Telegram user ID

**Optional:**
- `SUDO_USERS` - Space-separated list of admin user IDs
- `AUTH_CHATS` - Space-separated list of authorized chat IDs
- `WEB_SERVER` - Set to "true" for web server mode (keep-alive)
- `PING_URL` - Base URL for pinging (for Koyeb/Render deployments)
- `PING_TIME` - Ping interval in seconds (default: 300)
- `PUBLIC_MODE` - Set to "true" for public access
- `TIMEZONE` - Timezone (default: Asia/Kolkata)
- `TMDB_ACCESS_TOKEN` - TMDB API token (optional, uses proxy if not set)

## Project Structure
```
echobotz/
├── core/
│   ├── EchoClient.py      # Telegram bot client
│   └── plugs.py            # Plugin loader
├── helper/
│   ├── utils/              # Utility functions
│   ├── anilist_api.py      # AniList API integration
│   ├── ott.py              # OTT platform scraping
│   ├── tmdb_helper.py      # TMDB API integration
│   └── ...
├── plugins/
│   ├── anilist.py          # Anime search plugin
│   ├── bypass.py           # DDL bypass plugin
│   ├── imdb.py             # IMDb search plugin
│   ├── poster.py           # Poster scraping plugin
│   └── ...
└── __main__.py             # Entry point

config.py                   # Configuration loader
web.py                      # Optional web server
wab.py                      # HTTP server for keep-alive
start.sh                    # Startup script
```

## Recent Changes
- Updated Telegram channels: `@EchoBotz` → `@IMAXPrime`
- Updated support group: `@NxTalks` → `@IMAXPrime`
- Updated channel URL: `https://t.me/EchoBotz` → `https://t.me/IMAXPrime`
- Updated support URL: `https://t.me/NxTalks` → `https://t.me/imaxpremiums`
- Created requirements.txt with all dependencies
- Prepared for Replit deployment

## Key Features
- **Poster Scraping**: Extract posters from OTT platforms (Netflix, Prime, Crunchyroll, etc.)
- **DDL Bypass**: Convert protected links from file hosts to direct downloads
- **IMDb Search**: Search movies and shows on IMDb
- **Anime Search**: Search anime on AniList
- **Admin Features**: Broadcasting, user authorization, logs retrieval
