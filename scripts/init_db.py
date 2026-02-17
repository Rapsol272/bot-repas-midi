import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

from repas_bot.db.migrations import apply_migrations
from repas_bot.db.connection import create_connection

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "./data/bot.db")


async def main() -> None:
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    async with create_connection(DB_PATH) as db:
        await apply_migrations(db, migrations_dir="./migrations")
    print(f"[OK] DB init + migrations applied: {DB_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
