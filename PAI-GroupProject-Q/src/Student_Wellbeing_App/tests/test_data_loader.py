# tests/test_data_loader.py

import sqlite3

import pytest

from src.Student_Wellbeing_App.core.streamlit_UI import data_loader


# ---------- Helper: create minimal schema used by data_loader ----------

def create_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()

    # Wellbeing records
    cur.execute("""
        CREATE TABLE wellbeing_record (
            record_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id   TEXT NOT NULL,
            week_start   TEXT NOT NULL,
            stress_level REAL NOT NULL,
            sleep_hours  REAL NOT NULL
        )
    """)

    # Students
    cur.execute("""
        CREATE TABLE student (
            student_id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            lastname   TEXT NOT NULL,
            email      TEXT NOT NULL,
            year       INTEGER NOT NULL
        )
    """)

    # Assessments & submissions (grades)
    cur.execute("""
        CREATE TABLE assessment (
            assessment_id INTEGER PRIMARY KEY,
            module_code   TEXT NOT NULL,
            title         TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE submission (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id    TEXT NOT NULL,
            assessment_id INTEGER NOT NULL,
            mark          REAL,
            FOREIGN KEY (assessment_id) REFERENCES assessment(assessment_id)
        )
    """)

    # Attendance
    cur.execute("""
        CREATE TABLE attendance (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id  TEXT NOT NULL,
            session_id  TEXT NOT NULL,
            status      TEXT NOT NULL,
            session_date TEXT
        )
    """)

    # Enrollment (used in load_academic_data when module_code is provided)
    cur.execute("""
        CREATE TABLE enrollment (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            module_code TEXT NOT NULL
        )
    """)

    conn.commit()


# ---------- Pytest fixture: in-memory DB + monkeypatched get_db ----------

@pytest.fixture
def test_db(monkeypatch):
    """
    Provides an in-memory sqlite database and patches data_loader.get_db()
    so all functions under test use this temp DB instead of the real one.
    """
    conn = sqlite3.connect(":memory:")
    create_schema(conn)

    # Each call to get_db() should return a connection that will be closed
    # by the code under test after use. For simplicity we return the same
    # connection; closing it at the end of the test session is fine.
    def _get_db():
        return conn

    monkeypatch.setattr(data_loader, "get_db", _get_db)
    yield conn
    conn.close()


# ---------- Tests: load_aggregate_wellbeing_trend ----------

def test_load_aggregate_wellbeing_trend_aggregates_by_week(test_db):
    cur = test_db.cursor()
    # two records in same week, one in another
    cur.executemany(
        "INSERT INTO wellbeing_record(student_id, week_start, stress_level, sleep_hours) "
        "VALUES (?, ?, ?, ?)",
        [
            ("STU001", "2025-01-06", 3, 6),
            ("STU002", "2025-01-06", 5, 8),
            ("STU001", "2025-01-13", 2, 7),
        ],
    )
    test_db.commit()

    df = data_loader.load_aggregate_wellbeing_trend()

    # Expect 2 weeks
    assert set(df["week_start"]) == {"2025-01-06", "2025-01-13"}
    # Week 1 averages: (3+5)/2 = 4, (6+8)/2 = 7
    row_week1 = df[df["week_start"] == "2025-01-06"].iloc[0]
    assert pytest.approx(row_week1["avg_stress"], 0.001) == 4.0
    assert pytest.approx(row_week1["avg_sleep"], 0.001) == 7.0


# ---------- Tests: load_course_performance_summary ----------

