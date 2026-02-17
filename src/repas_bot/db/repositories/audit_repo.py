import aiosqlite
import json

class AuditRepo:
    def __init__(self, db: aiosqlite.Connection):
        self.db = db

    async def log(self, guild_id: int, actor_user_id: int, action: str, payload: dict) -> None:
        await self.db.execute("""
        INSERT INTO audit_log(guild_id, actor_user_id, action, payload_json)
        VALUES(?, ?, ?, ?)
        """, (guild_id, actor_user_id, action, json.dumps(payload, ensure_ascii=False)))
        await self.db.commit()
