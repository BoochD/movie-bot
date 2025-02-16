import aiosqlite
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                username TEXT
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                request TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_movie_counts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                movie_title TEXT NOT NULL,
                count INTEGER DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                UNIQUE(user_id, movie_title)
            )
        """)

        await db.commit()

async def add_user(user_id: int, username: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO users (user_id, username)
            VALUES (?, ?)
        """, (user_id, username))
        await db.commit()

async def save_request(user_id: int, request: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id FROM users WHERE user_id = ?", (user_id,)) as cursor:
            user = await cursor.fetchone()
        if user:
            user_db_id = user[0]
            await db.execute("""
                INSERT INTO requests (user_id, request)
                VALUES (?, ?)
            """, (user_db_id, request))
            await db.commit()

async def get_user_requests(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT r.request, r.timestamp 
            FROM requests r
            JOIN users u ON r.user_id = u.id
            WHERE u.user_id = ?
            ORDER BY r.timestamp DESC
            LIMIT 20
        """, (user_id,)) as cursor:
            history = await cursor.fetchall()
    return history

async def update_movie_count(user_id: int, movie_title: str): 
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT count FROM user_movie_counts WHERE user_id = ? AND movie_title = ?
        """, (user_id, movie_title)) as cursor:
            row = await cursor.fetchone()
        if row: 
            new_count = row[0] + 1
            await db.execute("""
                UPDATE user_movie_counts 
                SET count = ? 
                WHERE user_id = ? AND movie_title = ?
            """, (new_count, user_id, movie_title))
        else:
            await db.execute("""
                INSERT INTO user_movie_counts (user_id, movie_title, count) 
                VALUES (?, ?, 1)
            """, (user_id, movie_title))
        await db.commit()

async def get_user_movies(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT movie_title, count 
            FROM user_movie_counts 
            WHERE user_id = ?
            ORDER BY count DESC
        """, (user_id,)) as cursor:
            movies = await cursor.fetchall()
    return movies
