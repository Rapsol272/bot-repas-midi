import aiosqlite

class RatingsRepo:
    def __init__(self, db: aiosqlite.Connection):
        self.db = db

    async def rate(self, guild_id: int, dish_id: int, meal_id: int, user_id: int, rating: int, comment: str) -> None:
        await self.db.execute("""
        INSERT INTO dish_ratings(guild_id, dish_id, meal_id, user_id, rating, comment)
        VALUES(?, ?, ?, ?, ?, ?)
        ON CONFLICT(guild_id, dish_id, meal_id, user_id) DO UPDATE SET
          rating=excluded.rating,
          comment=excluded.comment
        """, (guild_id, dish_id, meal_id, user_id, rating, comment))
        await self.db.commit()

    async def dish_stats(self, guild_id: int, dish_id: int):
        cur = await self.db.execute("""
        SELECT COUNT(*), AVG(rating)
        FROM dish_ratings
        WHERE guild_id=? AND dish_id=?
        """, (guild_id, dish_id))
        return await cur.fetchone()

    async def top_dishes(self, guild_id: int, limit: int = 10):
        cur = await self.db.execute("""
        SELECT d.name, COUNT(*) as n, AVG(r.rating) as avg_rating
        FROM dish_ratings r
        JOIN dishes d ON d.dish_id = r.dish_id
        WHERE r.guild_id=?
        GROUP BY r.dish_id
        HAVING n >= 2
        ORDER BY avg_rating DESC, n DESC
        LIMIT ?
        """, (guild_id, limit))
        return await cur.fetchall()
