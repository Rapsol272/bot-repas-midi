import aiosqlite
from repas_bot.db.repositories.audit_repo import AuditRepo

class AuditService:
    def __init__(self, db: aiosqlite.Connection):
        self.repo = AuditRepo(db)

    async def log(self, guild_id: int, actor_user_id: int, action: str, payload: dict):
        await self.repo.log(guild_id, actor_user_id, action, payload)
