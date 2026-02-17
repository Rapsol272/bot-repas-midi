import discord

from repas_bot.services.participation_service import ParticipationService
from repas_bot.services.ledger_service import LedgerService
from repas_bot.db.repositories.participants_repo import ParticipantsRepo
from repas_bot.utils.money import cents_to_euros_str


class MealParticipationView(discord.ui.View):
    def __init__(self, db, guild_id: int, meal_id: int, price_cents: int, timeout: float | None = None):
        super().__init__(timeout=timeout)
        self.db = db
        self.guild_id = guild_id
        self.meal_id = meal_id
        self.price_cents = int(price_cents)

    async def _already_yes(self, user_id: int) -> bool:
        repo = ParticipantsRepo(self.db)
        status = await repo.get_status(self.meal_id, user_id)
        return status == "YES"

    @discord.ui.button(label="Je participe", style=discord.ButtonStyle.success, emoji="✅")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.guild:
            return await interaction.response.send_message("Commande serveur uniquement.", ephemeral=True)

        # Evite double débit
        was_yes = await self._already_yes(interaction.user.id)

        part = ParticipationService(self.db)
        await part.join(self.meal_id, interaction.user.id)

        if not was_yes:
            ledger = LedgerService(self.db)
            await ledger.charge_meal(self.guild_id, interaction.user.id, self.meal_id, self.price_cents, interaction.user.id)

        await interaction.response.send_message(
            f"Participation enregistrée. (+{cents_to_euros_str(self.price_cents)} de dette)" if not was_yes
            else "Participation déjà enregistrée (pas de nouveau débit).",
            ephemeral=True
        )

    @discord.ui.button(label="Je ne participe pas", style=discord.ButtonStyle.secondary, emoji="❌")
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.guild:
            return await interaction.response.send_message("Commande serveur uniquement.", ephemeral=True)

        part = ParticipationService(self.db)
        await part.leave(self.meal_id, interaction.user.id)

        await interaction.response.send_message("Ok, noté : tu ne participes pas.", ephemeral=True)
