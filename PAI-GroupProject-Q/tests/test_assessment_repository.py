import pytest
import sqlite3
from unittest.mock import MagicMock, patch
from datetime import date

from src.Student_Wellbeing_App.core.repositories.AssessmentRepository import AssessmentRepository
from src.Student_Wellbeing_App.core.models.Assessment import Assessment

# Schema definition
SCHEMA_SQL = """
CREATE TABLE assessment (
    assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_code TEXT NOT NULL,
    title TEXT NOT NULL,
    due_date DATE NOT NULL,
    weight REAL NOT NULL
);
"""

@pytest.fixture
def mock_db_conn():
    """
    Creates an in-memory database connection.
    Mocks the close() method to prevent the repository from closing the connection prematurely.
    Registers a date adapter to silence Python 3.12+ DeprecationWarnings.
    """
    # Register an adapter so sqlite3 knows how to handle datetime.date objects.
    # This converts the date to an ISO format string before storing.
    sqlite3.register_adapter(date, lambda d: d.isoformat())

    # 1. Create the real in-memory connection
    real_conn = sqlite3.connect(":memory:")
    cur = real_conn.cursor()
    cur.executescript(SCHEMA_SQL)
    real_conn.commit()

    # 2. Create a Mock object as a proxy
    mock_conn = MagicMock()
    
    # 3. Forward critical methods to the real connection
    mock_conn.cursor.side_effect = real_conn.cursor
    mock_conn.execute.side_effect = real_conn.execute
    mock_conn.commit.side_effect = real_conn.commit
    mock_conn.rollback.side_effect = real_conn.rollback
    
    # 4. Critical: Make .close() do nothing
    mock_conn.close.return_value = None

    yield mock_conn

    # 5. Clean up: Actually close the real DB after test finishes
    real_conn.close()

@pytest.fixture
def repository(mock_db_conn):
    """Initializes Repository with the mock connection."""
    with patch("src.Student_Wellbeing_App.core.repositories.AssessmentRepository.get_db_connection", return_value=mock_db_conn):
        yield AssessmentRepository()

class TestAssessmentRepository:

    def test_save_assessment(self, repository):
        """Test: Save a new Assessment record."""
        # Prepare data
        new_assessment = Assessment(
            assessment_id=0,
            module_code="CS101",
            title="Assignment 1",
            due_date=date(2023, 12, 25),
            weight=0.5
        )

        # Execute save
        new_id = repository.save(new_assessment)

        # Verify ID validity
        assert new_id is not None
        assert new_id > 0

        # Verify data persistence
        assessments = repository.get_by_module("CS101")
        assert len(assessments) == 1
        saved = assessments[0]
        
        assert saved.module_code == "CS101"
        assert saved.title == "Assignment 1"
        assert saved.weight == 0.5
        
        # We compare the string representation to ensure correctness.
        assert str(saved.due_date) == "2023-12-25"

    def test_get_by_module_returns_correct_objects(self, repository):
        """Test: Retrieve Assessments by module_code."""
        # Insert records for CS102
        a1 = Assessment(0, "CS102", "Midterm", date(2024, 1, 15), 0.3)
        a2 = Assessment(0, "CS102", "Final", date(2024, 5, 20), 0.7)
        # Insert a record for CS103 (Distractor)
        a3 = Assessment(0, "CS103", "Project", date(2024, 3, 10), 1.0)

        repository.save(a1)
        repository.save(a2)
        repository.save(a3)

        # Query for CS102
        results = repository.get_by_module("CS102")

        assert len(results) == 2
        
        # Verify return type
        assert isinstance(results[0], Assessment)
        
        # Verify content
        titles = [a.title for a in results]
        assert "Midterm" in titles
        assert "Final" in titles
        assert "Project" not in titles

    def test_get_by_module_returns_empty_list_if_not_found(self, repository):
        """Test: Querying a non-existent module_code returns an empty list."""
        results = repository.get_by_module("NON_EXISTENT_CODE")
        assert isinstance(results, list)
        assert len(results) == 0
