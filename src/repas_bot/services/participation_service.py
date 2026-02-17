import aiosqlite
from repas_bot.db.repositories.participants_repo import ParticipantsRepo

class ParticipationService:
    def __init__(self, db: aiosqlite.Connection):
        self.repo = ParticipantsRepo(db)

    async def join(self, meal_id: int, user_id: int) -> None:
        await self.repo.set_status(meal_id, user_id, "YES")

    async def leave(self, meal_id: int, user_id: int) -> None:
        await self.repo.set_status(meal_id, user_id, "NO")

    async def list_yes(self, meal_id: int):
        return await self.repo.list_yes(meal_id)
