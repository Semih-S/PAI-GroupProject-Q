from unittest.mock import MagicMock

from src.Student_Wellbeing_App.core.services.AuthenticationService import (
    AuthenticationService,
    AuthResult,
)


def test_authenticate_user_delegates_to_user_repo():
    user_repo = MagicMock()
    user_repo.authenticate_by_id.return_value = "USER"

    service = AuthenticationService(user_repo=user_repo, student_repo=MagicMock())
    result = service.authenticate_user("EMP0001", "pw")

    assert result == "USER"
    user_repo.authenticate_by_id.assert_called_once_with("EMP0001", "pw")


def test_authenticate_student_delegates_to_student_repo():
    student_repo = MagicMock()
    student_repo.authenticate_by_id.return_value = "STUDENT"

    service = AuthenticationService(user_repo=MagicMock(), student_repo=student_repo)
    result = service.authenticate_student("STU0001", "pw")

    assert result == "STUDENT"
    student_repo.authenticate_by_id.assert_called_once_with("STU0001", "pw")


def test_authenticate_any_emp_prefix_returns_user_authresult():
    user_repo = MagicMock()
    student_repo = MagicMock()
    fake_user = object()
    user_repo.authenticate_by_id.return_value = fake_user

    service = AuthenticationService(user_repo=user_repo, student_repo=student_repo)
    result = service.authenticate_any("emp0001", "pw")

    assert isinstance(result, AuthResult)
    assert result.kind == "user"
    assert result.principal is fake_user


def test_authenticate_any_st_prefix_returns_student_authresult():
    user_repo = MagicMock()
    student_repo = MagicMock()
    fake_student = object()
    student_repo.authenticate_by_id.return_value = fake_student

    service = AuthenticationService(user_repo=user_repo, student_repo=student_repo)
    result = service.authenticate_any("stu0001", "pw")

    assert result.kind == "student"
    assert result.principal is fake_student


def test_authenticate_any_unknown_prefix_returns_none():
    service = AuthenticationService(user_repo=MagicMock(), student_repo=MagicMock())
    assert service.authenticate_any("ABC123", "pw") is None
