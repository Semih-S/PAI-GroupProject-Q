"""
Tests for AlertRepository class.
Tests alert persistence, retrieval, and status management operations.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from Student_Wellbeing_App.core.models.Alert import Alert
from Student_Wellbeing_App.core.repositories.AlertRepository import AlertRepository


class TestAlertRepositorySave:
    """Test suite for saving alerts to database."""

    @patch('Student_Wellbeing_App.core.repositories.AlertRepository.get_db_connection')
    def test_save_alert_with_all_fields(self, mock_get_db):
        """Verify alert can be saved with all required fields."""
        # Mock the database connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Create an alert to save
        alert = Alert(
            alert_id=1,
            student_id="S001",
            alert_type="low_attendance",
            reason="Missed 3 sessions",
            created_at=datetime(2025, 1, 15, 10, 30, 0),
            resolved=0
        )

        # Save the alert
        repo = AlertRepository()
        repo.save(alert)

        # Verify the cursor executed the insert
        assert mock_cursor.execute.called
        call_args = mock_cursor.execute.call_args
        assert "INSERT INTO alert" in call_args[0][0]
        assert call_args[0][1] == ("S001", "low_attendance", "Missed 3 sessions",
                                   datetime(2025, 1, 15, 10, 30, 0), 0)

        # Verify connection was closed
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('Student_Wellbeing_App.core.repositories.AlertRepository.get_db_connection')
    def test_save_alert_unresolved(self, mock_get_db):
        """Verify unresolved alert is saved correctly."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        alert = Alert(
            alert_id=2,
            student_id="S002",
            alert_type="low_wellbeing",
            reason="Declining wellbeing scores",
            created_at=datetime.now(),
            resolved=0
        )

        repo = AlertRepository()
        repo.save(alert)

        # Verify resolved is False (0)
        call_args = mock_cursor.execute.call_args
        assert call_args[0][1][4] == 0

    @patch('Student_Wellbeing_App.core.repositories.AlertRepository.get_db_connection')
    def test_save_alert_resolved(self, mock_get_db):
        """Verify resolved alert can be saved."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        alert = Alert(
            alert_id=3,
            student_id="S003",
            alert_type="low_performance",
            reason="Assessment score below threshold",
            created_at=datetime.now(),
            resolved=1
        )

        repo = AlertRepository()
        repo.save(alert)

        # Verify resolved is True (1)
        call_args = mock_cursor.execute.call_args
        assert call_args[0][1][4] == 1

    @patch('Student_Wellbeing_App.core.repositories.AlertRepository.get_db_connection')
    def test_save_alert_with_empty_reason(self, mock_get_db):
        """Verify alert can be saved with empty reason string."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        alert = Alert(
            alert_id=4,
            student_id="S004",
            alert_type="test",
            reason="",
            created_at=datetime.now(),
            resolved=0
        )

        repo = AlertRepository()
        repo.save(alert)

        # Verify the alert was saved with empty reason
        call_args = mock_cursor.execute.call_args
        assert call_args[0][1][2] == ""


