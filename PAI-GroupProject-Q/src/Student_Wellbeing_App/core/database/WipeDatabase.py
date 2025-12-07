from pathlib import Path
import sqlite3

DB_FILE = Path("student_wellbeing_db.sqlite3")
SCHEMA_NAME = "student_wellbeing_db"


def wipe_database():
    if not DB_FILE.exists():
        print("⚠ Database file not found — nothing to wipe.")
        return


    conn = sqlite3.connect(DB_FILE)
    conn.close()

    # Delete the database file
    DB_FILE.unlink()

    print("✅ SQLite database file deleted.")


if __name__ == "__main__":
    wipe_database()
