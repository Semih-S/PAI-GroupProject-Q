"""
Tests for AttendanceRepository class.
Tests attendance record persistence, retrieval, and deletion operations.
"""

import pytest
from datetime import date
from unittest.mock import Mock, patch

from Student_Wellbeing_App.core.models.AttendanceRecord import AttendanceRecord
from Student_Wellbeing_App.core.models.AttendanceStatus import AttendanceStatus
from Student_Wellbeing_App.core.repositories.AttendanceRepository import AttendanceRepository


class TestAttendanceRepositorySave:
    """Test suite for saving attendance records to database."""

    @patch('Student_Wellbeing_App.core.repositories.AttendanceRepository.get_db_connection')
    def test_save_attendance_with_all_fields(self, mock_get_db):
        """Verify attendance record can be saved with all required fields."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        record = AttendanceRecord(
            attendance_id=1,
            student_id="S001",
            session_date=date(2025, 1, 15),
            session_id="SES001",
            status=AttendanceStatus.PRESENT
        )

        repo = AttendanceRepository()
        repo.save(record)

        # Verify the cursor executed the insert
        assert mock_cursor.execute.called
        call_args = mock_cursor.execute.call_args
        assert "INSERT INTO attendance" in call_args[0][0]
        assert call_args[0][1] == (1, "S001", date(
            2025, 1, 15), "SES001", "Present")

    @patch('Student_Wellbeing_App.core.repositories.AttendanceRepository.get_db_connection')
    def test_save_attendance_with_present_status(self, mock_get_db):
        """Verify attendance record with PRESENT status saves correctly."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        record = AttendanceRecord(
            attendance_id=2,
            student_id="S002",
            session_date=date(2025, 1, 16),
            session_id="SES002",
            status=AttendanceStatus.PRESENT
        )

        repo = AttendanceRepository()
        repo.save(record)

        call_args = mock_cursor.execute.call_args
        assert call_args[0][1][4] == "Present"

    @patch('Student_Wellbeing_App.core.repositories.AttendanceRepository.get_db_connection')
    def test_save_attendance_with_absent_status(self, mock_get_db):
        """Verify attendance record with ABSENT status saves correctly."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        record = AttendanceRecord(
            attendance_id=3,
            student_id="S003",
            session_date=date(2025, 1, 17),
            session_id="SES003",
            status=AttendanceStatus.ABSENT
        )

        repo = AttendanceRepository()
        repo.save(record)

        call_args = mock_cursor.execute.call_args
        assert call_args[0][1][4] == "Absent"

    @patch('Student_Wellbeing_App.core.repositories.AttendanceRepository.get_db_connection')
    def test_save_attendance_with_excused_status(self, mock_get_db):
        """Verify attendance record with EXCUSED status saves correctly."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        record = AttendanceRecord(
            attendance_id=4,
            student_id="S004",
            session_date=date(2025, 1, 18),
            session_id="SES004",
            status=AttendanceStatus.EXCUSED
        )

        repo = AttendanceRepository()
        repo.save(record)

        call_args = mock_cursor.execute.call_args
        assert call_args[0][1][4] == "Excused"

    @patch('Student_Wellbeing_App.core.repositories.AttendanceRepository.get_db_connection')
    def test_save_attendance_closes_connection(self, mock_get_db):
        """Verify database connection closes after save."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        record = AttendanceRecord(
            attendance_id=5,
            student_id="S005",
            session_date=date(2025, 1, 19),
            session_id="SES005",
            status=AttendanceStatus.PRESENT
        )

        repo = AttendanceRepository()
        repo.save(record)

        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()


class TestAttendanceRepositoryGetByStudent:
    """Test suite for retrieving attendance records by student."""

    @patch('Student_Wellbeing_App.core.repositories.AttendanceRepository.get_db_connection')
    def test_get_by_student_returns_all_records(self, mock_get_db):
        """Verify get_by_student returns all attendance records for a student."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            (1, "S001", date(2025, 1, 15), "SES001", "Present"),
            (2, "S001", date(2025, 1, 16), "SES002", "Absent"),
        ]

        repo = AttendanceRepository()
        records = repo.get_by_student(1)

        # Verify the query
        call_args = mock_cursor.execute.call_args
        assert "SELECT attendance_id,student_id,session_date,session_id,status FROM attendance WHERE student_id=?" in call_args[
            0][0]
        assert call_args[0][1] == (1,)

        # Verify records are returned
        assert len(records) == 2
        assert isinstance(records[0], AttendanceRecord)
        assert records[0].attendance_id == 1
        assert records[1].attendance_id == 2

    @patch('Student_Wellbeing_App.core.repositories.AttendanceRepository.get_db_connection')
    def test_get_by_student_returns_empty_when_no_records(self, mock_get_db):
        """Verify get_by_student returns empty list when student has no records."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        repo = AttendanceRepository()
        records = repo.get_by_student(999)

        assert records == []
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('Student_Wellbeing_App.core.repositories.AttendanceRepository.get_db_connection')
    def test_get_by_student_creates_correct_objects(self, mock_get_db):
        """Verify AttendanceRecord objects are properly created from database rows."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            (10, "S010", date(2025, 2, 1), "SES010", "Present"),
        ]

        repo = AttendanceRepository()
        records = repo.get_by_student(10)

        assert len(records) == 1
        record = records[0]
        assert record.attendance_id == 10
        assert record.student_id == "S010"
        assert record.session_date == date(2025, 2, 1)
        assert record.session_id == "SES010"
        assert record.status == AttendanceStatus.PRESENT

    @patch('Student_Wellbeing_App.core.repositories.AttendanceRepository.get_db_connection')
    def test_get_by_student_with_multiple_statuses(self, mock_get_db):
        """Verify records with different statuses are retrieved correctly."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            (1, "S011", date(2025, 2, 1), "SES001", "Present"),
            (2, "S011", date(2025, 2, 2), "SES002", "Absent"),
            (3, "S011", date(2025, 2, 3), "SES003", "Excused"),
        ]

        repo = AttendanceRepository()
        records = repo.get_by_student(11)

        assert len(records) == 3
        assert records[0].status == AttendanceStatus.PRESENT
        assert records[1].status == AttendanceStatus.ABSENT
        assert records[2].status == AttendanceStatus.EXCUSED

    @patch('Student_Wellbeing_App.core.repositories.AttendanceRepository.get_db_connection')
    def test_get_by_student_with_large_student_id(self, mock_get_db):
        """Verify large student ID values are handled correctly."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        repo = AttendanceRepository()
        repo.get_by_student(999999)

        call_args = mock_cursor.execute.call_args
        assert call_args[0][1] == (999999,)


