import aiosqlite
from repas_bot.db.repositories.ledger_repo import LedgerRepo
from repas_bot.utils.money import cents_to_euros_str

class LedgerService:
    def __init__(self, db: aiosqlite.Connection):
        self.repo = LedgerRepo(db)

    async def charge_meal(self, guild_id: int, user_id: int, meal_id: int, price_cents: int, created_by_user_id: int) -> int:
        note = f"Repas #{meal_id}"
        return await self.repo.add_entry(guild_id, user_id, meal_id, "DEBIT", price_cents, "POSTED", note, created_by_user_id)

    async def submit_repayment(self, guild_id: int, user_id: int, amount_cents: int, note: str, created_by_user_id: int) -> int:
        # PENDING : à valider par admin
        return await self.repo.add_entry(guild_id, user_id, None, "CREDIT", amount_cents, "PENDING", note, created_by_user_id)

    async def approve(self, entry_id: int, approved_by_user_id: int) -> None:
        await self.repo.approve_entry(entry_id, approved_by_user_id)

    async def pending(self, guild_id: int):
        return await self.repo.list_pending(guild_id)

    async def balance_str(self, guild_id: int, user_id: int) -> str:
        cents = await self.repo.balance_cents(guild_id, user_id)
        return cents_to_euros_str(cents)

    async def balances_by_user(self, guild_id: int):
        return await self.repo.balances_by_user(guild_id)

    async def global_balance_str(self, guild_id: int) -> str:
        cents = await self.repo.global_balance_cents(guild_id)
        return cents_to_euros_str(cents)
