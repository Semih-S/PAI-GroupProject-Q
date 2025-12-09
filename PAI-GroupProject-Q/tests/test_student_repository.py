"""
Tests for StudentRepository class.
Tests student persistence, ID generation (STUxxxx), and authentication.
"""

import pytest
import hashlib
from unittest.mock import Mock, patch, ANY

from src.Student_Wellbeing_App.core.models.Student import Student
from src.Student_Wellbeing_App.core.repositories.StudentRepository import StudentRepository


class TestStudentRepository:
    """Test suite for StudentRepository database operations."""

    @pytest.fixture
    def mock_db(self):
        """
        Fixture to mock the database connection and cursor.
        Returns (mock_conn, mock_cursor).
        """
        with patch('src.Student_Wellbeing_App.core.repositories.StudentRepository.get_db_connection') as mock_connect:
            mock_conn = Mock()
            mock_cursor = Mock()
            
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            
            yield mock_conn, mock_cursor

    def test_save_generates_first_id(self, mock_db):
        """Verify the first student saved gets ID 'STU0001'."""
        mock_conn, mock_cursor = mock_db
        
        # Mock ID check returning None (no existing students)
        mock_cursor.fetchone.return_value = None
        
        repo = StudentRepository()
        student = Student(
            student_id="",  # Placeholder
            first_name="Jane",
            lastname="Doe",
            email="jane@example.com",
            password="hashed_pw",
            year=1
        )
        
        new_id = repo.save(student)
        
        assert new_id == "STU0001"
        assert student.student_id == "STU0001"  # Object should be updated
        
        # Verify INSERT
        mock_cursor.execute.assert_called()
        insert_args = [call for call in mock_cursor.execute.call_args_list if "INSERT INTO student" in call[0][0]]
        assert len(insert_args) == 1
        
        params = insert_args[0][0][1]
        assert params[0] == "STU0001"
        
        mock_conn.commit.assert_called_once()

    def test_save_increments_id(self, mock_db):
        """Verify ID increments correctly from existing max ID."""
        _, mock_cursor = mock_db
        
        # Mock existing max ID
        mock_cursor.fetchone.return_value = ("STU0042",)
        
        repo = StudentRepository()
        student = Student("", "John", "Doe", "john@ex.com", "pw", 2)
        
        new_id = repo.save(student)
        
        assert new_id == "STU0043"

    def test_list_all(self, mock_db):
        """Verify list_all returns a list of Student objects."""
        _, mock_cursor = mock_db
        
        # Mock DB rows (6 columns based on SQL)
        mock_rows = [
            ("STU001", "A", "B", "a@b.com", "pass", 1),
            ("STU002", "C", "D", "c@d.com", "pass", 2),
        ]
        mock_cursor.fetchall.return_value = mock_rows
        
        repo = StudentRepository()
        students = repo.list_all()
        
        assert len(students) == 2
        assert isinstance(students[0], Student)
        assert students[0].student_id == "STU001"
        assert students[1].lastname == "D"

    def test_delete(self, mock_db):
        """Verify delete executes correct SQL."""
        mock_conn, mock_cursor = mock_db
        
        repo = StudentRepository()
        repo.delete("STU0099")
        
        mock_cursor.execute.assert_called_with(
            "DELETE FROM student WHERE student_id = ?", 
            ("STU0099",)
        )
        mock_conn.commit.assert_called_once()

    def test_get_student_by_id_found(self, mock_db):
        """Verify retrieving a single student by ID."""
        _, mock_cursor = mock_db
        
        mock_row = ("STU005", "Test", "User", "t@u.com", "hash", 3)
        mock_cursor.fetchone.return_value = mock_row
        
        repo = StudentRepository()
        student = repo.get_student_by_id("STU005")
        
        assert student is not None
        assert student.student_id == "STU005"
        assert student.email == "t@u.com"

    def test_get_student_by_id_none(self, mock_db):
        """Verify returning None if student does not exist."""
        _, mock_cursor = mock_db
        mock_cursor.fetchone.return_value = None
        
        repo = StudentRepository()
        student = repo.get_student_by_id("NONEXISTENT")
        
        assert student is None

    def test_authenticate_success(self, mock_db):
        """
        Verify authentication succeeds when input password hash matches DB hash.
        """
        _, mock_cursor = mock_db
        
        raw_password = "mySecretPassword"
        # The repo calculates sha256 of input. We simulate the DB storing that hash.
        expected_hash = hashlib.sha256(raw_password.encode()).hexdigest()
        
        # DB returns: student_id, first_name, lastname, email, password(hash), year
        mock_row = ("STU100", "Auth", "User", "auth@test.com", expected_hash, 1)
        mock_cursor.fetchone.return_value = mock_row
        
        repo = StudentRepository()
        result = repo.authenticate_by_id("STU100", raw_password)
        
        assert result is not None
        assert result.student_id == "STU100"
        # Ensure the object contains the hash from DB, not plain text
        assert result.password == expected_hash

    def test_authenticate_wrong_password(self, mock_db):
        """Verify authentication fails when passwords do not match."""
        _, mock_cursor = mock_db
        
        stored_hash = "correct_hash_value"
        mock_row = ("STU100", "Auth", "User", "auth@test.com", stored_hash, 1)
        mock_cursor.fetchone.return_value = mock_row
        
        repo = StudentRepository()
        # Input "wrong" will hash to something else
        result = repo.authenticate_by_id("STU100", "wrong")
        
        assert result is None

    def test_authenticate_user_not_found(self, mock_db):
        """Verify authentication fails if ID is not in DB."""
        _, mock_cursor = mock_db
        mock_cursor.fetchone.return_value = None
        
        repo = StudentRepository()
        result = repo.authenticate_by_id("UNKNOWN", "pass")
        
        assert result is None
