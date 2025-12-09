import pytest
import sqlite3
from unittest.mock import MagicMock, patch
from datetime import date

from src.Student_Wellbeing_App.core.repositories.SubmissionRepository import SubmissionRepository
from src.Student_Wellbeing_App.core.models.SubmissionStatus import SubmissionStatus
from src.Student_Wellbeing_App.core.models.SubmissionRecord import SubmissionRecord

# SQL Schema for setting up the in-memory database
SCHEMA_SQL = """
CREATE TABLE submission (
    submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    assessment_id INTEGER NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL,
    mark REAL
);
"""

@pytest.fixture
def mock_db_conn():
    """
    We use a MagicMock that acts like a proxy. It forwards execution
    calls to the real DB, but ignores the .close() call.
    """
    # 1. Create the REAL in-memory connection
    real_conn = sqlite3.connect(":memory:")
    cur = real_conn.cursor()
    cur.executescript(SCHEMA_SQL)
    real_conn.commit()

    # 2. Create a MOCK object to intercept method calls
    mock_conn = MagicMock()

    # 3. Forward critical methods to the real connection
    mock_conn.cursor.side_effect = real_conn.cursor
    mock_conn.execute.side_effect = real_conn.execute
    mock_conn.commit.side_effect = real_conn.commit
    mock_conn.rollback.side_effect = real_conn.rollback

    # 4. Make .close() a no-op (do nothing)
    mock_conn.close.return_value = None

    yield mock_conn

    # 5. Actually close the real DB after the test finishes
    real_conn.close()

@pytest.fixture
def repository(mock_db_conn):
    """
    Initializes the Repository and patches get_db_connection to return
    our non-closing mock connection.
    """
    with patch("src.Student_Wellbeing_App.core.repositories.SubmissionRepository.get_db_connection", return_value=mock_db_conn):
        yield SubmissionRepository()

class TestSubmissionRepository:

    def test_upsert_grade_creates_new_record(self, repository):
        """Verify: upsert creates a new record if it does not exist."""
        student_id = "S1001"
        assessment_id = 101
        mark = 85.5

        # Execute
        new_id = repository.upsert_grade(student_id, assessment_id, mark)

        # Verify ID is valid
        assert new_id > 0
        
        # Verify data was written (Validation step calls DB again, so connection must stay open)
        results = repository.get_by_student(student_id)
        assert len(results) == 1
        record = results[0]
        
        assert record.student_id == student_id
        assert record.assessment_id == assessment_id
        assert record.mark == mark
        assert record.status == SubmissionStatus.SUBMITTED

    def test_upsert_grade_updates_existing_record(self, repository):
        """Verify: upsert updates the mark if record exists."""
        student_id = "S1001"
        assessment_id = 101
        
        # First insertion (80.0)
        id_1 = repository.upsert_grade(student_id, assessment_id, 80.0)
        
        # Second insertion (90.0) - Should trigger UPDATE
        id_2 = repository.upsert_grade(student_id, assessment_id, 90.0)

        # Verify ID remains the same
        assert id_1 == id_2

        # Verify mark is updated
        results = repository.get_by_student(student_id)
        assert len(results) == 1
        assert results[0].mark == 90.0

    def test_update_mark_by_id(self, repository):
        """Verify: update mark directly by ID."""
        # Create initial record
        sub_id = repository.upsert_grade("S002", 202, 50.0)
        
        # Update
        repository.update_mark_by_id(sub_id, 75.0)
        
        # Verify using a different method
        conn_results = repository.get_by_assessment(202)
        assert conn_results[0]["mark"] == 75.0

    def test_delete_by_id(self, repository):
        """Verify: delete record by ID."""
        sub_id = repository.upsert_grade("S003", 303, 60.0)
        
        # Confirm existence
        assert len(repository.get_by_student("S003")) == 1
        
        # Delete
        repository.delete_by_id(sub_id)
        
        # Confirm deletion
        assert len(repository.get_by_student("S003")) == 0

    def test_get_by_assessment(self, repository):
        """Verify: get all submissions for a specific assessment (returns list of dicts)."""
        # Insert records
        repository.upsert_grade("StudentA", 500, 80.0)
        repository.upsert_grade("StudentB", 500, 90.0)
        repository.upsert_grade("StudentC", 600, 70.0) # Distractor

        results = repository.get_by_assessment(500)
        
        assert len(results) == 2
        # Verify structure
        assert isinstance(results[0], dict)
        assert "mark" in results[0]
        assert "student_id" in results[0]
        
        # Verify content
        student_ids = [r["student_id"] for r in results]
        assert "StudentA" in student_ids
        assert "StudentB" in student_ids
        assert "StudentC" not in student_ids

    def test_get_by_student_returns_model_objects(self, repository):
        """Verify: get_by_student returns SubmissionRecord objects with correct Enum status."""
        student_id = "S_ENUM_TEST"
        repository.upsert_grade(student_id, 1, 100.0)

        records = repository.get_by_student(student_id)
        
        assert len(records) == 1
        record = records[0]

        # Verify type
        assert isinstance(record, SubmissionRecord)
        
        # Verify Status Enum conversion
        assert isinstance(record.status, SubmissionStatus)
        assert record.status == SubmissionStatus.SUBMITTED

    def test_get_by_student_handles_legacy_status(self, repository, mock_db_conn):
        """Verify: Handles unknown status strings by defaulting to SUBMITTED."""
        # Manually insert weird status using the real underlying cursor
        # Note: We use mock_db_conn.execute, which proxies to the real DB
        mock_db_conn.execute(
            "INSERT INTO submission (student_id, assessment_id, status, mark) VALUES (?, ?, ?, ?)",
            ("S_WEIRD", 999, "UNKNOWN_STATUS_CODE", 0.0)
        )
        mock_db_conn.commit()

        # Call Repository
        records = repository.get_by_student("S_WEIRD")
        
        assert len(records) == 1
        # Logic check: r[4] if r[4] in ... else 'SUBMITTED'
        assert records[0].status == SubmissionStatus.SUBMITTED
