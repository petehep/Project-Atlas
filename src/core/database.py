import sqlite3
import os
from core.models import HeatConfig

class AtlasDatabase:
    """The persistence layer for all Atlas race data."""
    def __init__(self, db_path="data/atlas.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._initialize_db()

    def _initialize_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS heats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    heat_number TEXT NOT NULL,
                    thermalling_dir TEXT NOT NULL,
                    track_open REAL NOT NULL,
                    track_close REAL NOT NULL,
                    heat_end REAL NOT NULL,
                    status TEXT DEFAULT 'READY'
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            conn.commit()

    def save_heat(self, config: HeatConfig):
        """Saves a new heat or updates an existing one if ID is present."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if config.id:
                cursor.execute("""
                    UPDATE heats 
                    SET heat_number=?, thermalling_dir=?, track_open=?, track_close=?, heat_end=?
                    WHERE id=?
                """, (config.heat_number, config.thermalling_dir, 
                      config.track_open, config.track_close, config.heat_end, config.id))
            else:
                cursor.execute("""
                    INSERT INTO heats (heat_number, thermalling_dir, track_open, track_close, heat_end, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (config.heat_number, config.thermalling_dir, 
                      config.track_open, config.track_close, config.heat_end, config.status))
            conn.commit()

    def delete_heat(self, heat_id):
        """Hard delete from the daily schedule."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM heats WHERE id = ?", (heat_id,))
            conn.commit()

    def get_todays_schedule(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM heats WHERE status != 'ARCHIVED' ORDER BY track_open ASC")
            return [dict(row) for row in cursor.fetchall()]

    def update_heat_status(self, heat_id, new_status):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE heats SET status = ? WHERE id = ?", (new_status, heat_id))
            conn.commit()

    def get_setting(self, key, default=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else default

    def save_setting(self, key, value):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO settings (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
            """, (key, value))
            conn.commit()
