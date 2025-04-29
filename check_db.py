import asyncio
import asyncpg

from app.config.settings import settings


async def check_db():
    try:
        # Connect to the database
        conn = await asyncpg.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )

        # Test the connection
        await conn.execute("SELECT 1")

        await conn.close()

    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return False

    return True


if __name__ == "__main__":
    asyncio.run(check_db())

