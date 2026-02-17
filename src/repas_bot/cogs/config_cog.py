import discord
from discord import app_commands
from discord.ext import commands

from repas_bot.permissions import has_admin_rights
from repas_bot.services.config_service import ConfigService

class ConfigCog(commands.Cog):
    def __init__(self, bot: commands.Bot, db, settings):
        self.bot = bot
        self.db = db
        self.settings = settings

    @app_commands.command(name="config_menu_channel", description="Définit le salon où poster le menu")
    async def config_menu_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.guild or not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("Commande serveur uniquement.", ephemeral=True)

        if not await has_admin_rights(interaction, self.settings.admin_role_name):
            return await interaction.response.send_message("Droits insuffisants.", ephemeral=True)

        svc = ConfigService(self.db)
        await svc.ensure_guild(interaction.guild_id, self.settings.admin_role_name, self.settings.timezone, self.settings.default_meal_price_cents)
        await svc.set_menu_channel(interaction.guild_id, channel.id)
        await interaction.response.send_message(f"Salon menu défini : {channel.mention}", ephemeral=True)

async def setup(bot: commands.Bot):
    # setup géré dans app.py
    pass
