import discord
from repas_bot.utils.money import cents_to_euros_str

def menu_embed(meal_date: str, title: str, description: str, price_cents: int, status: str) -> discord.Embed:
    e = discord.Embed(title=f"Menu du {meal_date} ({status})", description=f"**{title}**\n\n{description}")
    e.add_field(name="Prix", value=cents_to_euros_str(price_cents), inline=True)
    return e

def simple_embed(title: str, desc: str) -> discord.Embed:
    return discord.Embed(title=title, description=desc)