def test_load_course_performance_summary_merges_grades_and_attendance(test_db):
    cur = test_db.cursor()
    # Module CS101, students STU1, STU2
    cur.execute("INSERT INTO assessment(assessment_id, module_code, title) VALUES (1, 'CS101', 'Test 1')")
    cur.executemany(
        "INSERT INTO submission(student_id, assessment_id, mark) VALUES (?, ?, ?)",
        [
            ("STU1", 1, 60),
            ("STU2", 1, 80),
        ],
    )

    # attendance: session_id uses module code as prefix
    cur.executemany(
        "INSERT INTO attendance(student_id, session_id, status) VALUES (?, ?, ?)",
        [
            ("STU1", "CS101-01", "PRESENT"),
            ("STU1", "CS101-01", "ABSENT"),
            ("STU2", "CS101-01", "PRESENT"),
        ],
    )
    test_db.commit()

    df = data_loader.load_course_performance_summary()

    # Should have a row for CS101
    assert "CS101" in set(df["module_code"])

    row = df[df["module_code"] == "CS101"].iloc[0]
    # avg_mark = (60 + 80) / 2 = 70
    assert pytest.approx(row["avg_mark"], 0.001) == 70.0
    # attendance_rate = PRESENT / total = 2/3 * 100 ~ 66.67
    assert pytest.approx(row["attendance_rate"], 0.01) == pytest.approx(66.6667, 0.01)


# ---------- Tests: load_full_export_data & risk flags ----------

def test_load_full_export_data_includes_basic_columns(test_db):
    cur = test_db.cursor()

    # one student with minimal info, no related records
    cur.execute("""
        INSERT INTO student(student_id, first_name, lastname, email, year)
        VALUES ('STU100', 'Alice', 'Ng', 'alice@example.com', 2025)
    """)

    test_db.commit()

    df = data_loader.load_full_export_data()

    # columns and single row should exist
    assert len(df) == 1
    assert "student_id" in df.columns
    assert "first_name" in df.columns
    assert "lastname" in df.columns
    assert "Risk_Status" in df.columns
    assert df.loc[0, "student_id"] == "STU100"
    # with no data, risk should default to Normal
    assert df.loc[0, "Risk_Status"] == "Normal"


def test_load_full_export_data_sets_risk_flags_correctly(test_db):
    cur = test_db.cursor()

    # high risk student
    cur.execute("""
        INSERT INTO student(student_id, first_name, lastname, email, year)
        VALUES ('STURISK', 'Bob', 'Khan', 'bob@example.com', 2025)
    """)
    # normal student
    cur.execute("""
        INSERT INTO student(student_id, first_name, lastname, email, year)
        VALUES ('STUNORM', 'Cara', 'Lee', 'cara@example.com', 2025)
    """)

    # Grades: high risk < 50, normal > 50
    cur.executemany(
        "INSERT INTO assessment(assessment_id, module_code, title) VALUES (?, ?, ?)",
        [
            (1, "CS101", "Test 1"),
            (2, "CS101", "Test 2"),
        ],
    )
    cur.executemany(
        "INSERT INTO submission(student_id, assessment_id, mark) VALUES (?, ?, ?)",
        [
            ("STURISK", 1, 40),
            ("STUNORM", 1, 70),
        ],
    )

    # Attendance: high risk < 80%, normal >= 80%
    cur.executemany(
        "INSERT INTO attendance(student_id, session_id, status) VALUES (?, ?, ?)",
        [
            ("STURISK", "CS101-01", "PRESENT"),
            ("STURISK", "CS101-02", "ABSENT"),
            ("STURISK", "CS101-03", "ABSENT"),   # 1/3 present => 33.3%
            ("STUNORM", "CS101-01", "PRESENT"),
            ("STUNORM", "CS101-02", "PRESENT"),  # 2/2 present => 100%
        ],
    )

    # Wellbeing: high risk stress >= 4, sleep < 6
    cur.executemany(
        "INSERT INTO wellbeing_record(student_id, week_start, stress_level, sleep_hours) "
        "VALUES (?, ?, ?, ?)",
        [
            ("STURISK", "2025-01-06", 4.5, 5.0),
            ("STUNORM", "2025-01-06", 2.0, 7.5),
        ],
    )

    test_db.commit()

    df = data_loader.load_full_export_data()

    risk_row = df[df["student_id"] == "STURISK"].iloc[0]
    normal_row = df[df["student_id"] == "STUNORM"].iloc[0]

    # High-risk student should have multiple flags
    risk_status = risk_row["Risk_Status"]
    assert "AT RISK" in risk_status
    assert "High Stress" in risk_status
    assert "Low Sleep" in risk_status
    assert "Low Attendance" in risk_status
    assert "Low Grades" in risk_status

    # Normal student should be "Normal"
    assert normal_row["Risk_Status"] == "Normal"


