#!/usr/bin/env python
"""
Run script for Kleinanzeigen Sniper.
This script ensures that the application is started properly and configuration is valid.
"""

import os
import sys

from dotenv import load_dotenv


def check_environment():
    """Check if environment is properly configured."""
    load_dotenv()
    
    missing_vars = []
    
    # Check required environment variables
    if not os.getenv("BOT_TOKEN"):
        missing_vars.append("BOT_TOKEN")
    
    if not os.getenv("ADMIN_USER_IDS"):
        missing_vars.append("ADMIN_USER_IDS")
    
    if missing_vars:
        print("Error: The following required environment variables are missing:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease copy .env.example to .env and configure these variables.")
        return False
    
    return True


def prepare_directories():
    """Create necessary directories if they don't exist."""
    # Create data directory
    os.makedirs("data", exist_ok=True)
    
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    return True


def main():
    """Main function to run the application."""
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Prepare directories
    if not prepare_directories():
        sys.exit(1)
    
    # Run the application
    print("Starting Kleinanzeigen Sniper...")
    
    try:
        from app.main import main
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 