class TestAttendanceRepositoryDelete:
    """Test suite for deleting attendance records."""

    @patch('Student_Wellbeing_App.core.repositories.AttendanceRepository.get_db_connection')
    def test_delete_attendance_by_id(self, mock_get_db):
        """Verify attendance record is deleted by ID."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        repo = AttendanceRepository()
        repo.delete(1)

        # Verify the delete query
        assert mock_cursor.execute.called
        call_args = mock_cursor.execute.call_args
        assert "DELETE FROM attendance WHERE attendance_id=?" in call_args[0][0]
        assert call_args[0][1] == (1,)

    @patch('Student_Wellbeing_App.core.repositories.AttendanceRepository.get_db_connection')
    def test_delete_multiple_different_records(self, mock_get_db):
        """Verify different records can be deleted independently."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        repo = AttendanceRepository()

        for attendance_id in [1, 5, 10, 99]:
            repo.delete(attendance_id)

        # Verify execute was called for each
        assert mock_cursor.execute.call_count == 4

    @patch('Student_Wellbeing_App.core.repositories.AttendanceRepository.get_db_connection')
    def test_delete_closes_connection(self, mock_get_db):
        """Verify database connection closes after delete."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        repo = AttendanceRepository()
        repo.delete(1)

        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('Student_Wellbeing_App.core.repositories.AttendanceRepository.get_db_connection')
    def test_delete_nonexistent_record(self, mock_get_db):
        """Verify deleting non-existent record doesn't error."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        repo = AttendanceRepository()
        # Should not raise error even if record doesn't exist
        repo.delete(999)

        assert mock_cursor.execute.called
        mock_cursor.close.assert_called_once()