# ---------- Tests: load_academic_data (per-module correlation dataset) ----------

def test_load_academic_data_for_module_filters_and_merges(test_db):
    cur = test_db.cursor()

    # students
    cur.executemany(
        "INSERT INTO student(student_id, first_name, lastname, email, year) "
        "VALUES (?, ?, ?, ?, ?)",
        [
            ("STU1", "Alice", "Ng", "a@example.com", 2025),
            ("STU2", "Ben", "Li", "b@example.com", 2025),
            ("STU3", "Chris", "Jo", "c@example.com", 2025),  # not enrolled
        ],
    )

    # enrollment only for STU1, STU2 in CS101
    cur.executemany(
        "INSERT INTO enrollment(student_id, module_code) VALUES (?, ?)",
        [
            ("STU1", "CS101"),
            ("STU2", "CS101"),
        ],
    )

    # assessments & grades
    cur.execute("INSERT INTO assessment(assessment_id, module_code, title) VALUES (1, 'CS101', 'Test')")
    cur.executemany(
        "INSERT INTO submission(student_id, assessment_id, mark) VALUES (?, ?, ?)",
        [
            ("STU1", 1, 50),
            ("STU2", 1, 75),
        ],
    )

    # attendance: only PRESENT counts towards present_count
    cur.executemany(
        "INSERT INTO attendance(student_id, session_id, status) VALUES (?, ?, ?)",
        [
            ("STU1", "CS101-01", "PRESENT"),
            ("STU1", "CS101-02", "ABSENT"),
            ("STU2", "CS101-01", "PRESENT"),
            ("STU2", "CS101-02", "PRESENT"),
            ("STU3", "CS101-01", "PRESENT"),  # not enrolled, should not appear for CS101
        ],
    )

    test_db.commit()

    df = data_loader.load_academic_data("CS101")

    # Only enrolled students for the module should appear
    assert set(df["student_id"]) == {"STU1", "STU2"}

    stu1 = df[df["student_id"] == "STU1"].iloc[0]
    stu2 = df[df["student_id"] == "STU2"].iloc[0]

    # avg_mark per student
    assert pytest.approx(stu1["avg_mark"], 0.001) == 50.0
    assert pytest.approx(stu2["avg_mark"], 0.001) == 75.0

    # present_count counts only PRESENT rows for that student and module
    assert stu1["present_count"] == 1  # 1 PRESENT, 1 ABSENT
    assert stu2["present_count"] == 2  # 2 PRESENT


def test_load_academic_data_without_module_returns_all_students(test_db):
    cur = test_db.cursor()

    cur.executemany(
        "INSERT INTO student(student_id, first_name, lastname, email, year) "
        "VALUES (?, ?, ?, ?, ?)",
        [
            ("STU1", "Alice", "Ng", "a@example.com", 2025),
            ("STU2", "Ben", "Li", "b@example.com", 2025),
        ],
    )

    # A single assessment with marks for both
    cur.execute("INSERT INTO assessment(assessment_id, module_code, title) VALUES (1, 'CS101', 'Test')")
    cur.executemany(
        "INSERT INTO submission(student_id, assessment_id, mark) VALUES (?, ?, ?)",
        [
            ("STU1", 1, 50),
            ("STU2", 1, 100),
        ],
    )
    # Attendance for both
    cur.executemany(
        "INSERT INTO attendance(student_id, session_id, status) VALUES (?, ?, ?)",
        [
            ("STU1", "CS101-01", "PRESENT"),
            ("STU2", "CS101-01", "PRESENT"),
        ],
    )
    test_db.commit()

    df = data_loader.load_academic_data()

    assert set(df["student_id"]) == {"STU1", "STU2"}
    # Ensure both avg_mark and present_count are present and non-null
    assert not df["avg_mark"].isna().any()
    assert not df["present_count"].isna().any()
