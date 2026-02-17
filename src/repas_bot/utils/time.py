from datetime import datetime
from zoneinfo import ZoneInfo

def today_iso(tz_name: str) -> str:
    tz = ZoneInfo(tz_name)
    return datetime.now(tz).date().isoformat()
