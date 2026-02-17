import discord
from discord import app_commands
from discord.ext import commands
from repas_bot.services.config_service import ConfigService

from repas_bot.services.ledger_service import LedgerService
from repas_bot.utils.money import euros_to_cents

class CagnoteCog(commands.Cog):
    def __init__(self, bot: commands.Bot, db, settings):
        self.bot = bot
        self.db = db
        self.settings = settings

    @app_commands.command(name="cagnote_solde", description="Affiche combien tu dois (solde)")
    async def cagnote_solde(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message("Commande serveur uniquement.", ephemeral=True)

        svc = LedgerService(self.db)
        bal = await svc.balance_str(interaction.guild_id, interaction.user.id)
        await interaction.response.send_message(f"Solde (dette) : **{bal}**", ephemeral=True)

    @app_commands.command(name="cagnote_rembourser", description="Déclare un remboursement (à valider par admin)")
    @app_commands.describe(montant="Montant en euros (ex: 10.0)", note="Optionnel")
    async def cagnote_rembourser(self, interaction: discord.Interaction, montant: float, note: str = ""):
        if not interaction.guild:
            return await interaction.response.send_message("Commande serveur uniquement.", ephemeral=True)

        svc = LedgerService(self.db)
        amount_cents = euros_to_cents(montant)

        entry_id = await svc.submit_repayment(
            interaction.guild_id, interaction.user.id, amount_cents, note, interaction.user.id
        )

        # Réponse utilisateur
        await interaction.response.send_message(
            f"Remboursement soumis (entry_id={entry_id}) en attente de validation.",
            ephemeral=True
        )

        # --- NOTIF ROLE CHEF ---
        # récup config pour savoir où notifier (menu_channel si défini)
        cfg = await ConfigService(self.db).get(interaction.guild_id)
        menu_channel_id = cfg[4] if cfg else None  # menu_channel_id

        channel = interaction.channel
        if menu_channel_id:
            ch = interaction.guild.get_channel(int(menu_channel_id))
            if isinstance(ch, discord.TextChannel):
                channel = ch

        # role chef par nom (ADMIN_ROLE_NAME)
        chef_role = discord.utils.get(interaction.guild.roles, name=self.settings.admin_role_name)
        mention = chef_role.mention if chef_role else f"@{self.settings.admin_role_name}"

        # build message
        user_mention = interaction.user.mention
        euros_str = f"{montant:.2f} €"
        note_txt = note.strip() if note and note.strip() else "(aucune note)"

        content = (
            f"{mention} 💰 **Demande de remboursement à valider**\n"
            f"- Demandeur : {user_mention} (`{interaction.user.id}`)\n"
            f"- Montant : **{euros_str}**\n"
            f"- Note : {note_txt}\n"
            f"- entry_id : `{entry_id}`\n"
            f"➡️ Valider avec : `/admin_approve entry_id:{entry_id}`"
        )

        # autoriser la mention du role
        allowed = discord.AllowedMentions(roles=True, users=True)
        await channel.send(content=content, allowed_mentions=allowed)


async def setup(bot: commands.Bot):
    pass
