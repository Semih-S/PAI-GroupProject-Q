from datetime import datetime
from unittest.mock import MagicMock

from src.Student_Wellbeing_App.core.services.AlertService import AlertService
from src.Student_Wellbeing_App.core.models.AttendanceStatus import AttendanceStatus
from src.Student_Wellbeing_App.core.models.AlertType import AlertType
from src.Student_Wellbeing_App.core.models.Alert import Alert


def test_raise_alert_saves_and_logs():
    alert_repo = MagicMock()
    audit = MagicMock()
    attendance_repo = MagicMock()

    alert_repo.save.return_value = 42

    service = AlertService(alert_repo=alert_repo, attendance_repo=attendance_repo, audit_service=audit)
    service.audit = audit  # guard against ctor override

    new_id = service.raise_alert(
        student_id="STU0001",
        alert_type=AlertType.ATTENDANCE,
        reason="Test reason",
        created_at=datetime(2025, 1, 1)
    )

    assert new_id == 42
    alert_repo.save.assert_called_once()
    audit.log.assert_called_once()
    args, kwargs = audit.log.call_args
    assert args[0] == "SYSTEM"
    assert args[1] == "RAISE_ALERT"
    assert "STU0001" in args[2]


def _attendance_record(status):
    class R:
        def __init__(self, status):
            self.status = status
    return R(status)


def test_generate_multiple_absence_alerts_triggers_when_threshold_met():
    alert_repo = MagicMock()
    attendance_repo = MagicMock()
    audit = MagicMock()

    attendance_repo.get_by_student.return_value = [
        _attendance_record(AttendanceStatus.ABSENT),
        _attendance_record(AttendanceStatus.ABSENT),
        _attendance_record(AttendanceStatus.ABSENT),
    ]
    alert_repo.save.return_value = 99

    service = AlertService(alert_repo=alert_repo, attendance_repo=attendance_repo, audit_service=audit)
    service.audit = audit

    alert_id = service.generate_multiple_absence_alerts("STU0001", threshold=3)
    assert alert_id == 99
    alert_repo.save.assert_called_once()
    audit.log.assert_called_once()


def test_generate_multiple_absence_alerts_returns_none_if_below_threshold():
    service = AlertService(
        alert_repo=MagicMock(),
        attendance_repo=MagicMock(),
        audit_service=MagicMock()
    )
    service.attendance_repo.get_by_student.return_value = [
        _attendance_record(AttendanceStatus.PRESENT),
        _attendance_record(AttendanceStatus.ABSENT),
    ]

    result = service.generate_multiple_absence_alerts("STU0001", threshold=3)
    assert result is None
    service.alert_repo.save.assert_not_called()


def test_resolve_alert_marks_resolved_and_logs():
    alert_repo = MagicMock()
    audit = MagicMock()
    service = AlertService(alert_repo=alert_repo, attendance_repo=MagicMock(), audit_service=audit)
    service.audit = audit

    service.resolve_alert(123, performed_by="EMP0001")

    alert_repo.resolve.assert_called_once_with(123)
    audit.log.assert_called_once()
    args, _ = audit.log.call_args
    assert args[0] == "EMP0001"
    assert args[1] == "RESOLVE_ALERT"
    assert "123" in args[2]
