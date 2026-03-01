import discord
from discord import app_commands
from discord.ext import commands

from repas_bot.permissions import has_admin_rights
from repas_bot.services.config_service import ConfigService


class PollCog(commands.Cog):
    def __init__(self, bot: commands.Bot, db, settings):
        self.bot = bot
        self.db = db
        self.settings = settings

    @staticmethod
    def _parse_options(options: str) -> list[tuple[str, str]]:
        parsed: list[tuple[str, str]] = []
        for raw_item in options.split(";"):
            item = raw_item.strip()
            if not item:
                continue
            if "=" not in item:
                raise ValueError("format")
            emoji, label = item.split("=", 1)
            emoji = emoji.strip()
            label = label.strip()
            if not emoji or not label:
                raise ValueError("format")
            parsed.append((emoji, label))
        return parsed

    @app_commands.command(name="poll_create", description="Crée un sondage Discord dans le salon sondages")
    @app_commands.describe(
        question="Question du sondage",
        options="Format: emoji=texte; emoji=texte (ex: 🍕=Pizza; 🍔=Burger)",
    )
    async def poll_create(self, interaction: discord.Interaction, question: str, options: str):
        if not interaction.guild:
            return await interaction.response.send_message("Commande serveur uniquement.", ephemeral=True)

        if not await has_admin_rights(interaction, self.settings.admin_role_name):
            return await interaction.response.send_message("Droits insuffisants.", ephemeral=True)

        try:
            parsed_options = self._parse_options(options)
        except ValueError:
            return await interaction.response.send_message(
                "Format invalide. Utilise `emoji=texte; emoji=texte` (ex: `🍕=Pizza; 🍔=Burger`).",
                ephemeral=True,
            )

        if len(parsed_options) < 2:
            return await interaction.response.send_message("Il faut au moins 2 options.", ephemeral=True)

        svc = ConfigService(self.db)
        await svc.ensure_guild(
            interaction.guild_id,
            self.settings.admin_role_name,
            self.settings.timezone,
            self.settings.default_meal_price_cents,
        )
        cfg = await svc.get(interaction.guild_id)
        poll_channel_id = cfg[5] if cfg else None  # poll_channel_id
        if not poll_channel_id:
            return await interaction.response.send_message(
                "Aucun salon sondages configuré. Utilise `/config_poll_channel`.",
                ephemeral=True,
            )

        configured_channel = interaction.guild.get_channel(int(poll_channel_id))
        if not isinstance(configured_channel, discord.TextChannel):
            return await interaction.response.send_message(
                "Le salon sondages configuré est introuvable.",
                ephemeral=True,
            )
        channel = configured_channel

        description_lines = [f"{emoji} {label}" for emoji, label in parsed_options]
        embed = discord.Embed(
            title="🗳️ Sondage repas",
            description=f"**{question}**\n\n" + "\n".join(description_lines),
        )
        embed.set_footer(text=f"Créé par {interaction.user.display_name}")

        poll_message = await channel.send(embed=embed)
        for emoji, _ in parsed_options:
            await poll_message.add_reaction(emoji)

        await interaction.response.send_message(
            f"Sondage publié dans {channel.mention}.",
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    pass
