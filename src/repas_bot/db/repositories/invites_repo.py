import aiosqlite

class InvitesRepo:
    def __init__(self, db: aiosqlite.Connection):
        self.db = db

    async def create_invite(self, guild_id: int, code: str, display_name: str, created_by_user_id: int) -> int:
        cur = await self.db.execute("""
        INSERT INTO external_invites(guild_id, code, display_name, created_by_user_id)
        VALUES(?, ?, ?, ?)
        """, (guild_id, code, display_name, created_by_user_id))
        await self.db.commit()
        return cur.lastrowid

    async def get_by_code(self, code: str):
        cur = await self.db.execute("""
        SELECT invite_id, guild_id, display_name, is_active
        FROM external_invites WHERE code=?
        """, (code,))
        return await cur.fetchone()

    async def set_participation(self, meal_id: int, invite_id: int, status: str) -> None:
        await self.db.execute("""
        INSERT INTO external_participants(meal_id, invite_id, status)
        VALUES(?, ?, ?)
        ON CONFLICT(meal_id, invite_id) DO UPDATE SET
          status=excluded.status,
          updated_at=datetime('now')
        """, (meal_id, invite_id, status))
        await self.db.commit()
