import discord

async def has_admin_rights(interaction: discord.Interaction, admin_role_name: str) -> bool:
    if not interaction.guild:
        return False

    # Toujours fetch : interaction.user peut être un Member partiel sans roles
    try:
        member = await interaction.guild.fetch_member(interaction.user.id)  # type: ignore[arg-type]
    except Exception:
        member = None

    if member is not None:
        # Administrator
        if member.guild_permissions.administrator:
            return True

        # Option pratique : accepter aussi "Gérer le serveur"
        # if member.guild_permissions.manage_guild:
        #     return True

        return any(r.name == admin_role_name for r in member.roles)

    # fallback ultime
    perms = interaction.app_permissions
    return bool(perms and perms.administrator)
