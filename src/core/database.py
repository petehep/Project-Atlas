import sqlite3
import os
import time
from core.models import HeatConfig

class AtlasDatabase:
    """The Immutable Source of Truth for Project Atlas."""
    def __init__(self, db_path="data/atlas.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._initialize_db()

    def _initialize_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # The schema remains simple. Status is strictly for Operator oversight.
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS heats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    heat_number TEXT NOT NULL,
                    thermalling_dir TEXT NOT NULL,
                    track_open REAL NOT NULL,
                    track_close REAL NOT NULL,
                    heat_end REAL NOT NULL,
                    status TEXT DEFAULT 'SCHEDULED'
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            conn.commit()

    def get_active_scheduled_heat(self, now):
        """
        The Single Source of Truth.
        Finds the first heat marked 'SCHEDULED' that hasn't ended yet.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            # Query Logic: 
            # 1. Must be SCHEDULED
            # 2. Must end in the future (relative to 'now')
            # 3. Get the earliest one first
            cursor.execute("""
                SELECT * FROM heats 
                WHERE status = 'SCHEDULED' AND heat_end > ? 
                ORDER BY track_open ASC LIMIT 1
            """, (now,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def save_heat(self, config: HeatConfig):
        """Saves or Updates. Status always reverts to SCHEDULED on edit for safety."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if config.id:
                cursor.execute("""
                    UPDATE heats 
                    SET heat_number=?, thermalling_dir=?, track_open=?, track_close=?, heat_end=?, status='SCHEDULED'
                    WHERE id=?
                """, (config.heat_number, config.thermalling_dir, 
                      config.track_open, config.track_close, config.heat_end, config.id))
            else:
                cursor.execute("""
                    INSERT INTO heats (heat_number, thermalling_dir, track_open, track_close, heat_end, status)
                    VALUES (?, ?, ?, ?, ?, 'SCHEDULED')
                """, (config.heat_number, config.thermalling_dir, 
                      config.track_open, config.track_close, config.heat_end))
            conn.commit()

    def set_heat_status(self, heat_id, status):
        """Operator manual override (COMPLETED, CANCELLED)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE heats SET status = ? WHERE id = ?", (status, heat_id))
            conn.commit()

    def delete_heat(self, heat_id):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM heats WHERE id = ?", (heat_id,))
            conn.commit()

    def get_todays_schedule(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM heats ORDER BY track_open ASC")
            return [dict(row) for row in cursor.fetchall()]

    def get_setting(self, key, default=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else default

    def save_setting(self, key, value):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))
            conn.commit()
