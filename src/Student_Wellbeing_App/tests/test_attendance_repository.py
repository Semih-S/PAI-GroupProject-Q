import pytest
import sqlite3
from unittest.mock import MagicMock, patch
from datetime import date

from src.Student_Wellbeing_App.core.repositories.AttendanceRepository import AttendanceRepository
from src.Student_Wellbeing_App.core.models.AttendanceRecord import AttendanceRecord
from src.Student_Wellbeing_App.core.models.AttendanceStatus import AttendanceStatus

# Schema definition based on the fields used in Repository
SCHEMA_SQL = """
CREATE TABLE attendance (
    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    session_date DATE NOT NULL,
    session_id TEXT NOT NULL,
    status TEXT NOT NULL
);
"""

@pytest.fixture
def mock_db_conn():
    # Fix for DeprecationWarning: Register adapter for date objects
    sqlite3.register_adapter(date, lambda d: d.isoformat())

    # 1. Create real in-memory connection
    real_conn = sqlite3.connect(":memory:")
    cur = real_conn.cursor()
    cur.executescript(SCHEMA_SQL)
    real_conn.commit()

    # 2. Create Mock proxy
    mock_conn = MagicMock()
    
    # 3. Forward critical methods to real connection
    mock_conn.cursor.side_effect = real_conn.cursor
    mock_conn.execute.side_effect = real_conn.execute
    mock_conn.commit.side_effect = real_conn.commit
    mock_conn.rollback.side_effect = real_conn.rollback
    
    # 4. Prevent premature closing
    mock_conn.close.return_value = None

    yield mock_conn

    # 5. Cleanup
    real_conn.close()

@pytest.fixture
def repository(mock_db_conn):
    """Initializes Repository with the mock connection."""
    with patch("src.Student_Wellbeing_App.core.repositories.AttendanceRepository.get_db_connection", return_value=mock_db_conn):
        yield AttendanceRepository()

class TestAttendanceRepository:

    def test_upsert_creates_new_record(self, repository):
        """Test: upsert inserts a new record when it doesn't exist."""
        # Prepare data
        record = AttendanceRecord(
            attendance_id=0, # Placeholder, will be auto-generated
            student_id="S001",
            session_date=date(2025, 1, 15),
            session_id="SES001",
            status=AttendanceStatus.PRESENT
        )

        # Execute upsert
        new_id = repository.upsert(record)

        # Verify ID returned
        assert new_id > 0

        # Verify data in DB
        saved_records = repository.get_by_student("S001")
        assert len(saved_records) == 1
        saved = saved_records[0]
        
        assert saved.student_id == "S001"
        assert saved.session_id == "SES001"
        assert saved.status == AttendanceStatus.PRESENT
        # Check date string representation (due to SQLite storage)
        assert str(saved.session_date) == "2025-01-15"

    def test_upsert_updates_existing_record(self, repository):
        """Test: upsert updates the status if student+date+session already exists."""
        # 1. Insert initial record (PRESENT)
        record = AttendanceRecord(0, "S002", date(2025, 1, 16), "SES002", AttendanceStatus.PRESENT)
        id_1 = repository.upsert(record)

        # 2. Update same record (change to ABSENT)
        record.status = AttendanceStatus.ABSENT
        id_2 = repository.upsert(record)

        # Verify ID remains the same (it was an update, not insert)
        assert id_1 == id_2

        # Verify status updated in DB
        saved_records = repository.get_by_student("S002")
        assert len(saved_records) == 1
        assert saved_records[0].status == AttendanceStatus.ABSENT

    def test_update_status_by_id(self, repository):
        """Test: Update status directly using attendance_id."""
        # Create record
        record = AttendanceRecord(0, "S003", date(2025, 1, 17), "SES003", AttendanceStatus.LATE)
        new_id = repository.upsert(record)

        # Update status
        repository.update_status_by_id(new_id, "EXCUSED")

        # Verify
        saved_records = repository.get_by_student("S003")
        assert saved_records[0].status == AttendanceStatus.EXCUSED

    def test_delete_by_id(self, repository):
        """Test: Delete record by attendance_id."""
        # Create record
        record = AttendanceRecord(0, "S004", date(2025, 1, 18), "SES004", AttendanceStatus.PRESENT)
        new_id = repository.upsert(record)

        # Verify existence
        assert len(repository.get_by_student("S004")) == 1

        # Delete
        repository.delete_by_id(new_id)

        # Verify deletion
        assert len(repository.get_by_student("S004")) == 0

    def test_get_by_student_returns_correct_objects(self, repository):
        """Test: Retrieve records by student_id and ensure Enum conversion works."""
        # Insert mixed records
        r1 = AttendanceRecord(0, "S_TARGET", date(2025, 2, 1), "SES10", AttendanceStatus.PRESENT)
        r2 = AttendanceRecord(0, "S_TARGET", date(2025, 2, 2), "SES11", AttendanceStatus.ABSENT)
        r3 = AttendanceRecord(0, "S_OTHER", date(2025, 2, 1), "SES10", AttendanceStatus.LATE)

        repository.upsert(r1)
        repository.upsert(r2)
        repository.upsert(r3)

        # Query
        results = repository.get_by_student("S_TARGET")

        assert len(results) == 2
        # Check if they are AttendanceRecord instances
        assert isinstance(results[0], AttendanceRecord)
        # Check Enum types
        assert results[0].status == AttendanceStatus.PRESENT
        assert results[1].status == AttendanceStatus.ABSENT

    def test_get_by_session_returns_list(self, repository):
        """Test: Retrieve records by session_id."""
        # Insert records for same session
        r1 = AttendanceRecord(0, "StudentA", date(2025, 3, 1), "LECTURE_1", AttendanceStatus.PRESENT)
        r2 = AttendanceRecord(0, "StudentB", date(2025, 3, 1), "LECTURE_1", AttendanceStatus.LATE)
        r3 = AttendanceRecord(0, "StudentA", date(2025, 3, 2), "LECTURE_2", AttendanceStatus.PRESENT)

        repository.upsert(r1)
        repository.upsert(r2)
        repository.upsert(r3)

        # Query by session
        results = repository.get_by_session("LECTURE_1")

        assert len(results) == 2
        student_ids = [r.student_id for r in results]
        assert "StudentA" in student_ids
        assert "StudentB" in student_ids
