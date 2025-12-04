"""
Tests for AuditRepository class.
Tests audit log persistence and logging operations.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from Student_Wellbeing_App.core.models.AuditLog import AuditLog
from Student_Wellbeing_App.core.repositories.AuditRepository import AuditRepository


class TestAuditRepositoryLog:
    """Test suite for logging audit records to database."""

    @patch('Student_Wellbeing_App.core.repositories.AuditRepository.get_db_connection')
    def test_log_audit_with_all_fields(self, mock_get_db):
        """Verify audit log can be saved with all required fields."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        log = AuditLog(
            log_id=1,
            user_id=101,
            entitiy_type="Student",
            entity_id=1001,
            action_type="CREATE",
            timestamp=datetime(2025, 1, 15, 10, 30, 0),
            details="Created new student record"
        )

        repo = AuditRepository()
        repo.log(log)

        # Verify the cursor executed the insert
        assert mock_cursor.execute.called
        call_args = mock_cursor.execute.call_args
        assert "INSERT INTO audit_log" in call_args[0][0]
        assert call_args[0][1] == (101, "Student", 1001, "CREATE",
                                   datetime(2025, 1, 15, 10, 30, 0), "Created new student record")

    @patch('Student_Wellbeing_App.core.repositories.AuditRepository.get_db_connection')
    def test_log_audit_with_create_action(self, mock_get_db):
        """Verify audit log with CREATE action type saves correctly."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        log = AuditLog(
            log_id=2,
            user_id=102,
            entitiy_type="User",
            entity_id=2001,
            action_type="CREATE",
            timestamp=datetime.now(),
            details="User account created"
        )

        repo = AuditRepository()
        repo.log(log)

        call_args = mock_cursor.execute.call_args
        assert call_args[0][1][3] == "CREATE"

    @patch('Student_Wellbeing_App.core.repositories.AuditRepository.get_db_connection')
    def test_log_audit_with_update_action(self, mock_get_db):
        """Verify audit log with UPDATE action type saves correctly."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        log = AuditLog(
            log_id=3,
            user_id=103,
            entitiy_type="Student",
            entity_id=1002,
            action_type="UPDATE",
            timestamp=datetime.now(),
            details="Updated student information"
        )

        repo = AuditRepository()
        repo.log(log)

        call_args = mock_cursor.execute.call_args
        assert call_args[0][1][3] == "UPDATE"

    @patch('Student_Wellbeing_App.core.repositories.AuditRepository.get_db_connection')
    def test_log_audit_with_delete_action(self, mock_get_db):
        """Verify audit log with DELETE action type saves correctly."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        log = AuditLog(
            log_id=4,
            user_id=104,
            entitiy_type="WellbeingRecord",
            entity_id=3001,
            action_type="DELETE",
            timestamp=datetime.now(),
            details="Deleted old wellbeing record"
        )

        repo = AuditRepository()
        repo.log(log)

        call_args = mock_cursor.execute.call_args
        assert call_args[0][1][3] == "DELETE"

    @patch('Student_Wellbeing_App.core.repositories.AuditRepository.get_db_connection')
    def test_log_audit_with_view_action(self, mock_get_db):
        """Verify audit log with VIEW action type saves correctly."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        log = AuditLog(
            log_id=5,
            user_id=105,
            entitiy_type="Alert",
            entity_id=4001,
            action_type="VIEW",
            timestamp=datetime.now(),
            details="Viewed alert details"
        )

        repo = AuditRepository()
        repo.log(log)

        call_args = mock_cursor.execute.call_args
        assert call_args[0][1][3] == "VIEW"

    @patch('Student_Wellbeing_App.core.repositories.AuditRepository.get_db_connection')
    def test_log_audit_closes_connection(self, mock_get_db):
        """Verify database connection closes after logging."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        log = AuditLog(
            log_id=6,
            user_id=106,
            entitiy_type="Student",
            entity_id=1003,
            action_type="CREATE",
            timestamp=datetime.now(),
            details="Test"
        )

        repo = AuditRepository()
        repo.log(log)

        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()


class TestAuditRepositoryEntityTypes:
    """Test suite for various entity types in audit logs."""

    @patch('Student_Wellbeing_App.core.repositories.AuditRepository.get_db_connection')
    def test_log_audit_for_student_entity(self, mock_get_db):
        """Verify audit log with Student entity type."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        log = AuditLog(
            log_id=10,
            user_id=110,
            entitiy_type="Student",
            entity_id=5001,
            action_type="CREATE",
            timestamp=datetime.now(),
            details=""
        )

        repo = AuditRepository()
        repo.log(log)

        call_args = mock_cursor.execute.call_args
        assert call_args[0][1][1] == "Student"

    @patch('Student_Wellbeing_App.core.repositories.AuditRepository.get_db_connection')
    def test_log_audit_for_user_entity(self, mock_get_db):
        """Verify audit log with User entity type."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        log = AuditLog(
            log_id=11,
            user_id=111,
            entitiy_type="User",
            entity_id=5002,
            action_type="CREATE",
            timestamp=datetime.now(),
            details=""
        )

        repo = AuditRepository()
        repo.log(log)

        call_args = mock_cursor.execute.call_args
        assert call_args[0][1][1] == "User"

    @patch('Student_Wellbeing_App.core.repositories.AuditRepository.get_db_connection')
    def test_log_audit_for_alert_entity(self, mock_get_db):
        """Verify audit log with Alert entity type."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        log = AuditLog(
            log_id=12,
            user_id=112,
            entitiy_type="Alert",
            entity_id=5003,
            action_type="UPDATE",
            timestamp=datetime.now(),
            details=""
        )

        repo = AuditRepository()
        repo.log(log)

        call_args = mock_cursor.execute.call_args
        assert call_args[0][1][1] == "Alert"

    @patch('Student_Wellbeing_App.core.repositories.AuditRepository.get_db_connection')
    def test_log_audit_for_attendance_entity(self, mock_get_db):
        """Verify audit log with Attendance entity type."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        log = AuditLog(
            log_id=13,
            user_id=113,
            entitiy_type="Attendance",
            entity_id=5004,
            action_type="CREATE",
            timestamp=datetime.now(),
            details=""
        )

        repo = AuditRepository()
        repo.log(log)

        call_args = mock_cursor.execute.call_args
        assert call_args[0][1][1] == "Attendance"


class TestAuditRepositoryDetails:
    """Test suite for audit log details field."""

    @patch('Student_Wellbeing_App.core.repositories.AuditRepository.get_db_connection')
    def test_log_audit_with_empty_details(self, mock_get_db):
        """Verify audit log with empty details string."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        log = AuditLog(
            log_id=20,
            user_id=120,
            entitiy_type="Student",
            entity_id=6001,
            action_type="VIEW",
            timestamp=datetime.now(),
            details=""
        )

        repo = AuditRepository()
        repo.log(log)

        call_args = mock_cursor.execute.call_args
        assert call_args[0][1][5] == ""

    @patch('Student_Wellbeing_App.core.repositories.AuditRepository.get_db_connection')
    def test_log_audit_with_long_details(self, mock_get_db):
        """Verify audit log with lengthy details string."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        long_details = "A" * 500
        log = AuditLog(
            log_id=21,
            user_id=121,
            entitiy_type="Student",
            entity_id=6002,
            action_type="UPDATE",
            timestamp=datetime.now(),
            details=long_details
        )

        repo = AuditRepository()
        repo.log(log)

        call_args = mock_cursor.execute.call_args
        assert call_args[0][1][5] == long_details

    @patch('Student_Wellbeing_App.core.repositories.AuditRepository.get_db_connection')
    def test_log_audit_with_special_characters_in_details(self, mock_get_db):
        """Verify audit log with special characters in details."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        special_details = "Updated record with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        log = AuditLog(
            log_id=22,
            user_id=122,
            entitiy_type="User",
            entity_id=6003,
            action_type="UPDATE",
            timestamp=datetime.now(),
            details=special_details
        )

        repo = AuditRepository()
        repo.log(log)

        call_args = mock_cursor.execute.call_args
        assert call_args[0][1][5] == special_details


