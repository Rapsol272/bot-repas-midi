import discord
from discord import app_commands
from discord.ext import commands

from repas_bot.services.dish_service import DishService
from repas_bot.services.meal_service import MealService
from repas_bot.services.rating_service import RatingService
from repas_bot.db.repositories.meals_repo import MealsRepo
from repas_bot.utils.time import today_iso

class PlatsCog(commands.Cog):
    def __init__(self, bot: commands.Bot, db, settings):
        self.bot = bot
        self.db = db
        self.settings = settings

    @app_commands.command(name="plat_add", description="Ajoute un plat au catalogue")
    async def plat_add(self, interaction: discord.Interaction, nom: str):
        if not interaction.guild:
            return await interaction.response.send_message("Commande serveur uniquement.", ephemeral=True)
        dish_id = await DishService(self.db).add(interaction.guild_id, nom)
        await interaction.response.send_message(f"Plat enregistré (dish_id={dish_id}).", ephemeral=True)

    @app_commands.command(name="plat_list", description="Liste les plats du catalogue")
    async def plat_list(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message("Commande serveur uniquement.", ephemeral=True)
        rows = await DishService(self.db).list(interaction.guild_id)
        if not rows:
            return await interaction.response.send_message("Aucun plat.", ephemeral=True)
        txt = "\n".join([f"- ({dish_id}) {name}" for dish_id, name in rows[:50]])
        await interaction.response.send_message(txt, ephemeral=True)

    @app_commands.command(name="menu_add_plat", description="Associe un plat au menu du jour (par nom)")
    async def menu_add_plat(self, interaction: discord.Interaction, nom_plat: str, date: str | None = None):
        if not interaction.guild:
            return await interaction.response.send_message("Commande serveur uniquement.", ephemeral=True)

        meal_date = date or today_iso(self.settings.timezone)
        row = await MealsRepo(self.db).get_by_date(interaction.guild_id, meal_date)
        if not row:
            return await interaction.response.send_message(f"Aucun menu pour {meal_date}.", ephemeral=True)

        meal_id = int(row[0])
        dish_id = await MealService(self.db).add_dish_to_meal(interaction.guild_id, meal_id, nom_plat)
        await interaction.response.send_message(f"Plat lié au menu (dish_id={dish_id}).", ephemeral=True)

    @app_commands.command(name="plat_note", description="Note un plat (1..5) pour un menu (date optionnelle)")
    async def plat_note(self, interaction: discord.Interaction, dish_id: int, note: int, date: str | None = None, commentaire: str = ""):
        if not interaction.guild:
            return await interaction.response.send_message("Commande serveur uniquement.", ephemeral=True)
        if note < 1 or note > 5:
            return await interaction.response.send_message("Note invalide (1..5).", ephemeral=True)

        meal_date = date or today_iso(self.settings.timezone)
        row = await MealsRepo(self.db).get_by_date(interaction.guild_id, meal_date)
        if not row:
            return await interaction.response.send_message(f"Aucun menu pour {meal_date}.", ephemeral=True)
        meal_id = int(row[0])

        await RatingService(self.db).rate(interaction.guild_id, dish_id, meal_id, interaction.user.id, note, commentaire)
        await interaction.response.send_message("Note enregistrée.", ephemeral=True)

    @app_commands.command(name="plat_top", description="Top plats (moyenne) - nécessite >=2 notes/plat")
    async def plat_top(self, interaction: discord.Interaction, limit: int = 10):
        if not interaction.guild:
            return await interaction.response.send_message("Commande serveur uniquement.", ephemeral=True)
        rows = await RatingService(self.db).top(interaction.guild_id, limit=max(1, min(limit, 20)))
        if not rows:
            return await interaction.response.send_message("Pas assez de notes.", ephemeral=True)
        txt = "\n".join([f"- **{name}** : {avg_rating:.2f}/5 ({n} notes)" for name, n, avg_rating in rows])
        await interaction.response.send_message(txt, ephemeral=True)

async def setup(bot: commands.Bot):
    pass
