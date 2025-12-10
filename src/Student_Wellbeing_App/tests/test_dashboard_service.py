from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock

from src.Student_Wellbeing_App.core.services.DashboardService import DashboardService
from src.Student_Wellbeing_App.core.models.AttendanceStatus import AttendanceStatus


def _att_record(status):
    return SimpleNamespace(
        attendance_id=1,
        student_id="STU0001",
        session_date=date(2025, 1, 1),
        session_id="CS101-1",
        status=status,
    )


def test_create_assessment_logs_and_saves():
    service = DashboardService()
    service.assessment_repo = MagicMock()
    service.audit = MagicMock()
    service.assessment_repo.save.return_value = 5

    new_id = service.create_assessment("CS101", "Midterm", date(2025, 5, 1), 20, performed_by="EMP0001")

    assert new_id == 5
    service.assessment_repo.save.assert_called_once()
    service.audit.log.assert_called_once()


def test_submit_grade_upserts_and_logs():
    service = DashboardService()
    service.submission_repo = MagicMock()
    service.audit = MagicMock()

    service.submit_grade("STU0001", 7, 88.0, performed_by="EMP0001")

    service.submission_repo.upsert_grade.assert_called_once_with("STU0001", 7, 88.0)
    service.audit.log.assert_called_once()


def test_update_grade_direct_updates_and_logs():
    service = DashboardService()
    service.submission_repo = MagicMock()
    service.audit = MagicMock()

    service.update_grade_direct(10, 91.5, performed_by="EMP0001")

    service.submission_repo.update_mark_by_id.assert_called_once_with(10, 91.5)
    service.audit.log.assert_called_once()


def test_delete_grade_entry_deletes_and_logs():
    service = DashboardService()
    service.submission_repo = MagicMock()
    service.audit = MagicMock()

    service.delete_grade_entry(10, performed_by="EMP0001")

    service.submission_repo.delete_by_id.assert_called_once_with(10)
    service.audit.log.assert_called_once()


def test_calculate_attendance_rate_handles_empty_records_as_100():
    service = DashboardService()
    service.attendance_repo = MagicMock()
    service.attendance_repo.get_by_student.return_value = []

    pct = service.calculate_attendance_rate("STU0001")
    assert pct == 100.0


def test_calculate_attendance_rate_computes_correctly():
    service = DashboardService()
    service.attendance_repo = MagicMock()
    service.attendance_repo.get_by_student.return_value = [
        _att_record(AttendanceStatus.PRESENT),
        _att_record(AttendanceStatus.ABSENT),
        _att_record(AttendanceStatus.PRESENT),
    ]
    pct = service.calculate_attendance_rate("STU0001")
    assert abs(pct - (2 / 3 * 100)) < 0.1
    


def test_get_module_stats_returns_zeroes_when_no_records():
    service = DashboardService()
    service.attendance_repo = MagicMock()
    service.attendance_repo.get_by_session.return_value = []

    stats = service.get_module_stats("CS101-1")
    assert stats["avg_attendance"] == 0.0
    assert stats["total_sessions"] == 0
    assert stats["absent_count"] == 0
