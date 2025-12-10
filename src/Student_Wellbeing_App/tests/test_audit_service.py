from unittest.mock import MagicMock

from src.Student_Wellbeing_App.core.services.AuditService import AuditService


def test_log_uses_system_when_user_id_blank():
    repo = MagicMock()
    service = AuditService()
    service.repo = repo

    service.log("", "ACTION", "details")
    repo.log_action.assert_called_once_with("SYSTEM", "ACTION", "details")


def test_log_uses_given_user_id():
    repo = MagicMock()
    service = AuditService()
    service.repo = repo

    service.log("EMP0001", "ACTION", "details")
    repo.log_action.assert_called_once_with("EMP0001", "ACTION", "details")


def test_get_logs_passes_through_to_repo():
    repo = MagicMock()
    repo.get_recent_logs.return_value = ["log1"]
    service = AuditService()
    service.repo = repo

    logs = service.get_logs()
    assert logs == ["log1"]
    repo.get_recent_logs.assert_called_once()
