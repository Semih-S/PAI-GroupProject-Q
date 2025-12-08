import sqlite3
import os
from pathlib import Path

# --- Absolute Path ---
CURRENT_DIR = Path(__file__).resolve().parent
DB_FILENAME = "student_wellbeing_db.sqlite3"
DB_PATH = CURRENT_DIR / DB_FILENAME

# Export a name other modules can print/log if they want
DB_NAME = DB_PATH

# Optional: Log the DB path for debugging
print(f"✈️ [DB CONNECTION] Connecting to: 👉 {DB_PATH}")

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn