from datetime import date
from unittest.mock import MagicMock

from src.Student_Wellbeing_App.core.services.AttendanceService import AttendanceService
from src.Student_Wellbeing_App.core.models.AttendanceStatus import AttendanceStatus
from src.Student_Wellbeing_App.core.models.AttendanceRecord import AttendanceRecord


def _record(status):
    return AttendanceRecord(
        attendance_id=1,
        student_id="STU0001",
        session_date=date(2025, 1, 1),
        session_id="CS101-1",
        status=status,
    )


def test_record_attendance_upserts_and_logs():
    repo = MagicMock()
    audit = MagicMock()

    service = AttendanceService(repo=repo)
    service.audit = audit

    repo.upsert.return_value = 10

    new_id = service.record_attendance(
        "STU0001", date(2025, 1, 1), "CS101-1", AttendanceStatus.PRESENT, performed_by="EMP0001"
    )

    assert new_id == 10
    repo.upsert.assert_called_once()
    audit.log.assert_called_once()
    args, _ = audit.log.call_args
    assert args[0] == "EMP0001"
    assert args[1] == "UPSERT_ATTENDANCE"


def test_get_attendance_percentage_handles_no_records_as_100():
    repo = MagicMock()
    repo.get_by_student.return_value = []

    service = AttendanceService(repo=repo)

    pct = service.get_attendance_percentage("STU0001")
    assert pct == 100.0


def test_get_attendance_percentage_calculates_correctly():
    repo = MagicMock()
    repo.get_by_student.return_value = [
        _record(AttendanceStatus.PRESENT),
        _record(AttendanceStatus.ABSENT),
        _record(AttendanceStatus.PRESENT),
    ]

    service = AttendanceService(repo=repo)
    pct = service.get_attendance_percentage("STU0001")
    # 2 present out of 3 = 66.66...
    assert abs(pct - (2 / 3 * 100)) < 0.01
