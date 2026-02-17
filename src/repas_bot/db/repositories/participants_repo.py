import aiosqlite

class ParticipantsRepo:
    def __init__(self, db: aiosqlite.Connection):
        self.db = db

    async def set_status(self, meal_id: int, user_id: int, status: str) -> None:
        await self.db.execute("""
        INSERT INTO participants(meal_id, user_id, status)
        VALUES(?, ?, ?)
        ON CONFLICT(meal_id, user_id) DO UPDATE SET
          status=excluded.status,
          updated_at=datetime('now')
        """, (meal_id, user_id, status))
        await self.db.commit()

    async def list_yes(self, meal_id: int):
        cur = await self.db.execute("""
        SELECT user_id FROM participants
        WHERE meal_id=? AND status='YES'
        """, (meal_id,))
        return [r[0] for r in await cur.fetchall()]

    async def get_status(self, meal_id: int, user_id: int):
        cur = await self.db.execute("""
        SELECT status FROM participants
        WHERE meal_id=? AND user_id=?
        """, (meal_id, user_id))
        row = await cur.fetchone()
        return row[0] if row else None

