import aiosqlite
from repas_bot.db.repositories.guild_config_repo import GuildConfigRepo

class ConfigService:
    def __init__(self, db: aiosqlite.Connection):
        self.repo = GuildConfigRepo(db)

    async def ensure_guild(self, guild_id: int, admin_role_name: str, timezone: str, default_price_cents: int):
        await self.repo.upsert_defaults(guild_id, admin_role_name, timezone, default_price_cents)

    async def set_menu_channel(self, guild_id: int, channel_id: int):
        await self.repo.set_menu_channel(guild_id, channel_id)

    async def set_poll_channel(self, guild_id: int, channel_id: int):
        await self.repo.set_poll_channel(guild_id, channel_id)

    async def get(self, guild_id: int):
        return await self.repo.get(guild_id)
