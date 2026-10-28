import sqlite3
import time
import os

# ----------------------------------------------------------------
# PATCH NOTE (July 2026) — Cross-platform path hardening
#
# PROBLEM: The original code used db_path="data/atlas.db" which is
# a path relative to the CURRENT WORKING DIRECTORY. This works fine
# on macOS when run_atlas.sh does "cd $(dirname $0)" first, but on
# Windows — or any launch method that doesn't set CWD to the project
# root — the database lands in the wrong place (or fails outright).
#
# FIX: Compute an absolute, project-relative path using __file__.
# This file lives at: src/core/database.py
# Three dirname() calls walk up: core → src → project_root
# The data folder is always at: <project_root>/data/atlas.db
# ----------------------------------------------------------------

class AtlasDatabase:
    def __init__(self, db_path=None):
        if db_path is None:
            _this_file    = os.path.abspath(__file__)       # …/src/core/database.py
            _core_dir     = os.path.dirname(_this_file)     # …/src/core
            _src_dir      = os.path.dirname(_core_dir)      # …/src
            _project_root = os.path.dirname(_src_dir)       # …/project_atlas
            db_path = os.path.join(_project_root, "data", "atlas.db")

        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._bootstrap()

    def _bootstrap(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS heats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    round_number TEXT,
                    heat_number TEXT,
                    group_letter TEXT,
                    thermalling_dir TEXT,
                    track_open INTEGER,
                    track_close INTEGER,
                    heat_end INTEGER,
                    status TEXT DEFAULT 'READY'
                )
            """)
            # Migration: add new columns to databases created before round/group existed.
            existing_cols = {row[1] for row in conn.execute("PRAGMA table_info(heats)")}
            if 'round_number' not in existing_cols:
                conn.execute("ALTER TABLE heats ADD COLUMN round_number TEXT")
            if 'group_letter' not in existing_cols:
                conn.execute("ALTER TABLE heats ADD COLUMN group_letter TEXT")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            conn.execute(
                "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                ("display_backend", "simulator"))
            conn.execute(
                "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                ("auto_boot_enabled", "0"))

    def save_heat(self, config):
        with sqlite3.connect(self.db_path) as conn:
            if config.id:
                conn.execute("""
                    UPDATE heats SET round_number=?, heat_number=?, group_letter=?, thermalling_dir=?, 
                    track_open=?, track_close=?, heat_end=? 
                    WHERE id=?
                """, (config.round_number, config.heat_number, config.group_letter,
                    config.thermalling_dir, config.track_open, config.track_close,
                    config.heat_end, config.id))
            else:
                conn.execute("""
                    INSERT INTO heats (round_number, heat_number, group_letter, thermalling_dir,
                                       track_open, track_close, heat_end, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'READY')
                """, (config.round_number, config.heat_number, config.group_letter,
                    config.thermalling_dir, config.track_open, config.track_close,
                    config.heat_end))

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

    def get_bool_setting(self, key, default=False):
        """Return a setting coerced to bool.

        Settings are stored as strings; this accepts common truthy values
        ("1", "true", "yes", "on") case-insensitively. Used by the auto-boot
        flag which must default to False (off).
        """
        raw = self.get_setting(key, None)
        if raw is None:
            return bool(default)
        return str(raw).strip().lower() in ("1", "true", "yes", "on")
