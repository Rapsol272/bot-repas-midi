import discord
from discord import app_commands
from discord.ext import commands

class HealthCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check bot")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("pong", ephemeral=True)

    @app_commands.command(name="debug_perms", description="Debug permissions (fetch_member, ephemeral)")
    async def debug_perms(self, interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            return await interaction.response.send_message("Pas en serveur.", ephemeral=True)

        # settings (si tu as fait bot.settings = settings)
        admin_role_name = getattr(getattr(self.bot, "settings", None), "admin_role_name", "N/A")

        # fetch member réel
        fetched_roles = []
        fetched_admin = None
        fetched_manage_guild = None
        fetch_error = None

        try:
            m = await guild.fetch_member(interaction.user.id)  # type: ignore[arg-type]
            fetched_roles = [r.name for r in m.roles]  # inclut @everyone
            fetched_admin = m.guild_permissions.administrator
            fetched_manage_guild = m.guild_permissions.manage_guild
        except Exception as e:
            fetch_error = f"{type(e).__name__}: {e}"

        # infos sur l'objet interaction.user
        is_member_obj = isinstance(interaction.user, discord.Member)
        direct_roles = []
        direct_admin = None
        if is_member_obj:
            direct_roles = [r.name for r in interaction.user.roles]
            direct_admin = interaction.user.guild_permissions.administrator

        ap = interaction.app_permissions
        ap_admin = ap.administrator if ap else None

        msg = (
            f"type_user={type(interaction.user).__name__}\n"
            f"guild_id={guild.id}\n"
            f"admin_role_name_env={admin_role_name}\n"
            f"member_obj_admin={direct_admin}\n"
            f"app_permissions_admin={ap_admin}\n"
            f"fetch_member_admin={fetched_admin}\n"
            f"fetch_member_manage_guild={fetched_manage_guild}\n"
            f"direct_roles={', '.join(direct_roles) if direct_roles else '(empty)'}\n"
            f"fetched_roles={', '.join(fetched_roles) if fetched_roles else '(empty)'}\n"
            f"fetch_error={fetch_error or 'None'}"
        )

        await interaction.response.send_message(msg, ephemeral=True)

async def setup(bot: commands.Bot):
    pass
