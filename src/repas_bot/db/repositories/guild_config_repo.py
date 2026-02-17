import aiosqlite

class GuildConfigRepo:
    def __init__(self, db: aiosqlite.Connection):
        self.db = db

    async def upsert_defaults(self, guild_id: int, admin_role_name: str, timezone: str = "Europe/Paris", default_meal_price_cents: int = 500) -> None:
        await self.db.execute("""
        INSERT INTO guild_config(guild_id, admin_role_name, timezone, default_meal_price_cents)
        VALUES(?, ?, ?, ?)
        ON CONFLICT(guild_id) DO UPDATE SET
          admin_role_name=excluded.admin_role_name,
          timezone=excluded.timezone,
          default_meal_price_cents=excluded.default_meal_price_cents
        """, (guild_id, admin_role_name, timezone, default_meal_price_cents))
        await self.db.commit()

    async def get(self, guild_id: int):
        cur = await self.db.execute("SELECT guild_id, admin_role_name, timezone, default_meal_price_cents, menu_channel_id FROM guild_config WHERE guild_id=?", (guild_id,))
        return await cur.fetchone()

    async def set_menu_channel(self, guild_id: int, channel_id: int) -> None:
        await self.db.execute("""
        INSERT INTO guild_config(guild_id, menu_channel_id)
        VALUES(?, ?)
        ON CONFLICT(guild_id) DO UPDATE SET menu_channel_id=excluded.menu_channel_id
        """, (guild_id, channel_id))
        await self.db.commit()
