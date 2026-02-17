# Bot Discord Repas du midi

Bot Discord (discord.py 2.x) pour gérer :
- Menu du jour + participation (oui/non)
- Cagnote (ledger) : dette par repas, remboursements soumis, validation admin
- Invités externes (hors Discord) via code
- Historisation plats + notes + stats simples

## Prérequis
- Python 3.11+ recommandé
- Un bot Discord + token

## Installation
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -e .
copy .env.example .env
# remplir DISCORD_TOKEN dans .env
python scripts/init_db.py
python -m repas_bot
