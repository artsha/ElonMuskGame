import aiosqlite
import os

DB_NAME = os.getenv("DB_NAME", "elon_game.db")

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                room_id TEXT PRIMARY KEY,
                creator_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'lobby',
                current_problem TEXT,
                elon_musk_user_id INTEGER,
                FOREIGN KEY (creator_id) REFERENCES users(user_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS room_members (
                room_id TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (room_id, user_id),
                FOREIGN KEY (room_id) REFERENCES rooms(room_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS problems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id TEXT NOT NULL,
                problem_text TEXT NOT NULL,
                added_by INTEGER NOT NULL,
                used INTEGER DEFAULT 0,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (room_id) REFERENCES rooms(room_id),
                FOREIGN KEY (added_by) REFERENCES users(user_id)
            )
        """)
        await db.commit()

async def get_db():
    return await aiosqlite.connect(DB_NAME)
