# Kleinanzeigen Sniper

A Telegram bot for monitoring and notifying about new listings on Kleinanzeigen.de.

## Features

- Parse Kleinanzeigen.de for new listings
- Get notifications via Telegram
- Configure custom search parameters (item name, location, radius)
- Receive detailed information about new items (photos, name, description, price, location)

## Tech Stack

- Python
- aiogram 3 (Telegram Bot API)
- aiohttp (HTTP client)
- JSON files for data storage (PostgreSQL planned for production)

## Project Structure

```
kleinanzeigen-sniper/
├── app/
│   ├── bot/           # Telegram bot handlers and utilities
│   ├── config/        # Configuration settings
│   ├── models/        # Data models
│   ├── services/      # Business logic services
│   ├── utils/         # Helper utilities
│   └── workers/       # Background workers for parsing
├── data/              # JSON storage
└── logs/              # Application logs
```

## Setup and Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and configure your settings
4. Run the application:
   ```
   python -m app.main
   ```

## Configuration

Edit the `.env` file to configure:

- `BOT_TOKEN`: Your Telegram bot token (obtained from [@BotFather](https://t.me/BotFather))
- `ADMIN_USER_IDS`: List of Telegram user IDs that have admin access
- `REQUEST_INTERVAL`: How often to check for new listings (in seconds)

## License

MIT 