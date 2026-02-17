import aiosqlite

class DishesRepo:
    def __init__(self, db: aiosqlite.Connection):
        self.db = db

    async def upsert_dish(self, guild_id: int, name: str, normalized_name: str) -> int:
        await self.db.execute("""
        INSERT INTO dishes(guild_id, name, normalized_name)
        VALUES(?, ?, ?)
        ON CONFLICT(guild_id, normalized_name) DO UPDATE SET
          name=excluded.name
        """, (guild_id, name, normalized_name))
        await self.db.commit()

        cur = await self.db.execute("SELECT dish_id FROM dishes WHERE guild_id=? AND normalized_name=?", (guild_id, normalized_name))
        row = await cur.fetchone()
        return int(row[0])

    async def list_dishes(self, guild_id: int):
        cur = await self.db.execute("""
        SELECT dish_id, name FROM dishes WHERE guild_id=?
        ORDER BY name ASC
        """, (guild_id,))
        return await cur.fetchall()

    async def link_meal_dish(self, meal_id: int, dish_id: int) -> None:
        await self.db.execute("""
        INSERT OR IGNORE INTO meal_dishes(meal_id, dish_id)
        VALUES(?, ?)
        """, (meal_id, dish_id))
        await self.db.commit()

    async def list_meal_dishes(self, meal_id: int):
        cur = await self.db.execute("""
        SELECT d.dish_id, d.name
        FROM meal_dishes md
        JOIN dishes d ON d.dish_id = md.dish_id
        WHERE md.meal_id=?
        ORDER BY d.name
        """, (meal_id,))
        return await cur.fetchall()