class TestAlertRepositoryListActive:
    """Test suite for retrieving active alerts."""

    @patch('Student_Wellbeing_App.core.repositories.AlertRepository.get_db_connection')
    def test_list_active_returns_unresolved_alerts(self, mock_get_db):
        """Verify list_active returns only unresolved alerts."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock the database response with unresolved alerts
        mock_cursor.fetchall.return_value = [
            (1, "S001", "low_attendance", "Missed sessions",
             datetime(2025, 1, 15, 10, 30, 0), 0),
            (2, "S002", "low_wellbeing", "Declining scores",
             datetime(2025, 1, 15, 11, 0, 0), 0),
        ]

        repo = AlertRepository()
        alerts = repo.list_active()

        # Verify the query
        assert mock_cursor.execute.called
        call_args = mock_cursor.execute.call_args
        assert "SELECT alert_id,student_id,alert_type,reason,created_at,resolved FROM alert WHERE resolved=false" in call_args[
            0][0]

        # Verify alerts are returned
        assert len(alerts) == 2
        assert isinstance(alerts[0], Alert)
        assert alerts[0].student_id == "S001"
        assert alerts[1].student_id == "S002"

    @patch('Student_Wellbeing_App.core.repositories.AlertRepository.get_db_connection')
    def test_list_active_returns_empty_when_no_alerts(self, mock_get_db):
        """Verify list_active returns empty list when no active alerts."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        repo = AlertRepository()
        alerts = repo.list_active()

        assert alerts == []
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('Student_Wellbeing_App.core.repositories.AlertRepository.get_db_connection')
    def test_list_active_alert_object_creation(self, mock_get_db):
        """Verify Alert objects are properly created from database rows."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        now = datetime(2025, 2, 1, 14, 30, 0)
        mock_cursor.fetchall.return_value = [
            (5, "S005", "low_performance", "Grade C on exam", now, 0),
        ]

        repo = AlertRepository()
        alerts = repo.list_active()

        assert len(alerts) == 1
        alert = alerts[0]
        assert alert.alert_id == 5
        assert alert.student_id == "S005"
        assert alert.alert_type == "low_performance"
        assert alert.reason == "Grade C on exam"
        assert alert.created_at == now
        assert alert.resolved == 0

    @patch('Student_Wellbeing_App.core.repositories.AlertRepository.get_db_connection')
    def test_list_active_multiple_alerts_same_student(self, mock_get_db):
        """Verify multiple alerts for same student are all returned."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            (6, "S006", "low_attendance", "Reason 1", datetime.now(), 0),
            (7, "S006", "low_wellbeing", "Reason 2", datetime.now(), 0),
            (8, "S006", "low_performance", "Reason 3", datetime.now(), 0),
        ]

        repo = AlertRepository()
        alerts = repo.list_active()

        assert len(alerts) == 3
        assert all(alert.student_id == "S006" for alert in alerts)


class TestAlertRepositoryResolve:
    """Test suite for resolving alerts."""

    @patch('Student_Wellbeing_App.core.repositories.AlertRepository.get_db_connection')
    def test_resolve_alert_by_id(self, mock_get_db):
        """Verify alert is resolved by ID."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        repo = AlertRepository()
        repo.resolve(1)

        # Verify the update query
        assert mock_cursor.execute.called
        call_args = mock_cursor.execute.call_args
        assert "UPDATE alert SET resolved=true WHERE alert_id=%s" in call_args[0][0]
        assert call_args[0][1] == (1,)

    @patch('Student_Wellbeing_App.core.repositories.AlertRepository.get_db_connection')
    def test_resolve_multiple_different_alerts(self, mock_get_db):
        """Verify different alerts can be resolved."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        repo = AlertRepository()

        # Resolve different alerts
        for alert_id in [1, 5, 10, 99]:
            repo.resolve(alert_id)

        # Verify execute was called for each
        assert mock_cursor.execute.call_count == 4

    @patch('Student_Wellbeing_App.core.repositories.AlertRepository.get_db_connection')
    def test_resolve_alert_closes_connection(self, mock_get_db):
        """Verify connection is closed after resolving."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        repo = AlertRepository()
        repo.resolve(1)

        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('Student_Wellbeing_App.core.repositories.AlertRepository.get_db_connection')
    def test_resolve_nonexistent_alert(self, mock_get_db):
        """Verify resolving non-existent alert doesn't error."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        repo = AlertRepository()
        # Should not raise error even if alert doesn't exist
        repo.resolve(999)

        assert mock_cursor.execute.called
        mock_cursor.close.assert_called_once()


