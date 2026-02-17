from contextlib import asynccontextmanager
import aiosqlite

@asynccontextmanager
async def create_connection(db_path: str):
    db = await aiosqlite.connect(db_path)
    try:
        await db.execute("PRAGMA foreign_keys = ON;")
        await db.execute("PRAGMA journal_mode = WAL;")
        await db.execute("PRAGMA synchronous = NORMAL;")
        yield db
    finally:
        await db.close()