class TestAuditRepositoryTimestamps:
    """Test suite for timestamp handling in audit logs."""

    @patch('Student_Wellbeing_App.core.repositories.AuditRepository.get_db_connection')
    def test_log_audit_with_various_timestamps(self, mock_get_db):
        """Verify audit logs with various timestamp values."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        repo = AuditRepository()

        timestamps = [
            datetime(2025, 1, 1, 0, 0, 0),
            datetime(2025, 12, 31, 23, 59, 59),
            datetime(2024, 2, 29, 12, 30, 45),  # Leap year
        ]

        for i, ts in enumerate(timestamps):
            log = AuditLog(
                log_id=30+i,
                user_id=130+i,
                entitiy_type="Student",
                entity_id=7001+i,
                action_type="CREATE",
                timestamp=ts,
                details=""
            )
            repo.log(log)

        assert mock_cursor.execute.call_count == 3

    @patch('Student_Wellbeing_App.core.repositories.AuditRepository.get_db_connection')
    def test_log_audit_preserves_timestamp_precision(self, mock_get_db):
        """Verify timestamp precision is preserved when logging."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        ts = datetime(2025, 3, 15, 14, 30, 45, 123456)
        log = AuditLog(
            log_id=33,
            user_id=133,
            entitiy_type="Alert",
            entity_id=7004,
            action_type="VIEW",
            timestamp=ts,
            details=""
        )

        repo = AuditRepository()
        repo.log(log)

        call_args = mock_cursor.execute.call_args
        assert call_args[0][1][4] == ts