class TestAlertRepositoryIntegration:
    """Integration tests for AlertRepository workflows."""

    @patch('Student_Wellbeing_App.core.repositories.AlertRepository.get_db_connection')
    def test_save_and_list_workflow(self, mock_get_db):
        """Verify save followed by list_active workflow."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        repo = AlertRepository()

        # Save an alert
        alert = Alert(
            alert_id=9,
            student_id="S009",
            alert_type="low_attendance",
            reason="Test",
            created_at=datetime.now(),
            resolved=0
        )
        repo.save(alert)

        # List active alerts
        mock_cursor.fetchall.return_value = [
            (9, "S009", "low_attendance", "Test", datetime.now(), 0),
        ]
        alerts = repo.list_active()

        assert len(alerts) == 1
        assert alerts[0].student_id == "S009"

    @patch('Student_Wellbeing_App.core.repositories.AlertRepository.get_db_connection')
    def test_save_resolve_workflow(self, mock_get_db):
        """Verify save followed by resolve workflow."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        repo = AlertRepository()

        # Save alert
        alert = Alert(
            alert_id=10,
            student_id="S010",
            alert_type="low_wellbeing",
            reason="Test",
            created_at=datetime.now(),
            resolved=0
        )
        repo.save(alert)

        # Resolve alert
        repo.resolve(10)

        # Verify both operations executed
        assert mock_cursor.execute.call_count == 2

    @patch('Student_Wellbeing_App.core.repositories.AlertRepository.get_db_connection')
    def test_multiple_operations_connection_management(self, mock_get_db):
        """Verify connection management across multiple operations."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        repo = AlertRepository()

        # Perform multiple operations
        alert = Alert(1, "S001", "test", "reason", datetime.now(), 0)
        repo.save(alert)
        repo.list_active()
        repo.resolve(1)

        # Verify get_db_connection was called 3 times (once per operation)
        assert mock_get_db.call_count == 3
        # Verify close was called for each connection
        assert mock_cursor.close.call_count == 3
        assert mock_conn.close.call_count == 3


class TestAlertRepositoryErrorHandling:
    """Test suite for error handling in AlertRepository."""

    @patch('Student_Wellbeing_App.core.repositories.AlertRepository.get_db_connection')
    def test_save_handles_database_error(self, mock_get_db):
        """Verify save handles database errors gracefully."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")

        repo = AlertRepository()
        alert = Alert(1, "S001", "test", "reason", datetime.now(), 0)

        with pytest.raises(Exception):
            repo.save(alert)

    @patch('Student_Wellbeing_App.core.repositories.AlertRepository.get_db_connection')
    def test_list_active_handles_database_error(self, mock_get_db):
        """Verify list_active handles database errors."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")

        repo = AlertRepository()

        with pytest.raises(Exception):
            repo.list_active()

    @patch('Student_Wellbeing_App.core.repositories.AlertRepository.get_db_connection')
    def test_resolve_handles_database_error(self, mock_get_db):
        """Verify resolve handles database errors."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")

        repo = AlertRepository()

        with pytest.raises(Exception):
            repo.resolve(1)


class TestAlertRepositoryDataValidation:
    """Test suite for data validation in AlertRepository."""

    @patch('Student_Wellbeing_App.core.repositories.AlertRepository.get_db_connection')
    def test_save_preserves_alert_data_integrity(self, mock_get_db):
        """Verify saved alert data maintains integrity."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        timestamp = datetime(2025, 3, 15, 9, 45, 30, 123456)
        alert = Alert(
            alert_id=11,
            student_id="S011",
            alert_type="low_performance",
            reason="Complex reason with special chars: !@#$%",
            created_at=timestamp,
            resolved=1
        )

        repo = AlertRepository()
        repo.save(alert)

        # Verify data is passed correctly
        call_args = mock_cursor.execute.call_args
        saved_data = call_args[0][1]
        assert saved_data[0] == "S011"
        assert saved_data[1] == "low_performance"
        assert saved_data[2] == "Complex reason with special chars: !@#$%"
        assert saved_data[3] == timestamp
        assert saved_data[4] == 1

    @patch('Student_Wellbeing_App.core.repositories.AlertRepository.get_db_connection')
    def test_list_active_returns_correct_alert_types(self, mock_get_db):
        """Verify list_active returns alerts with correct types."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            (1, "S001", "low_attendance", "Reason 1", datetime.now(), 0),
            (2, "S002", "low_wellbeing", "Reason 2", datetime.now(), 0),
            (3, "S003", "low_performance", "Reason 3", datetime.now(), 0),
        ]

        repo = AlertRepository()
        alerts = repo.list_active()

        alert_types = [alert.alert_type for alert in alerts]
        assert "low_attendance" in alert_types
        assert "low_wellbeing" in alert_types
        assert "low_performance" in alert_types
