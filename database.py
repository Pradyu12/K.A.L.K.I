import aiosqlite
import asyncio
from pathlib import Path

DB_PATH = Path("kalki_core.db")

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        # Command Logs
        await db.execute("""
            CREATE TABLE IF NOT EXISTS command_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transcript TEXT,
                command TEXT,
                response TEXT,
                execution_duration REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Mission Log (Tasks)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'pending',
                priority TEXT DEFAULT 'medium',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # System Settings
        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        await db.commit()

async def log_command(transcript, command, response, duration):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO command_logs (transcript, command, response, execution_duration)
            VALUES (?, ?, ?, ?)
        """, (transcript, command, response, duration))
        await db.commit()

# Task Operations
async def add_task(title, description=None, priority='medium'):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO tasks (title, description, priority)
            VALUES (?, ?, ?)
        """, (title, description, priority))
        await db.commit()

async def get_tasks(status=None):
    async with aiosqlite.connect(DB_PATH) as db:
        if status:
            async with db.execute("SELECT id, title, description, status, priority, created_at FROM tasks WHERE status = ? ORDER BY created_at DESC", (status,)) as cursor:
                return await cursor.fetchall()
        else:
            async with db.execute("SELECT id, title, description, status, priority, created_at FROM tasks ORDER BY created_at DESC") as cursor:
                return await cursor.fetchall()

async def update_task_status(task_id, status):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
        await db.commit()

async def delete_task(task_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        await db.commit()

# Settings Operations
async def set_setting(key, value):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        await db.commit()

async def get_setting(key):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT value FROM settings WHERE key = ?", (key,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def get_recent_logs(limit=10):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT transcript, response, timestamp FROM command_logs ORDER BY timestamp DESC LIMIT ?", (limit,)) as cursor:
            return await cursor.fetchall()
