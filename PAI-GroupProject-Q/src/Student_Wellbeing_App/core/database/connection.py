import sqlite3
from pathlib import Path

# DB lives next to this file: core/database/student_wellbeing_db.sqlite3
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "student_wellbeing_db.sqlite3"

# Export a name other modules can print/log if they want
DB_NAME = DB_PATH


def get_db_connection() -> sqlite3.Connection:
    """
    Return a NEW SQLite connection each time.
    Callers are responsible for closing it.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # optional: dict-like row access
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_db_pool():
    """
    Backwards-compatible shim for old MySQL-style pool code.
    For SQLite we just return a new connection.
    Prefer to call get_db_connection() directly.
    """
    return get_db_connection()
