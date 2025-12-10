"""
Tests for AttendanceRecord model class.
Tests dataclass instantiation, field validation, and attendance record lifecycle.
"""

import pytest
from datetime import date

from src.Student_Wellbeing_App.core.models.AttendanceRecord import AttendanceRecord
from src.Student_Wellbeing_App.core.models.AttendanceStatus import AttendanceStatus


class TestAttendanceRecordInstantiation:
    """Test suite for AttendanceRecord model instantiation."""

    def test_attendance_record_instantiation_with_all_fields(self):
        """Verify AttendanceRecord can be created with all required fields."""
        record = AttendanceRecord(
            attendance_id=1,
            student_id="S001",
            session_date=date(2025, 1, 15),
            session_id="sess_001",
            status=AttendanceStatus.PRESENT,
        )

        assert record.attendance_id == 1
        assert record.student_id == "S001"
        assert record.session_date == date(2025, 1, 15)
        assert record.session_id == "sess_001"
        assert record.status == AttendanceStatus.PRESENT

    def test_attendance_record_with_absent_status(self):
        """Verify AttendanceRecord accepts ABSENT status."""
        record = AttendanceRecord(
            attendance_id=2,
            student_id="S002",
            session_date=date(2025, 1, 16),
            session_id="sess_002",
            status=AttendanceStatus.ABSENT,
        )

        assert record.status == AttendanceStatus.ABSENT

    def test_attendance_record_with_excused_status(self):
        """Verify AttendanceRecord accepts EXCUSED status."""
        record = AttendanceRecord(
            attendance_id=3,
            student_id="S003",
            session_date=date(2025, 1, 17),
            session_id="sess_003",
            status=AttendanceStatus.EXCUSED,
        )

        assert record.status == AttendanceStatus.EXCUSED


class TestAttendanceRecordFieldAccess:
    """Test suite for accessing and modifying AttendanceRecord fields."""

    def test_attendance_record_field_access(self):
        """Verify all AttendanceRecord fields are accessible."""
        record = AttendanceRecord(
            attendance_id=4,
            student_id="S004",
            session_date=date(2025, 1, 18),
            session_id="sess_004",
            status=AttendanceStatus.PRESENT,
        )

        # Access each field
        assert record.attendance_id is not None
        assert record.student_id is not None
        assert record.session_date is not None
        assert record.session_id is not None
        assert record.status is not None

    def test_attendance_record_field_mutation(self):
        """Verify AttendanceRecord fields can be modified after instantiation."""
        record = AttendanceRecord(
            attendance_id=5,
            student_id="S005",
            session_date=date(2025, 1, 19),
            session_id="sess_005",
            status=AttendanceStatus.PRESENT,
        )

        # Modify status field
        record.status = AttendanceStatus.ABSENT
        assert record.status == AttendanceStatus.ABSENT

        # Modify student_id field
        record.student_id = "S005_updated"
        assert record.student_id == "S005_updated"

    def test_attendance_record_equality(self):
        """Verify two AttendanceRecord instances with same data are equal."""
        date_val = date(2025, 1, 20)
        record1 = AttendanceRecord(
            attendance_id=6,
            student_id="S006",
            session_date=date_val,
            session_id="sess_006",
            status=AttendanceStatus.PRESENT,
        )
        record2 = AttendanceRecord(
            attendance_id=6,
            student_id="S006",
            session_date=date_val,
            session_id="sess_006",
            status=AttendanceStatus.PRESENT,
        )

        assert record1 == record2

    def test_attendance_record_inequality(self):
        """Verify two AttendanceRecord instances with different data are not equal."""
        record1 = AttendanceRecord(
            attendance_id=7,
            student_id="S007",
            session_date=date(2025, 1, 21),
            session_id="sess_007",
            status=AttendanceStatus.PRESENT,
        )
        record2 = AttendanceRecord(
            attendance_id=8,
            student_id="S008",
            session_date=date(2025, 1, 22),
            session_id="sess_008",
            status=AttendanceStatus.ABSENT,
        )

        assert record1 != record2


class TestAttendanceRecordStudentId:
    """Test suite for student ID handling in attendance records."""

    def test_attendance_record_numeric_student_id(self):
        """Verify AttendanceRecord accepts numeric string student IDs."""
        record = AttendanceRecord(
            attendance_id=9,
            student_id="123456",
            session_date=date(2025, 1, 23),
            session_id="sess_009",
            status=AttendanceStatus.PRESENT,
        )

        assert record.student_id == "123456"

    def test_attendance_record_alphanumeric_student_id(self):
        """Verify AttendanceRecord accepts alphanumeric student IDs."""
        record = AttendanceRecord(
            attendance_id=10,
            student_id="S2025001",
            session_date=date(2025, 1, 24),
            session_id="sess_010",
            status=AttendanceStatus.PRESENT,
        )

        assert record.student_id == "S2025001"

    def test_attendance_record_student_id_case_sensitive(self):
        """Verify AttendanceRecord treats student IDs as case-sensitive."""
        record1 = AttendanceRecord(
            attendance_id=11,
            student_id="S001",
            session_date=date(2025, 1, 25),
            session_id="sess_011",
            status=AttendanceStatus.PRESENT,
        )
        record2 = AttendanceRecord(
            attendance_id=12,
            student_id="s001",
            session_date=date(2025, 1, 26),
            session_id="sess_012",
            status=AttendanceStatus.PRESENT,
        )

        assert record1.student_id != record2.student_id


