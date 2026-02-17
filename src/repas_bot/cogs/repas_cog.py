import discord
from discord import app_commands
from discord.ext import commands

from repas_bot.db.repositories.meals_repo import MealsRepo
from repas_bot.services.participation_service import ParticipationService
from repas_bot.services.ledger_service import LedgerService
from repas_bot.utils.time import today_iso

class RepasCog(commands.Cog):
    def __init__(self, bot: commands.Bot, db, settings):
        self.bot = bot
        self.db = db
        self.settings = settings

    async def _get_today_meal(self, guild_id: int, date: str | None = None):
        meal_date = date or today_iso(self.settings.timezone)
        row = await MealsRepo(self.db).get_by_date(guild_id, meal_date)
        return meal_date, row

    @app_commands.command(name="repas_join", description="Je participe au repas (crée la dette)")
    async def repas_join(self, interaction: discord.Interaction, date: str | None = None):
        if not interaction.guild:
            return await interaction.response.send_message("Commande serveur uniquement.", ephemeral=True)

        meal_date, row = await self._get_today_meal(interaction.guild_id, date)
        if not row:
            return await interaction.response.send_message(f"Aucun menu pour {meal_date}.", ephemeral=True)

        meal_id, _, _, _, price_cents, status = row
        if status != "OPEN":
            return await interaction.response.send_message("Repas clôturé.", ephemeral=True)

        part = ParticipationService(self.db)
        await part.join(meal_id, interaction.user.id)

        ledger = LedgerService(self.db)
        await ledger.charge_meal(interaction.guild_id, interaction.user.id, meal_id, int(price_cents), interaction.user.id)

        await interaction.response.send_message("Participation enregistrée + dette ajoutée.", ephemeral=True)

    @app_commands.command(name="repas_leave", description="Je ne participe pas")
    async def repas_leave(self, interaction: discord.Interaction, date: str | None = None):
        if not interaction.guild:
            return await interaction.response.send_message("Commande serveur uniquement.", ephemeral=True)

        meal_date, row = await self._get_today_meal(interaction.guild_id, date)
        if not row:
            return await interaction.response.send_message(f"Aucun menu pour {meal_date}.", ephemeral=True)

        meal_id = int(row[0])
        part = ParticipationService(self.db)
        await part.leave(meal_id, interaction.user.id)
        await interaction.response.send_message("Ok, noté (NO).", ephemeral=True)

async def setup(bot: commands.Bot):
    pass
