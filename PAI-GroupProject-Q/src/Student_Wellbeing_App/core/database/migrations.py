import os
import sys
from pathlib import Path
from datetime import datetime

# Ensure the project root is in sys.path
current_file = Path(__file__).resolve()
project_root = current_file.parents[4]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.Student_Wellbeing_App.core.database.connection import (
    get_db_connection,
    DB_NAME,
)

def run_migrations():
    # Connect using the same helper + same DB path as the rest of the app
    conn = get_db_connection()
    cursor = conn.cursor()

    print("DB file path:", DB_NAME)

    # 1. Student
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student (
        student_id TEXT PRIMARY KEY,
        first_name TEXT,
        lastname   TEXT,
        email      TEXT UNIQUE,
        password   TEXT,
        year       INTEGER
    )
    """)

    # 2. Attendance
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id    TEXT,
        session_date  DATE,
        session_id    TEXT,
        status        TEXT,
        FOREIGN KEY (student_id) REFERENCES student(student_id)
    )
    """)

    # 3. Assessment
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assessment (
        assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        module_code   TEXT,
        title         TEXT,
        due_date      DATE,
        weight        REAL
    )
    """)

    # 4. Submission
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS submission (
        submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id    TEXT,
        assessment_id INTEGER,
        submitted_at  DATETIME,
        status        TEXT,
        mark          REAL,
        FOREIGN KEY (student_id)    REFERENCES student(student_id),
        FOREIGN KEY (assessment_id) REFERENCES assessment(assessment_id)
    )
    """)

    # 5. Wellbeing
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wellbeing_record (
        record_id    INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id   TEXT,
        week_start   DATE,
        stress_level INTEGER,
        sleep_hours  REAL,
        source_type  TEXT,
        FOREIGN KEY (student_id) REFERENCES student(student_id)
    )
    """)

    # 6. Alert
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alert (
        alert_id    INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id  TEXT,
        alert_type  TEXT,
        reason      TEXT,
        created_at  DATETIME,
        resolved    INTEGER,
        FOREIGN KEY (student_id) REFERENCES student(student_id)
    )
    """)

    # 7. Retention Rule
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS retention_rule (
        rule_id          INTEGER PRIMARY KEY AUTOINCREMENT,
        data_type        TEXT,
        retention_months INTEGER,
        is_active        INTEGER
    )
    """)

    # 8. Audit Log
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_log (
        log_id      INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     TEXT,
        action      TEXT, 
        details     TEXT,
        timestamp   DATETIME
    )
    """)

    # 9. User
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            user_id       TEXT PRIMARY KEY,
            first_name    TEXT NOT NULL,
            lastname      TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role          TEXT NOT NULL
        );
    """)
    
    # 10. Module
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS module (
        module_code TEXT PRIMARY KEY,
        title       TEXT NOT NULL
    )
    """)

    # 11. Teaching Assignment
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teaching_assignment (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     TEXT,
        module_code TEXT,
        FOREIGN KEY (user_id) REFERENCES user(user_id),
        FOREIGN KEY (module_code) REFERENCES module(module_code)
    )
    """)

    # 12. Enrollment
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS enrollment (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id  TEXT,
        module_code TEXT,
        FOREIGN KEY (student_id) REFERENCES student(student_id),
        FOREIGN KEY (module_code) REFERENCES module(module_code)
    )
    """)

    conn.commit()
    print(f"[{datetime.utcnow()}] ✅Migrations completed successfully on {DB_NAME}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    run_migrations()