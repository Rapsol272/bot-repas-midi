import os
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv

from repas_bot.config import load_settings
from repas_bot.logging_setup import setup_logging
from repas_bot.db.connection import create_connection
from repas_bot.db.migrations import apply_migrations

from repas_bot.cogs.config_cog import ConfigCog
from repas_bot.cogs.menu_cog import MenuCog
from repas_bot.cogs.repas_cog import RepasCog
from repas_bot.cogs.cagnote_cog import CagnoteCog
from repas_bot.cogs.invites_cog import InvitesCog
from repas_bot.cogs.plats_cog import PlatsCog
from repas_bot.cogs.admin_cog import AdminCog
from repas_bot.cogs.health_cog import HealthCog


log = logging.getLogger("repas_bot")

async def run() -> None:
    load_dotenv()
    settings = load_settings()

    setup_logging(settings.log_level)

    intents = discord.Intents.default()
    intents.guilds = True

    bot = commands.Bot(command_prefix="!", intents=intents)
    bot.settings = settings  # pour debug

    @bot.event
    async def on_ready():
        log.info("Logged in as %s", bot.user)

        # Sync commands (global or per guild)
        if settings.guild_id and settings.guild_id != 0:
            guild = discord.Object(id=settings.guild_id)
            bot.tree.copy_global_to(guild=guild)
            await bot.tree.sync(guild=guild)
            log.info("Commands synced to guild=%s", settings.guild_id)
        else:
            await bot.tree.sync()
            log.info("Commands synced globally")

    async with create_connection(settings.db_path) as db:
        # migrations au démarrage
        await apply_migrations(db, migrations_dir="./migrations")

        # register cogs (inject db/settings)
        await bot.add_cog(HealthCog(bot))
        await bot.add_cog(ConfigCog(bot, db, settings))
        await bot.add_cog(MenuCog(bot, db, settings))
        await bot.add_cog(RepasCog(bot, db, settings))
        await bot.add_cog(CagnoteCog(bot, db, settings))
        await bot.add_cog(InvitesCog(bot, db, settings))
        await bot.add_cog(PlatsCog(bot, db, settings))
        await bot.add_cog(AdminCog(bot, db, settings))

        await bot.start(settings.discord_token)