class TestAttendanceRepositoryIntegration:
    """Integration tests for AttendanceRepository workflows."""

    @patch('Student_Wellbeing_App.core.repositories.AttendanceRepository.get_db_connection')
    def test_save_and_retrieve_workflow(self, mock_get_db):
        """Verify save followed by get_by_student workflow."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        repo = AttendanceRepository()

        # Save a record
        record = AttendanceRecord(
            attendance_id=20,
            student_id="S020",
            session_date=date(2025, 2, 10),
            session_id="SES020",
            status=AttendanceStatus.PRESENT
        )
        repo.save(record)

        # Retrieve records
        mock_cursor.fetchall.return_value = [
            (20, "S020", date(2025, 2, 10), "SES020", "Present"),
        ]
        records = repo.get_by_student(20)

        assert len(records) == 1
        assert records[0].student_id == "S020"

    @patch('Student_Wellbeing_App.core.repositories.AttendanceRepository.get_db_connection')
    def test_save_delete_workflow(self, mock_get_db):
        """Verify save followed by delete workflow."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        repo = AttendanceRepository()

        # Save record
        record = AttendanceRecord(
            attendance_id=21,
            student_id="S021",
            session_date=date(2025, 2, 11),
            session_id="SES021",
            status=AttendanceStatus.ABSENT
        )
        repo.save(record)

        # Delete record
        repo.delete(21)

        # Verify both operations executed
        assert mock_cursor.execute.call_count == 2

    @patch('Student_Wellbeing_App.core.repositories.AttendanceRepository.get_db_connection')
    def test_multiple_operations_connection_management(self, mock_get_db):
        """Verify connection management across multiple operations."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        repo = AttendanceRepository()

        # Perform multiple operations
        record = AttendanceRecord(1, "S001", date(
            2025, 1, 1), "SES001", AttendanceStatus.PRESENT)
        repo.save(record)
        repo.get_by_student(1)
        repo.delete(1)

        # Verify get_db_connection was called 3 times
        assert mock_get_db.call_count == 3
        # Verify close was called for each connection
        assert mock_cursor.close.call_count == 3
        assert mock_conn.close.call_count == 3


class TestAttendanceRepositoryErrorHandling:
    """Test suite for error handling in AttendanceRepository."""

    @patch('Student_Wellbeing_App.core.repositories.AttendanceRepository.get_db_connection')
    def test_save_handles_database_error(self, mock_get_db):
        """Verify save propagates database errors."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")

        repo = AttendanceRepository()
        record = AttendanceRecord(1, "S001", date(
            2025, 1, 1), "SES001", AttendanceStatus.PRESENT)

        with pytest.raises(Exception):
            repo.save(record)

    @patch('Student_Wellbeing_App.core.repositories.AttendanceRepository.get_db_connection')
    def test_get_by_student_handles_database_error(self, mock_get_db):
        """Verify get_by_student propagates database errors."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")

        repo = AttendanceRepository()

        with pytest.raises(Exception):
            repo.get_by_student(1)

    @patch('Student_Wellbeing_App.core.repositories.AttendanceRepository.get_db_connection')
    def test_delete_handles_database_error(self, mock_get_db):
        """Verify delete propagates database errors."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")

        repo = AttendanceRepository()

        with pytest.raises(Exception):
            repo.delete(1)


class TestAttendanceRepositoryDataValidation:
    """Test suite for data validation in AttendanceRepository."""

    @patch('Student_Wellbeing_App.core.repositories.AttendanceRepository.get_db_connection')
    def test_save_with_various_dates(self, mock_get_db):
        """Verify attendance records with various dates save correctly."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        repo = AttendanceRepository()

        test_dates = [
            date(2025, 1, 1),
            date(2025, 12, 31),
            date(2024, 2, 29),  # Leap year
        ]

        for test_date in test_dates:
            record = AttendanceRecord(
                1, "S001", test_date, "SES001", AttendanceStatus.PRESENT)
            repo.save(record)

        # Verify each save executed
        assert mock_cursor.execute.call_count == 3

    @patch('Student_Wellbeing_App.core.repositories.AttendanceRepository.get_db_connection')
    def test_get_by_student_preserves_all_fields(self, mock_get_db):
        """Verify all fields are preserved when retrieving records."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        test_date = date(2025, 3, 15)
        mock_cursor.fetchall.return_value = [
            (99, "S099", test_date, "SES099", "Excused"),
        ]

        repo = AttendanceRepository()
        records = repo.get_by_student(99)

        record = records[0]
        assert record.attendance_id == 99
        assert record.student_id == "S099"
        assert record.session_date == test_date
        assert record.session_id == "SES099"
        assert record.status == AttendanceStatus.EXCUSED