class TestAttendanceRecordSessionDate:
    """Test suite for session date handling."""

    def test_attendance_record_session_date_exact(self):
        """Verify AttendanceRecord captures exact session date."""
        session_date = date(2025, 1, 27)
        record = AttendanceRecord(
            attendance_id=13,
            student_id="S013",
            session_date=session_date,
            session_id="sess_013",
            status=AttendanceStatus.PRESENT,
        )

        assert record.session_date == session_date

    def test_attendance_record_session_date_different_dates(self):
        """Verify records with different session dates are distinguishable."""
        date1 = date(2025, 1, 28)
        date2 = date(2025, 1, 29)

        record1 = AttendanceRecord(
            attendance_id=14,
            student_id="S014",
            session_date=date1,
            session_id="sess_014",
            status=AttendanceStatus.PRESENT,
        )
        record2 = AttendanceRecord(
            attendance_id=15,
            student_id="S015",
            session_date=date2,
            session_id="sess_015",
            status=AttendanceStatus.PRESENT,
        )

        assert record1.session_date != record2.session_date
        assert record1.session_date < record2.session_date

    def test_attendance_record_session_date_ordering(self):
        """Verify session dates can be ordered chronologically."""
        dates = [
            date(2025, 1, 30),
            date(2025, 1, 28),
            date(2025, 1, 29),
        ]
        sorted_dates = sorted(dates)

        assert sorted_dates == [
            date(2025, 1, 28),
            date(2025, 1, 29),
            date(2025, 1, 30),
        ]


class TestAttendanceRecordSessionId:
    """Test suite for session ID handling."""

    def test_attendance_record_session_id_numeric(self):
        """Verify AttendanceRecord accepts numeric session IDs."""
        record = AttendanceRecord(
            attendance_id=16,
            student_id="S016",
            session_date=date(2025, 1, 31),
            session_id="001",
            status=AttendanceStatus.PRESENT,
        )

        assert record.session_id == "001"

    def test_attendance_record_session_id_alphanumeric(self):
        """Verify AttendanceRecord accepts alphanumeric session IDs."""
        record = AttendanceRecord(
            attendance_id=17,
            student_id="S017",
            session_date=date(2025, 2, 1),
            session_id="sess_2025_001",
            status=AttendanceStatus.PRESENT,
        )

        assert record.session_id == "sess_2025_001"

    def test_attendance_record_session_id_case_sensitive(self):
        """Verify session IDs are case-sensitive."""
        record1 = AttendanceRecord(
            attendance_id=18,
            student_id="S018",
            session_date=date(2025, 2, 2),
            session_id="SESS_001",
            status=AttendanceStatus.PRESENT,
        )
        record2 = AttendanceRecord(
            attendance_id=19,
            student_id="S019",
            session_date=date(2025, 2, 3),
            session_id="sess_001",
            status=AttendanceStatus.PRESENT,
        )

        assert record1.session_id != record2.session_id


class TestAttendanceRecordDataIntegrity:
    """Test suite for data integrity and field types."""

    def test_attendance_id_is_integer(self):
        """Verify attendance_id field is an integer."""
        record = AttendanceRecord(
            attendance_id=20,
            student_id="S020",
            session_date=date(2025, 2, 4),
            session_id="sess_020",
            status=AttendanceStatus.PRESENT,
        )

        assert isinstance(record.attendance_id, int)

    def test_student_id_is_string(self):
        """Verify student_id field is a string."""
        record = AttendanceRecord(
            attendance_id=21,
            student_id="S021",
            session_date=date(2025, 2, 5),
            session_id="sess_021",
            status=AttendanceStatus.PRESENT,
        )

        assert isinstance(record.student_id, str)

    def test_session_date_is_date(self):
        """Verify session_date field is a date object."""
        record = AttendanceRecord(
            attendance_id=22,
            student_id="S022",
            session_date=date(2025, 2, 6),
            session_id="sess_022",
            status=AttendanceStatus.PRESENT,
        )

        assert isinstance(record.session_date, date)

    def test_session_id_is_string(self):
        """Verify session_id field is a string."""
        record = AttendanceRecord(
            attendance_id=23,
            student_id="S023",
            session_date=date(2025, 2, 7),
            session_id="sess_023",
            status=AttendanceStatus.PRESENT,
        )

        assert isinstance(record.session_id, str)

    def test_status_is_attendance_status(self):
        """Verify status field is an AttendanceStatus enum."""
        record = AttendanceRecord(
            attendance_id=24,
            student_id="S024",
            session_date=date(2025, 2, 8),
            session_id="sess_024",
            status=AttendanceStatus.PRESENT,
        )

        assert isinstance(record.status, AttendanceStatus)


