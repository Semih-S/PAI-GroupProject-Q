from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
DB_FILENAME = "student_wellbeing_db.sqlite3"
DB_FILE = BASE_DIR / DB_FILENAME

# Removes the database file from disk.
def wipe_database():
    #checking for the existence of the file to prevent error
    if not DB_FILE.exists():
        print("⚠ Database file not found — nothing to wipe.")
        return

    # Opening a connection to ensure the file isn't locked by another process.
    conn = sqlite3.connect(DB_FILE)
    conn.close()

    # Delete the database file
    DB_FILE.unlink()

    print("✅ SQLite database file deleted.")


if __name__ == "__main__":
    wipe_database()