class TestAuditRepositoryUserIds:
    """Test suite for user ID handling in audit logs."""

    @patch('Student_Wellbeing_App.core.repositories.AuditRepository.get_db_connection')
    def test_log_audit_with_various_user_ids(self, mock_get_db):
        """Verify audit logs with various user ID values."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        repo = AuditRepository()

        user_ids = [1, 100, 999, 10000]

        for i, uid in enumerate(user_ids):
            log = AuditLog(
                log_id=40+i,
                user_id=uid,
                entitiy_type="Student",
                entity_id=8001+i,
                action_type="CREATE",
                timestamp=datetime.now(),
                details=""
            )
            repo.log(log)

        assert mock_cursor.execute.call_count == 4

    @patch('Student_Wellbeing_App.core.repositories.AuditRepository.get_db_connection')
    def test_log_audit_with_zero_user_id(self, mock_get_db):
        """Verify audit log with zero user ID."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        log = AuditLog(
            log_id=50,
            user_id=0,
            entitiy_type="System",
            entity_id=9001,
            action_type="SYSTEM_EVENT",
            timestamp=datetime.now(),
            details="System initiated operation"
        )

        repo = AuditRepository()
        repo.log(log)

        call_args = mock_cursor.execute.call_args
        assert call_args[0][1][0] == 0


