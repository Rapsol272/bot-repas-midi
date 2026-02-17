import discord

def ok_embed(title: str, description: str) -> discord.Embed:
    return discord.Embed(title=title, description=description)

def error_embed(description: str) -> discord.Embed:
    return discord.Embed(title="Erreur", description=description)
