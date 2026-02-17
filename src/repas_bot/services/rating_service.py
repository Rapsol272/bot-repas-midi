import aiosqlite
from repas_bot.db.repositories.ratings_repo import RatingsRepo

class RatingService:
    def __init__(self, db: aiosqlite.Connection):
        self.repo = RatingsRepo(db)

    async def rate(self, guild_id: int, dish_id: int, meal_id: int, user_id: int, rating: int, comment: str):
        await self.repo.rate(guild_id, dish_id, meal_id, user_id, rating, comment)

    async def stats(self, guild_id: int, dish_id: int):
        return await self.repo.dish_stats(guild_id, dish_id)

    async def top(self, guild_id: int, limit: int = 10):
        return await self.repo.top_dishes(guild_id, limit)
