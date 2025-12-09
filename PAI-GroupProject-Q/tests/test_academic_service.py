import types
from unittest.mock import MagicMock

from src.Student_Wellbeing_App.core.services.AcademicService import AcademicService
from src.Student_Wellbeing_App.core.models.AcademicSummary import AcademicSummary


def _make_submission(mark):
    return types.SimpleNamespace(mark=mark)


def _make_student(student_id="STU0001"):
    return types.SimpleNamespace(student_id=student_id)


def test_get_student_academic_profile_counts_low_marks_and_attendance():
    submission_service = MagicMock()
    attendance_service = MagicMock()

    submission_service.get_submissions_for_student.return_value = [
        _make_submission(80),
        _make_submission(40),  # low
        _make_submission(49),  # low
        _make_submission(None) # ignored
    ]
    attendance_service.get_attendance_percentage.return_value = 72.5

    service = AcademicService(
        submission_service=submission_service,
        attendance_service=attendance_service,
        student_service=MagicMock()
    )

    profile = service.get_student_academic_profile("STU0001")

    assert profile["total_submissions"] == 4
    assert profile["low_marks_count"] == 2
    assert profile["attendance_pct"] == 72.5
    assert len(profile["submissions"]) == 4
    submission_service.get_submissions_for_student.assert_called_once_with("STU0001")
    attendance_service.get_attendance_percentage.assert_called_once_with("STU0001")


def test_get_low_attendance_students_filters_below_threshold():
    attendance_service = MagicMock()
    students = [_make_student("STU0001"), _make_student("STU0002")]

    attendance_service.get_attendance_percentage.side_effect = [60.0, 85.0]

    service = AcademicService(
        submission_service=MagicMock(),
        attendance_service=attendance_service,
        student_service=MagicMock()
    )

    result = service.get_low_attendance_students(students, threshold=75.0)
    assert len(result) == 1
    student, pct = result[0]
    assert student.student_id == "STU0001"
    assert pct == 60.0


def test_get_low_mark_students_counts_low_submissions():
    submission_service = MagicMock()

    s1 = _make_student("STU0001")
    s2 = _make_student("STU0002")

    submission_service.get_submissions_for_student.side_effect = [
        [_make_submission(40), _make_submission(30)],  # 2 low
        [_make_submission(60)],                        # no low
    ]

    service = AcademicService(
        submission_service=submission_service,
        attendance_service=MagicMock(),
        student_service=MagicMock()
    )

    result = service.get_low_mark_students([s1, s2], threshold=50.0)
    assert len(result) == 1
    student, count = result[0]
    assert student.student_id == "STU0001"
    assert count == 2


def test_get_student_academic_summary_returns_none_if_student_missing():
    student_service = MagicMock()
    student_service.get_student_by_id.return_value = None

    service = AcademicService(
        submission_service=MagicMock(),
        attendance_service=MagicMock(),
        student_service=student_service
    )

    summary = service.get_student_academic_summary("STU9999")
    assert summary is None
    student_service.get_student_by_id.assert_called_once_with("STU9999")


def test_get_student_academic_summary_builds_academic_summary():
    student = _make_student("STU0001")
    student_service = MagicMock()
    student_service.get_student_by_id.return_value = student

    attendance_service = MagicMock()
    attendance_service.get_attendance_percentage.return_value = 90.0

    subs = [_make_submission(80), _make_submission(40)]
    submission_service = MagicMock()
    submission_service.get_submissions_for_student.return_value = subs

    service = AcademicService(
        submission_service=submission_service,
        attendance_service=attendance_service,
        student_service=student_service
    )

    summary = service.get_student_academic_summary("STU0001")
    assert isinstance(summary, AcademicSummary)
    assert summary.student == student
    assert summary.attendance_percentage == 90.0
    assert summary.submissions == subs
    assert len(summary.low_mark_submissions) == 1
