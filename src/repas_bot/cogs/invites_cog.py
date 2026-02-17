import discord
from discord import app_commands
from discord.ext import commands

from repas_bot.permissions import has_admin_rights
from repas_bot.services.invite_service import InviteService
from repas_bot.db.repositories.meals_repo import MealsRepo
from repas_bot.utils.time import today_iso

class InvitesCog(commands.Cog):
    def __init__(self, bot: commands.Bot, db, settings):
        self.bot = bot
        self.db = db
        self.settings = settings

    @app_commands.command(name="invite_create", description="Crée un code invité externe (admin)")
    async def invite_create(self, interaction: discord.Interaction, nom: str):
        if not interaction.guild or not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("Commande serveur uniquement.", ephemeral=True)

        if not await has_admin_rights(interaction, self.settings.admin_role_name):
            return await interaction.response.send_message("Droits insuffisants.", ephemeral=True)

        code = await InviteService(self.db).create(interaction.guild_id, nom, interaction.user.id)
        await interaction.response.send_message(f"Code invité pour **{nom}** : `{code}`", ephemeral=True)

    @app_commands.command(name="invite_join", description="Un invité externe participe via son code")
    async def invite_join(self, interaction: discord.Interaction, code: str, date: str | None = None):
        if not interaction.guild:
            return await interaction.response.send_message("Commande serveur uniquement.", ephemeral=True)

        meal_date = date or today_iso(self.settings.timezone)
        row = await MealsRepo(self.db).get_by_date(interaction.guild_id, meal_date)
        if not row:
            return await interaction.response.send_message(f"Aucun menu pour {meal_date}.", ephemeral=True)

        meal_id = int(row[0])
        name = await InviteService(self.db).set_participation_by_code(meal_id, code.strip(), "YES")
        await interaction.response.send_message(f"Participation invité OK : **{name}**", ephemeral=True)

async def setup(bot: commands.Bot):
    pass
