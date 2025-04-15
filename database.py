import sqlite3
import os


class FileDatabase:
    def __init__(self, db_name="file_monitor.db"):
        self.connection = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        with self.connection:
            try:
                self.connection.execute("ALTER TABLE tasks ADD COLUMN exclusions TEXT")
            except sqlite3.OperationalError:
                pass  # Колонка уже существует

            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY,
                    path TEXT UNIQUE NOT NULL,
                    hash TEXT NOT NULL,
                    versions TEXT
                )
            """)
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    source TEXT UNIQUE NOT NULL,
                    target TEXT NOT NULL,
                    exclusions TEXT
                )
            """)
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL
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
        cur.execute("SELECT source, target, exclusions FROM tasks")
        return cur.fetchall()

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

    def get_setting(self, key):
        cur = self.connection.cursor()
        cur.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cur.fetchone()
        return row[0] if row else None

    def set_setting(self, key, value):
        with self.connection:
            self.connection.execute("""
                INSERT INTO settings (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
            """, (key, value))

    def get_file_versions(self, path):
        cur = self.connection.cursor()
        cur.execute("SELECT versions FROM files WHERE path = ?", (path,))
        row = cur.fetchone()
        return row[0] if row else None

    def update_file_versions(self, path, versions):
        with self.connection:
            self.connection.execute("""
                INSERT INTO files (path, hash, versions) VALUES (?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET versions=excluded.versions
            """, (path, self.get_file_hash(path), versions))

    def get_exclusions(self, source):
        cur = self.connection.cursor()
        cur.execute("SELECT exclusions FROM tasks WHERE source = ?", (source,))
        row = cur.fetchone()
        return row[0].split(',') if row and row[0] else []

    def set_exclusions(self, source, exclusions):
        if isinstance(exclusions, list):
            exclusions_str = ','.join(exclusions)
            with self.connection:
                self.connection.execute("""
                    UPDATE tasks SET exclusions = ? WHERE source = ?
                """, (exclusions_str, source))
        else:
            raise ValueError("Exclusions must be a list of strings.")

    def set_exclusions(self, source, exclusions):
        exclusions_str = ','.join(exclusions)
        with self.connection:
            self.connection.execute("""
                UPDATE tasks SET exclusions = ? WHERE source = ?
            """, (exclusions_str, source))

    def remove_task(self, source):
        with self.connection:
            self.connection.execute("DELETE FROM tasks WHERE source = ?", (source,))