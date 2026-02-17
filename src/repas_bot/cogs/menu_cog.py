import discord
from discord import app_commands
from discord.ext import commands

from repas_bot.services.meal_service import MealService
from repas_bot.services.config_service import ConfigService
from repas_bot.ui.embeds import menu_embed
from repas_bot.utils.time import today_iso
from repas_bot.utils.money import euros_to_cents
from repas_bot.permissions import has_admin_rights
from repas_bot.ui.views import MealParticipationView



class MenuCog(commands.Cog):
    def __init__(self, bot: commands.Bot, db, settings):
        self.bot = bot
        self.db = db
        self.settings = settings

    @app_commands.command(name="menu_set", description="Crée/met à jour le menu du jour (admin)")
    @app_commands.describe(
        titre="Titre du menu",
        description="Détails",
        prix="Prix en euros (ex: 6.0). Si vide -> prix par défaut"
    )
    async def menu_set(self, interaction: discord.Interaction, titre: str, description: str = "", prix: float | None = None, date: str | None = None):
        if not interaction.guild:
            return await interaction.response.send_message("Commande serveur uniquement.", ephemeral=True)

        if not await has_admin_rights(interaction, self.settings.admin_role_name):
            return await interaction.response.send_message("Droits insuffisants.", ephemeral=True)

        svc_cfg = ConfigService(self.db)
        await svc_cfg.ensure_guild(interaction.guild_id, self.settings.admin_role_name, self.settings.timezone, self.settings.default_meal_price_cents)
        cfg = await svc_cfg.get(interaction.guild_id)
        default_price = int(cfg[3]) if cfg else self.settings.default_meal_price_cents

        meal_date = date or today_iso(self.settings.timezone)
        price_cents = euros_to_cents(prix) if prix is not None else default_price

        svc = MealService(self.db)
        meal_id = await svc.upsert_menu(
            interaction.guild_id, meal_date, titre, description, price_cents, interaction.user.id
        )

               # Embed (réutilise ton embed actuel)
        e = menu_embed(meal_date, titre, description, price_cents, "OPEN")

        # Message admin (ephemeral)
        await interaction.response.send_message(f"Menu enregistré (meal_id={meal_id}).", embed=e, ephemeral=True)

        # Détermine le salon d’annonce
        menu_channel_id = None
        if cfg:
            menu_channel_id = cfg[4]  # menu_channel_id

        channel = interaction.channel
        if menu_channel_id:
            ch = interaction.guild.get_channel(int(menu_channel_id))
            if isinstance(ch, discord.TextChannel):
                channel = ch

        # View boutons
        view = MealParticipationView(self.db, interaction.guild_id, meal_id, price_cents, timeout=None)

        # Ping @everyone (nécessite que le bot ait le droit de mentionner everyone)
        allowed = discord.AllowedMentions(everyone=True)
        await channel.send(content="@everyone 🍽️ **Nouveau menu du jour !**", embed=e, view=view, allowed_mentions=allowed)


    @app_commands.command(name="menu_show", description="Affiche le menu du jour")
    async def menu_show(self, interaction: discord.Interaction, date: str | None = None):
        if not interaction.guild:
            return await interaction.response.send_message("Commande serveur uniquement.", ephemeral=True)

        from repas_bot.db.repositories.meals_repo import MealsRepo
        meal_date = date or today_iso(self.settings.timezone)
        row = await MealsRepo(self.db).get_by_date(interaction.guild_id, meal_date)
        if not row:
            return await interaction.response.send_message(f"Aucun menu pour {meal_date}.", ephemeral=True)

        meal_id, meal_date, title, desc, price_cents, status = row
        e = menu_embed(meal_date, title, desc, price_cents, status)
        await interaction.response.send_message(embed=e, ephemeral=True)

async def setup(bot: commands.Bot):
    pass
