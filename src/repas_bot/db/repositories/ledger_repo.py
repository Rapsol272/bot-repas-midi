import aiosqlite

class LedgerRepo:
    def __init__(self, db: aiosqlite.Connection):
        self.db = db

    async def add_entry(self, guild_id: int, user_id: int, meal_id: int | None, entry_type: str, amount_cents: int, status: str, note: str, created_by_user_id: int) -> int:
        cur = await self.db.execute("""
        INSERT INTO ledger_entries(guild_id, user_id, meal_id, entry_type, amount_cents, status, note, created_by_user_id)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?)
        """, (guild_id, user_id, meal_id, entry_type, amount_cents, status, note, created_by_user_id))
        await self.db.commit()
        return cur.lastrowid

    async def approve_entry(self, entry_id: int, approved_by_user_id: int) -> None:
        await self.db.execute("""
        UPDATE ledger_entries
        SET status='POSTED', approved_by_user_id=?, approved_at=datetime('now')
        WHERE entry_id=? AND status='PENDING'
        """, (approved_by_user_id, entry_id))
        await self.db.commit()

    async def list_pending(self, guild_id: int):
        cur = await self.db.execute("""
        SELECT entry_id, user_id, amount_cents, note, created_at
        FROM ledger_entries
        WHERE guild_id=? AND status='PENDING'
        ORDER BY created_at ASC
        """, (guild_id,))
        return await cur.fetchall()

    async def balance_cents(self, guild_id: int, user_id: int) -> int:
        cur = await self.db.execute("""
        SELECT
          COALESCE(SUM(CASE WHEN entry_type='DEBIT' THEN amount_cents ELSE 0 END),0) -
          COALESCE(SUM(CASE WHEN entry_type='CREDIT' THEN amount_cents ELSE 0 END),0) +
          COALESCE(SUM(CASE WHEN entry_type='ADJUST' THEN amount_cents ELSE 0 END),0)
        FROM ledger_entries
        WHERE guild_id=? AND user_id=? AND status='POSTED'
        """, (guild_id, user_id))
        row = await cur.fetchone()
        return int(row[0] or 0)
