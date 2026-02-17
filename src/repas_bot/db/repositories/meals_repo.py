import aiosqlite

class MealsRepo:
    def __init__(self, db: aiosqlite.Connection):
        self.db = db

    async def upsert_meal(self, guild_id: int, meal_date: str, title: str, description: str, price_cents: int, created_by_user_id: int) -> int:
        # insert or update
        await self.db.execute("""
        INSERT INTO meals(guild_id, meal_date, title, description, price_cents, created_by_user_id)
        VALUES(?, ?, ?, ?, ?, ?)
        ON CONFLICT(guild_id, meal_date) DO UPDATE SET
          title=excluded.title,
          description=excluded.description,
          price_cents=excluded.price_cents
        """, (guild_id, meal_date, title, description, price_cents, created_by_user_id))
        await self.db.commit()

        cur = await self.db.execute("SELECT meal_id FROM meals WHERE guild_id=? AND meal_date=?", (guild_id, meal_date))
        row = await cur.fetchone()
        return int(row[0])

    async def get_by_date(self, guild_id: int, meal_date: str):
        cur = await self.db.execute("""
        SELECT meal_id, meal_date, title, description, price_cents, status
        FROM meals WHERE guild_id=? AND meal_date=?
        """, (guild_id, meal_date))
        return await cur.fetchone()

    async def close_meal(self, meal_id: int) -> None:
        await self.db.execute("""
        UPDATE meals SET status='CLOSED', closed_at=datetime('now')
        WHERE meal_id=?
        """, (meal_id,))
        await self.db.commit()
