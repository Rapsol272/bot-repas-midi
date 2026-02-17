import aiosqlite
import secrets
import string
from repas_bot.db.repositories.invites_repo import InvitesRepo

def _new_code() -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(4)) + "-" + "".join(secrets.choice(alphabet) for _ in range(4))

class InviteService:
    def __init__(self, db: aiosqlite.Connection):
        self.repo = InvitesRepo(db)

    async def create(self, guild_id: int, display_name: str, created_by_user_id: int) -> str:
        code = _new_code()
        await self.repo.create_invite(guild_id, code, display_name, created_by_user_id)
        return code

    async def set_participation_by_code(self, meal_id: int, code: str, status: str) -> str:
        row = await self.repo.get_by_code(code)
        if not row:
            raise ValueError("Code inconnu.")
        invite_id, _, display_name, is_active = row
        if not is_active:
            raise ValueError("Code inactif.")
        await self.repo.set_participation(meal_id, invite_id, status)
        return display_name
