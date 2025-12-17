import aiosqlite
import logging

DB_NAME = 'tasks.db'

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                status INTEGER DEFAULT 0,
                deadline TEXT,
                category TEXT,
                priority TEXT,
                attachment_id TEXT,
                attachment_type TEXT
            )
        ''')
        # Attempt to migrate by adding columns if they don't exist
        # This is a simple migration strategy for dev
        columns = [
            ("deadline", "TEXT"),
            ("category", "TEXT"),
            ("priority", "TEXT"),
            ("attachment_id", "TEXT"),
            ("attachment_type", "TEXT")
        ]
        
        for col_name, col_type in columns:
            try:
                await db.execute(f'ALTER TABLE tasks ADD COLUMN {col_name} {col_type}')
            except Exception as e:
                # Column likely already exists
                pass
                
        await db.commit()

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                status INTEGER DEFAULT 0,
                deadline TEXT,
                category TEXT,
                priority TEXT,
                attachment_id TEXT,
                attachment_type TEXT
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                language TEXT DEFAULT 'en'
            )
        ''')
        # Attempt to migrate tasks table
        columns = [
            ("deadline", "TEXT"),
            ("category", "TEXT"),
            ("priority", "TEXT"),
            ("attachment_id", "TEXT"),
            ("attachment_type", "TEXT")
        ]
        for col_name, col_type in columns:
            try:
                await db.execute(f'ALTER TABLE tasks ADD COLUMN {col_name} {col_type}')
            except Exception:
                pass
                
        await db.commit()

async def set_user_language(user_id: int, language: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO users (user_id, language) VALUES (?, ?)', (user_id, language))
        await db.commit()

async def get_user_language(user_id: int) -> str:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT language FROM users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 'en'

async def add_task(user_id: int, title: str, category: str = None, priority: str = None, deadline: str = None, attachment_id: str = None, attachment_type: str = None):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            '''INSERT INTO tasks (user_id, title, category, priority, deadline, attachment_id, attachment_type) 
               VALUES (?, ?, ?, ?, ?, ?, ?)''', 
            (user_id, title, category, priority, deadline, attachment_id, attachment_type)
        )
        await db.commit()

async def get_tasks(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM tasks WHERE user_id = ?', (user_id,)) as cursor:
            return await cursor.fetchall()
            
async def search_tasks(user_id: int, query: str):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM tasks WHERE user_id = ? AND title LIKE ?', (user_id, f'%{query}%')) as cursor:
            return await cursor.fetchall()

async def delete_task(task_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        await db.commit()

async def update_task_status(task_id: int, status: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE tasks SET status = ? WHERE id = ?', (status, task_id))
        await db.commit()
