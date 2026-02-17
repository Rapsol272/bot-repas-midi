import aiosqlite
from repas_bot.db.repositories.dishes_repo import DishesRepo
from repas_bot.utils.normalize import normalize_name

class DishService:
    def __init__(self, db: aiosqlite.Connection):
        self.repo = DishesRepo(db)

    async def add(self, guild_id: int, name: str) -> int:
        return await self.repo.upsert_dish(guild_id, name.strip(), normalize_name(name))

    async def list(self, guild_id: int):
        return await self.repo.list_dishes(guild_id)