class TestAuditRepositoryIntegration:
    """Integration tests for AuditRepository workflows."""

    @patch('Student_Wellbeing_App.core.repositories.AuditRepository.get_db_connection')
    def test_multiple_sequential_logs(self, mock_get_db):
        """Verify multiple sequential logging operations work correctly."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        repo = AuditRepository()

        logs = [
            AuditLog(1, 101, "Student", 1001, "CREATE",
                     datetime.now(), "Created"),
            AuditLog(2, 101, "Student", 1001, "UPDATE",
                     datetime.now(), "Updated"),
            AuditLog(3, 102, "Alert", 2001, "VIEW", datetime.now(), "Viewed"),
        ]

        for log in logs:
            repo.log(log)

        assert mock_cursor.execute.call_count == 3
        assert mock_cursor.close.call_count == 3

    @patch('Student_Wellbeing_App.core.repositories.AuditRepository.get_db_connection')
    def test_audit_trail_for_single_entity(self, mock_get_db):
        """Verify complete audit trail for a single entity."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        repo = AuditRepository()
        entity_id = 5001

        actions = ["CREATE", "UPDATE", "UPDATE", "VIEW", "DELETE"]

        for i, action in enumerate(actions):
            log = AuditLog(
                log_id=60+i,
                user_id=160,
                entitiy_type="Student",
                entity_id=entity_id,
                action_type=action,
                timestamp=datetime.now(),
                details=f"Action: {action}"
            )
            repo.log(log)

        assert mock_cursor.execute.call_count == 5


class TestAuditRepositoryErrorHandling:
    """Test suite for error handling in AuditRepository."""

    @patch('Student_Wellbeing_App.core.repositories.AuditRepository.get_db_connection')
    def test_log_handles_database_error(self, mock_get_db):
        """Verify log propagates database errors."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")

        repo = AuditRepository()
        log = AuditLog(
            log_id=70,
            user_id=170,
            entitiy_type="Student",
            entity_id=10001,
            action_type="CREATE",
            timestamp=datetime.now(),
            details="Test"
        )

        with pytest.raises(Exception):
            repo.log(log)

    @patch('Student_Wellbeing_App.core.repositories.AuditRepository.get_db_connection')
    def test_log_handles_connection_error(self, mock_get_db):
        """Verify log handles connection errors."""
        mock_get_db.side_effect = Exception("Connection failed")

        repo = AuditRepository()
        log = AuditLog(
            log_id=71,
            user_id=171,
            entitiy_type="User",
            entity_id=10002,
            action_type="CREATE",
            timestamp=datetime.now(),
            details="Test"
        )

        with pytest.raises(Exception):
            repo.log(log)


class TestAuditRepositoryDataIntegrity:
    """Test suite for data integrity in AuditRepository."""

    @patch('Student_Wellbeing_App.core.repositories.AuditRepository.get_db_connection')
    def test_log_preserves_all_fields_exactly(self, mock_get_db):
        """Verify all audit log fields are preserved exactly."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        timestamp = datetime(2025, 4, 20, 15, 45, 30, 987654)
        details = "Complex details: User 'john.doe' modified record #5001"

        log = AuditLog(
            log_id=80,
            user_id=999,
            entitiy_type="WellbeingRecord",
            entity_id=11001,
            action_type="UPDATE",
            timestamp=timestamp,
            details=details
        )

        repo = AuditRepository()
        repo.log(log)

        call_args = mock_cursor.execute.call_args
        saved_data = call_args[0][1]

        assert saved_data[0] == 999  # user_id
        assert saved_data[1] == "WellbeingRecord"  # entity_type
        assert saved_data[2] == 11001  # entity_id
        assert saved_data[3] == "UPDATE"  # action_type
        assert saved_data[4] == timestamp  # timestamp
        assert saved_data[5] == details  # details

    @patch('Student_Wellbeing_App.core.repositories.AuditRepository.get_db_connection')
    def test_log_with_unicode_characters(self, mock_get_db):
        """Verify audit log handles unicode characters correctly."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        unicode_details = "Updated record: 你好世界 مرحبا بالعالم"
        log = AuditLog(
            log_id=81,
            user_id=181,
            entitiy_type="Student",
            entity_id=12001,
            action_type="UPDATE",
            timestamp=datetime.now(),
            details=unicode_details
        )

        repo = AuditRepository()
        repo.log(log)

        call_args = mock_cursor.execute.call_args
        assert call_args[0][1][5] == unicode_details