class TestAttendanceRecordStatusTransitions:
    """Test suite for status transitions in attendance records."""

    def test_attendance_record_change_present_to_absent(self):
        """Verify status can transition from PRESENT to ABSENT."""
        record = AttendanceRecord(
            attendance_id=25,
            student_id="S025",
            session_date=date(2025, 2, 9),
            session_id="sess_025",
            status=AttendanceStatus.PRESENT,
        )

        assert record.status == AttendanceStatus.PRESENT

        record.status = AttendanceStatus.ABSENT
        assert record.status == AttendanceStatus.ABSENT

    def test_attendance_record_change_absent_to_excused(self):
        """Verify status can transition from ABSENT to EXCUSED."""
        record = AttendanceRecord(
            attendance_id=26,
            student_id="S026",
            session_date=date(2025, 2, 10),
            session_id="sess_026",
            status=AttendanceStatus.ABSENT,
        )

        record.status = AttendanceStatus.EXCUSED
        assert record.status == AttendanceStatus.EXCUSED

    def test_attendance_record_change_excused_to_present(self):
        """Verify status can transition from EXCUSED to PRESENT."""
        record = AttendanceRecord(
            attendance_id=27,
            student_id="S027",
            session_date=date(2025, 2, 11),
            session_id="sess_027",
            status=AttendanceStatus.EXCUSED,
        )

        record.status = AttendanceStatus.PRESENT
        assert record.status == AttendanceStatus.PRESENT


class TestAttendanceRecordRepr:
    """Test suite for AttendanceRecord string representation."""

    def test_attendance_record_has_repr(self):
        """Verify AttendanceRecord dataclass has a string representation."""
        record = AttendanceRecord(
            attendance_id=28,
            student_id="S028",
            session_date=date(2025, 2, 12),
            session_id="sess_028",
            status=AttendanceStatus.PRESENT,
        )

        repr_str = repr(record)
        assert "AttendanceRecord" in repr_str
        assert "S028" in repr_str

    def test_attendance_record_repr_includes_key_fields(self):
        """Verify AttendanceRecord repr includes significant fields."""
        record = AttendanceRecord(
            attendance_id=29,
            student_id="S029",
            session_date=date(2025, 2, 13),
            session_id="sess_029",
            status=AttendanceStatus.ABSENT,
        )

        repr_str = repr(record)
        # Dataclass repr typically includes field names
        assert "attendance_id" in repr_str or "29" in repr_str


class TestAttendanceRecordComparison:
    """Test suite for comparing attendance records."""

    def test_attendance_record_same_student_different_dates(self):
        """Verify records for same student on different dates are different."""
        record1 = AttendanceRecord(
            attendance_id=30,
            student_id="S030",
            session_date=date(2025, 2, 14),
            session_id="sess_030",
            status=AttendanceStatus.PRESENT,
        )
        record2 = AttendanceRecord(
            attendance_id=31,
            student_id="S030",
            session_date=date(2025, 2, 15),
            session_id="sess_031",
            status=AttendanceStatus.PRESENT,
        )

        assert record1 != record2

    def test_attendance_record_same_date_different_students(self):
        """Verify records for different students on same date are different."""
        session_date = date(2025, 2, 16)
        record1 = AttendanceRecord(
            attendance_id=32,
            student_id="S032",
            session_date=session_date,
            session_id="sess_032",
            status=AttendanceStatus.PRESENT,
        )
        record2 = AttendanceRecord(
            attendance_id=33,
            student_id="S033",
            session_date=session_date,
            session_id="sess_032",
            status=AttendanceStatus.PRESENT,
        )

        assert record1 != record2

    def test_attendance_record_same_date_student_different_status(self):
        """Verify records with different statuses are different."""
        record1 = AttendanceRecord(
            attendance_id=34,
            student_id="S034",
            session_date=date(2025, 2, 17),
            session_id="sess_034",
            status=AttendanceStatus.PRESENT,
        )
        record2 = AttendanceRecord(
            attendance_id=35,
            student_id="S034",
            session_date=date(2025, 2, 17),
            session_id="sess_034",
            status=AttendanceStatus.ABSENT,
        )

        assert record1 != record2

