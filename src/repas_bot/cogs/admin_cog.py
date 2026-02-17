import discord
from discord import app_commands
from discord.ext import commands

from repas_bot.permissions import has_admin_rights
from repas_bot.services.ledger_service import LedgerService

class AdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot, db, settings):
        self.bot = bot
        self.db = db
        self.settings = settings

    def _check_admin(self, interaction: discord.Interaction) -> bool:
        return interaction.guild and isinstance(interaction.user, discord.Member) and has_admin_rights(interaction.user, self.settings.admin_role_name)

    @app_commands.command(name="admin_pending", description="Liste les remboursements en attente (admin)")
    async def admin_pending(self, interaction: discord.Interaction):
        if not self._check_admin(interaction):
            return await interaction.response.send_message("Droits insuffisants.", ephemeral=True)

        svc = LedgerService(self.db)
        rows = await svc.pending(interaction.guild_id)
        if not rows:
            return await interaction.response.send_message("Aucun remboursement en attente.", ephemeral=True)

        txt = "\n".join([f"- entry_id={eid} user_id={uid} amount={amt/100:.2f}€ note='{note}' ({created_at})"
                         for eid, uid, amt, note, created_at in rows[:50]])
        await interaction.response.send_message(txt, ephemeral=True)

    @app_commands.command(name="admin_approve", description="Valide un remboursement (admin)")
    async def admin_approve(self, interaction: discord.Interaction, entry_id: int):
        if not self._check_admin(interaction):
            return await interaction.response.send_message("Droits insuffisants.", ephemeral=True)

        svc = LedgerService(self.db)
        await svc.approve(entry_id, interaction.user.id)
        await interaction.response.send_message(f"Remboursement validé (entry_id={entry_id}).", ephemeral=True)

async def setup(bot: commands.Bot):
    pass
