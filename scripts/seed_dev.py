# Seed minimal pour tests locaux (optionnel)
import asyncio
import os
from dotenv import load_dotenv

from repas_bot.db.connection import create_connection
from repas_bot.db.repositories.guild_config_repo import GuildConfigRepo

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "./data/bot.db")


async def main():
    async with create_connection(DB_PATH) as db:
        repo = GuildConfigRepo(db)
        await repo.upsert_defaults(guild_id=123456789, admin_role_name="Chef")
    print("[OK] Seed done (guild_id=123456789)")


if __name__ == "__main__":
    asyncio.run(main())
