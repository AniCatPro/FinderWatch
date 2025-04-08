import sqlite3

class FileDatabase:
    def __init__(self, db_name="file_monitor.db"):
        self.connection = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        with self.connection:
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY,
                    path TEXT UNIQUE NOT NULL,
                    hash TEXT NOT NULL
                )
            """)
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    source TEXT UNIQUE NOT NULL,
                    target TEXT NOT NULL
                )
            """)

    def get_file_hash(self, path):
        cur = self.connection.cursor()
        cur.execute("SELECT hash FROM files WHERE path = ?", (path,))
        row = cur.fetchone()
        return row[0] if row else None

    def update_file_hash(self, path, hash):
        with self.connection:
            self.connection.execute("""
                INSERT INTO files (path, hash) VALUES (?, ?)
                ON CONFLICT(path) DO UPDATE SET hash=excluded.hash
            """, (path, hash))

    def add_task(self, source, target):
        with self.connection:
            self.connection.execute("""
                INSERT INTO tasks (source, target) VALUES (?, ?)
                ON CONFLICT(source) DO UPDATE SET target=excluded.target
            """, (source, target))

    def get_tasks(self):
        cur = self.connection.cursor()
        cur.execute("SELECT source, target FROM tasks")
        return cur.fetchall()

    def create_tables(self):
        with self.connection:
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY,
                    path TEXT UNIQUE NOT NULL,
                    hash TEXT NOT NULL
                )
            """)
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    source TEXT UNIQUE NOT NULL,
                    target TEXT NOT NULL
                )
            """)
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL
                )
            """)

    def get_automod_state(self):
        cur = self.connection.cursor()
        cur.execute("SELECT value FROM settings WHERE key = 'automod'")
        row = cur.fetchone()
        return row and row[0] == 'True'

    def set_automod_state(self, state):
        with self.connection:
            self.connection.execute("""
                INSERT INTO settings (key, value) VALUES ('automod', ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
            """, ('True' if state else 'False',))