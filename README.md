# Kleinanzeigen Sniper

A Telegram bot for monitoring and notifying about new listings on Kleinanzeigen.de.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![aiogram 3](https://img.shields.io/badge/aiogram-3.x-blue.svg)](https://github.com/aiogram/aiogram)

## Features

- Parse Kleinanzeigen.de for new listings with nearly zero latency
- Get notifications via Telegram
- Configure custom search parameters (item name, location, price, type)
- Receive detailed information about new items (photos, name, description, price, location)

## Tech Stack

- Python
- aiogram 3 (Telegram Bot API)
- aiohttp (HTTP client)
- PostgreSQL & SQLAlchemy


## Project Structure

```
kleinanzeigen-sniper/
├── app/
│   ├── bot/           # Telegram bot handlers and utilities
│   ├── builders/      # Message builders
│   ├── config/        # Configuration settings
│   ├── db/            # Database models
│   ├── kleinanzeigen/ # Kleinanzeigen API Wrapper
│   ├── models/        # Pydantic models (deprecated and will be deleted)
│   ├── services/      # Business logic services
│   ├── utils/         # Helper utilities
│   └── workers/       # Background workers for parsing
└── logs/              # Application logs
```

## Setup and Installation

1. Clone the repository
2. Initialize virtual environment
   ```
   python3 -m venv .venv
   ```
3. Update .env file with your data
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Upgrade alembic to head
   ```
   alembic upgrade head
   ```
6. Run the application:
   ```
   python3 -m app.main
   ```

## Configuration

Edit the `.env` file to configure:

### Main settings

- `BOT_TOKEN`: Your Telegram bot token (obtained from [@BotFather](https://t.me/BotFather))
- `ADMIN_USER_IDS`: List of Telegram user IDs that have admin access
- `REQUEST_INTERVAL`: How often to check for new listings (in seconds)
- `NOTIFICATION_INTERVAL`: How often to send notifications to users (in seconds)

### Kleinanzeigen API Settings

- `KLEINANZEIGEN_CONCURRENT_REQUESTS_FOR_SCAN`: Maximum concurrent requests to Kleinanzeigen API
- `KLEINANZEIGEN_MAX_ITEMS_PER_PAGE`: Maximum length of fetched items list from Kleinanzeigen API
- `KLEINANZEIGEN_API_URL`: Link to Kleinanzeigen Backend server
- `KLEINANZEIGEN_AUTH_TOKEN`: Bearer auth token for Kleinanzeigen API
