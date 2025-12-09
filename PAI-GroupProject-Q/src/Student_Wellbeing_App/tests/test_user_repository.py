"""
Tests for UserRepository class.
Tests user persistence, retrieval, ID generation, and authentication.
"""

import pytest
import hashlib
from unittest.mock import Mock, patch

from src.Student_Wellbeing_App.core.models.User import User
from src.Student_Wellbeing_App.core.models.UserRole import UserRole
from src.Student_Wellbeing_App.core.repositories.UserRepository import UserRepository


class TestUserRepository:
    """Test suite for UserRepository database operations."""

    @pytest.fixture
    def mock_db_connection(self):
        """Fixture to mock the database connection and cursor."""
        with patch('src.Student_Wellbeing_App.core.repositories.UserRepository.get_db_connection') as mock_conn_func:
            mock_conn = Mock()
            mock_cursor = Mock()
            
            mock_conn_func.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            
            yield mock_conn_func, mock_conn, mock_cursor

    def test_init_establishes_connection(self, mock_db_connection):
        """Verify repository initializes with a database connection."""
        mock_conn_func, _, _ = mock_db_connection
        
        repo = UserRepository()
        
        assert repo._conn is not None
        assert mock_conn_func.called

    def test_next_emp_id_initial(self, mock_db_connection):
        """Verify the first generated ID is EMP0001 if no users exist."""
        _, _, mock_cursor = mock_db_connection
        
        # Mock fetchone to return None (no existing IDs)
        mock_cursor.fetchone.return_value = None
        
        repo = UserRepository()
        # Accessing private method for direct testing
        next_id = repo._next_emp_id(mock_cursor)
        
        assert next_id == "EMP0001"
        assert "SELECT user_id" in mock_cursor.execute.call_args[0][0]

    def test_next_emp_id_increment(self, mock_db_connection):
        """Verify ID increments correctly (e.g., EMP0012 -> EMP0013)."""
        _, _, mock_cursor = mock_db_connection
        
        # Mock fetchone to return the last ID
        mock_cursor.fetchone.return_value = ("EMP0012",)
        
        repo = UserRepository()
        next_id = repo._next_emp_id(mock_cursor)
        
        assert next_id == "EMP0013"

    def test_create_user(self, mock_db_connection):
        """Verify creating a user generates ID, inserts record, and commits."""
        _, mock_conn, mock_cursor = mock_db_connection
        
        # Mock ID generation query to return a previous ID
        mock_cursor.fetchone.return_value = ("EMP0009",)
        
        repo = UserRepository()
        
        # Create a dummy user object with a valid role (changed TEACHER to COURSE_DIRECTOR)
        user_input = User(
            user_id="", # Will be ignored/overwritten
            first_name="John",
            lastname="Doe",
            password_hash="hashed_secret",
            role=UserRole.COURSE_DIRECTOR
        )
        
        new_id = repo.create(user_input)
        
        assert new_id == "EMP0010"
        
        # Verify Insert execution
        insert_calls = [
            call for call in mock_cursor.execute.call_args_list 
            if "INSERT INTO user" in call[0][0]
        ]
        assert len(insert_calls) == 1
        
        sql, params = insert_calls[0][0]
        assert params[0] == "EMP0010"
        assert params[1] == "John"
        assert params[2] == "Doe"
        assert params[3] == "hashed_secret"
        assert params[4] == "COURSE_DIRECTOR" # Role name string
        
        mock_conn.commit.assert_called_once()

    def test_has_admin_true(self, mock_db_connection):
        """Verify has_admin returns True when count > 0."""
        _, _, mock_cursor = mock_db_connection
        
        # Mock count result (tuple)
        mock_cursor.fetchone.return_value = (1,)
        
        repo = UserRepository()
        result = repo.has_admin()
        
        assert result is True
        mock_cursor.execute.assert_called_with(
            "SELECT COUNT(*) FROM user WHERE role = ? LIMIT 1;", 
            ("ADMIN",)
        )

    def test_has_admin_false(self, mock_db_connection):
        """Verify has_admin returns False when query returns None."""
        _, _, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = None
        
        repo = UserRepository()
        result = repo.has_admin()
        
        assert result is False

    def test_get_by_id_found(self, mock_db_connection):
        """Verify get_by_id returns a correctly mapped User object."""
        _, _, mock_cursor = mock_db_connection
        
        # Mock DB row response
        mock_row = {
            "user_id": "EMP0050",
            "first_name": "Alice",
            "lastname": "Smith",
            "password_hash": "hash123",
            "role": "ADMIN"
        }
        mock_cursor.fetchone.return_value = mock_row
        
        repo = UserRepository()
        user = repo.get_by_id("EMP0050")
        
        assert user is not None
        assert isinstance(user, User)
        assert user.user_id == "EMP0050"
        assert user.first_name == "Alice"
        assert user.role == UserRole.ADMIN

    def test_get_by_id_not_found(self, mock_db_connection):
        """Verify get_by_id returns None if ID doesn't exist."""
        _, _, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = None
        
        repo = UserRepository()
        user = repo.get_by_id("NONEXISTENT")
        
        assert user is None

    def test_get_all(self, mock_db_connection):
        """Verify get_all returns a list of User objects."""
        _, _, mock_cursor = mock_db_connection
        
        # Using valid roles: STUDENT and COURSE_DIRECTOR
        mock_rows = [
            {
                "user_id": "EMP1", 
                "first_name": "A", 
                "lastname": "B", 
                "password_hash": "h", 
                "role": "STUDENT"
            },
            {
                "user_id": "EMP2", 
                "first_name": "C", 
                "lastname": "D", 
                "password_hash": "h", 
                "role": "COURSE_DIRECTOR"
            }
        ]
        mock_cursor.fetchall.return_value = mock_rows
        
        repo = UserRepository()
        users = repo.get_all()
        
        assert len(users) == 2
        assert users[0].user_id == "EMP1"
        assert users[0].role == UserRole.STUDENT
        assert users[1].user_id == "EMP2"
        assert users[1].role == UserRole.COURSE_DIRECTOR

    def test_get_by_role(self, mock_db_connection):
        """Verify get_by_role filters correctly and returns users."""
        _, _, mock_cursor = mock_db_connection
        
        mock_rows = [{
            "user_id": "EMP1", 
            "first_name": "A", 
            "lastname": "B", 
            "password_hash": "h", 
            "role": "STUDENT"
        }]
        mock_cursor.fetchall.return_value = mock_rows
        
        repo = UserRepository()
        users = repo.get_by_role(UserRole.STUDENT)
        
        assert len(users) == 1
        assert users[0].role == UserRole.STUDENT
        
        # Verify SQL used role name
        call_args = mock_cursor.execute.call_args
        assert "WHERE role = ?" in call_args[0][0]
        assert call_args[0][1] == ("STUDENT",)

    def test_authenticate_success(self, mock_db_connection):
        """Verify authentication succeeds with correct ID and password."""
        _, mock_conn, mock_cursor = mock_db_connection
        
        password = "securePassword123"
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        
        # Using valid role: COURSE_DIRECTOR
        mock_row = ("EMP100", "John", "Doe", hashed_pw, "COURSE_DIRECTOR")
        mock_cursor.fetchone.return_value = mock_row
        
        repo = UserRepository()
        user = repo.authenticate_by_id("EMP100", password)
        
        assert user is not None
        assert user.user_id == "EMP100"
        assert user.role == UserRole.COURSE_DIRECTOR
        
        # Verify inputs
        assert mock_cursor.execute.called
        assert mock_cursor.execute.call_args[0][1] == ("EMP100",)

    def test_authenticate_wrong_password(self, mock_db_connection):
        """Verify authentication fails with incorrect password."""
        _, _, mock_cursor = mock_db_connection
        
        real_password = "correctPassword"
        stored_hash = hashlib.sha256(real_password.encode()).hexdigest()
        
        # Using valid role
        mock_row = ("EMP100", "John", "Doe", stored_hash, "COURSE_DIRECTOR")
        mock_cursor.fetchone.return_value = mock_row
        
        repo = UserRepository()
        # Pass wrong password
        user = repo.authenticate_by_id("EMP100", "WRONG_PASSWORD")
        
        assert user is None

    def test_authenticate_user_not_found(self, mock_db_connection):
        """Verify authentication returns None if user ID doesn't exist."""
        _, _, mock_cursor = mock_db_connection
        
        mock_cursor.fetchone.return_value = None
        
        repo = UserRepository()
        user = repo.authenticate_by_id("NONEXISTENT", "anyPassword")
        
        assert user is None
