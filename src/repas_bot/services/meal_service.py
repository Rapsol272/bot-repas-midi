import aiosqlite
from repas_bot.db.repositories.meals_repo import MealsRepo
from repas_bot.db.repositories.dishes_repo import DishesRepo
from repas_bot.utils.normalize import normalize_name

class MealService:
    def __init__(self, db: aiosqlite.Connection):
        self.meals = MealsRepo(db)
        self.dishes = DishesRepo(db)

    async def upsert_menu(self, guild_id: int, meal_date: str, title: str, description: str, price_cents: int, created_by_user_id: int) -> int:
        return await self.meals.upsert_meal(guild_id, meal_date, title, description, price_cents, created_by_user_id)

    async def add_dish_to_meal(self, guild_id: int, meal_id: int, dish_name: str) -> int:
        norm = normalize_name(dish_name)
        dish_id = await self.dishes.upsert_dish(guild_id, dish_name.strip(), norm)
        await self.dishes.link_meal_dish(meal_id, dish_id)
        return dish_id
