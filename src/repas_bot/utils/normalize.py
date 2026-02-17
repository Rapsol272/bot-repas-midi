import re
import unicodedata

def normalize_name(s: str) -> str:
    s = s.strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s
