"""
Tests for AuditRepository class.
Tests audit log persistence and retrieval operations.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, ANY

# Note: AuditLog model is not used by the repository anymore, so we don't import it.
from src.Student_Wellbeing_App.core.repositories.AuditRepository import AuditRepository


class TestAuditRepositoryLog:
    """Test suite for logging audit records to database."""

    @patch('src.Student_Wellbeing_App.core.repositories.AuditRepository.get_db_connection')
    def test_log_action_success(self, mock_get_db):
        """Verify log_action saves correct data to the database."""
        # Setup Mock
        mock_conn = Mock()
        # Mocking connection for __init__ (create table) and log_action
        mock_get_db.return_value = mock_conn

        repo = AuditRepository()
        
        # Test Data
        user_id = "U101"
        action = "CREATE"
        details = "Created new student record"

        # Execute
        repo.log_action(user_id, action, details)

        # Verify calls
        # We expect at least two calls to execute:
        # 1. CREATE TABLE (in __init__)
        # 2. INSERT INTO (in log_action)
        
        # Find the INSERT call
        insert_calls = [
            call for call in mock_conn.execute.call_args_list 
            if "INSERT INTO audit_log" in str(call)
        ]
        
        assert len(insert_calls) == 1
        args, _ = insert_calls[0]
        sql, params = args

        assert "user_id, action, details, timestamp" in sql
        assert params[0] == user_id
        assert params[1] == action
        assert params[2] == details
        # Verify timestamp was generated and is a datetime object
        assert isinstance(params[3], datetime)

    @patch('src.Student_Wellbeing_App.core.repositories.AuditRepository.get_db_connection')
    def test_log_action_closes_connection(self, mock_get_db):
        """Verify database connection closes after logging."""
        mock_conn = Mock()
        mock_get_db.return_value = mock_conn

        repo = AuditRepository()
        repo.log_action("U102", "UPDATE", "Test close")

        # Expect close called twice: once for __init__, once for log_action
        assert mock_conn.close.call_count == 2

    @patch('src.Student_Wellbeing_App.core.repositories.AuditRepository.get_db_connection')
    def test_log_action_with_special_chars(self, mock_get_db):
        """Verify logging handles special characters in details."""
        mock_conn = Mock()
        mock_get_db.return_value = mock_conn
        
        repo = AuditRepository()
        special_details = "Special: !@#$%^&*()"
        
        repo.log_action("U103", "TEST", special_details)
        
        # Check params of the last execute call
        call_args = mock_conn.execute.call_args
        params = call_args[0][1]
        assert params[2] == special_details


class TestAuditRepositoryRetrieval:
    """Test suite for retrieving audit logs."""

    @patch('src.Student_Wellbeing_App.core.repositories.AuditRepository.get_db_connection')
    def test_get_recent_logs_returns_rows(self, mock_get_db):
        """Verify get_recent_logs returns data from cursor."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock returned data
        expected_rows = [
            {"log_id": 2, "user_id": "U1", "action": "LOGIN", "details": "A", "timestamp": "2025-01-01"},
            {"log_id": 1, "user_id": "U1", "action": "LOGOUT", "details": "B", "timestamp": "2025-01-01"},
        ]
        mock_cursor.fetchall.return_value = expected_rows

        repo = AuditRepository()
        logs = repo.get_recent_logs(limit=10)

        # Verify assertions
        assert logs == expected_rows
        
        # Verify Query
        mock_cursor.execute.assert_called_with(
            "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?", 
            (10,)
        )
        mock_conn.close.assert_called()

    @patch('src.Student_Wellbeing_App.core.repositories.AuditRepository.get_db_connection')
    def test_get_recent_logs_default_limit(self, mock_get_db):
        """Verify get_recent_logs uses default limit of 50."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        repo = AuditRepository()
        repo.get_recent_logs() # No limit passed

        call_args = mock_cursor.execute.call_args
        assert call_args[0][1] == (50,)


class TestAuditRepositoryInitialization:
    """Test suite for Repository initialization logic."""

    @patch('src.Student_Wellbeing_App.core.repositories.AuditRepository.get_db_connection')
    def test_init_creates_table(self, mock_get_db):
        """Verify table creation logic runs on initialization."""
        mock_conn = Mock()
        mock_get_db.return_value = mock_conn

        _ = AuditRepository()

        # Check that CREATE TABLE SQL was executed
        # We look through all execute calls
        create_table_called = False
        for call in mock_conn.execute.call_args_list:
            sql = call[0][0]
            if "CREATE TABLE IF NOT EXISTS audit_log" in sql:
                create_table_called = True
                break
        
        assert create_table_called
        assert mock_conn.commit.called
        assert mock_conn.close.called
