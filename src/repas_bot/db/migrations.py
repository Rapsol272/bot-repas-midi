import os
from pathlib import Path
import aiosqlite

async def _has_migration(db: aiosqlite.Connection, version: str) -> bool:
    row = await (await db.execute(
        "SELECT 1 FROM schema_migrations WHERE version = ?",
        (version,),
    )).fetchone()
    return row is not None

async def apply_migrations(db: aiosqlite.Connection, migrations_dir: str) -> None:
    # ensure schema_migrations exists (idempotent)
    await db.executescript("""
    CREATE TABLE IF NOT EXISTS schema_migrations (
      version TEXT PRIMARY KEY,
      applied_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """)
    await db.commit()

    path = Path(migrations_dir)
    files = sorted([p for p in path.glob("*.sql")])

    for p in files:
        version = p.name
        if await _has_migration(db, version):
            continue

        sql = p.read_text(encoding="utf-8")
        await db.executescript(sql)
        await db.execute(
            "INSERT INTO schema_migrations(version) VALUES(?)",
            (version,),
        )
        await db.commit()
