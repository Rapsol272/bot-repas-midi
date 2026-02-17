from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Settings:
    discord_token: str
    db_path: str
    log_level: str
    default_meal_price_cents: int
    timezone: str
    admin_role_name: str
    guild_id: int  # 0 = global sync

def load_settings() -> Settings:
    token = os.getenv("DISCORD_TOKEN", "").strip()
    if not token:
        raise RuntimeError("DISCORD_TOKEN is missing in environment (.env).")

    return Settings(
        discord_token=token,
        db_path=os.getenv("DB_PATH", "./data/bot.db"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        default_meal_price_cents=int(os.getenv("DEFAULT_MEAL_PRICE_CENTS", "500")),
        timezone=os.getenv("TIMEZONE", "Europe/Paris"),
        admin_role_name=os.getenv("ADMIN_ROLE_NAME", "Chef"),
        guild_id=int(os.getenv("GUILD_ID", "0")),
    )
