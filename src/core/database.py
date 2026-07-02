import sqlite3
import time
import os

class AtlasDatabase:
    def __init__(self, db_path="data/atlas.db"):
        os.makedirs("data", exist_ok=True)
        self.db_path = db_path
        self._bootstrap()

    def _bootstrap(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS heats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    heat_number TEXT,
                    thermalling_dir TEXT,
                    track_open INTEGER,
                    track_close INTEGER,
                    heat_end INTEGER,
                    status TEXT DEFAULT 'READY'
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)

    def save_heat(self, config):
        with sqlite3.connect(self.db_path) as conn:
            if config.id:
                conn.execute("""
                    UPDATE heats SET heat_number=?, thermalling_dir=?, 
                    track_open=?, track_close=?, heat_end=? 
                    WHERE id=?
                """, (config.heat_number, config.thermalling_dir, 
                    config.track_open, config.track_close, config.heat_end, config.id))
            else:
                conn.execute("""
                    INSERT INTO heats (heat_number, thermalling_dir, track_open, track_close, heat_end, status)
                    VALUES (?, ?, ?, ?, ?, 'READY')
                """, (config.heat_number, config.thermalling_dir, 
                    config.track_open, config.track_close, config.heat_end))

    def get_todays_schedule(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute("SELECT * FROM heats ORDER BY track_open ASC")]

    def get_active_heat(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            res = conn.execute("SELECT * FROM heats WHERE status = 'ACTIVE' LIMIT 1").fetchone()
            return dict(res) if res else None

    def get_next_pending_heat(self):
        now = int(time.time())
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            res = conn.execute("""
                SELECT * FROM heats 
                WHERE status = 'READY' AND track_close > ? 
                ORDER BY track_open ASC LIMIT 1
            """, (now,)).fetchone()
            return dict(res) if res else None

    def set_heat_status(self, heat_id, status):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE heats SET status = ? WHERE id = ?", (status, heat_id))

    def cancel_active_heat(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE heats SET status = 'CANCELLED' WHERE status = 'ACTIVE'")

    def delete_heat(self, heat_id):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM heats WHERE id = ?", (heat_id,))

    def save_setting(self, key, value):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))

    def get_setting(self, key, default=None):
        with sqlite3.connect(self.db_path) as conn:
            res = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
            return res[0] if res else default
