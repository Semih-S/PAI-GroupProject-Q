"""
Tests for WellbeingRecord model class.
Tests dataclass instantiation, field validation, and wellbeing metrics.
"""

import pytest
from datetime import date

from src.Student_Wellbeing_App.core.models.WellbeingRecord import WellbeingRecord


class TestWellbeingRecordInstantiation:
    """Test suite for WellbeingRecord model instantiation."""

    def test_wellbeing_record_instantiation_with_all_fields(self):
        """Verify WellbeingRecord can be created with all required fields."""
        record = WellbeingRecord(
            record_id=1,
            student_id=1001,
            week_start=date(2025, 1, 6),
            stress_level=3,
            sleep_hours=7.5,
            source_type="survey",
        )

        assert record.record_id == 1
        assert record.student_id == 1001
        assert record.week_start == date(2025, 1, 6)
        assert record.stress_level == 3
        assert record.sleep_hours == 7.5
        assert record.source_type == "survey"

    def test_wellbeing_record_instantiation_without_source_type(self):
        """Verify WellbeingRecord defaults source_type to 'survey'."""
        record = WellbeingRecord(
            record_id=2,
            student_id=1002,
            week_start=date(2025, 1, 13),
            stress_level=2,
            sleep_hours=8.0,
        )

        assert record.source_type == "survey"

    def test_wellbeing_record_instantiation_with_explicit_empty_source_type(self):
        """Verify WellbeingRecord accepts explicit source_type override."""
        record = WellbeingRecord(
            record_id=3,
            student_id=1003,
            week_start=date(2025, 1, 20),
            stress_level=4,
            sleep_hours=6.5,
            source_type="app",
        )

        assert record.source_type == "app"


class TestWellbeingRecordFieldAccess:
    """Test suite for accessing and modifying WellbeingRecord fields."""

    def test_wellbeing_record_field_access(self):
        """Verify all WellbeingRecord fields are accessible."""
        record = WellbeingRecord(
            record_id=4,
            student_id=1004,
            week_start=date(2025, 1, 27),
            stress_level=2,
            sleep_hours=7.0,
            source_type="survey",
        )

        assert record.record_id is not None
        assert record.student_id is not None
        assert record.week_start is not None
        assert record.stress_level is not None
        assert record.sleep_hours is not None
        assert record.source_type is not None

    def test_wellbeing_record_field_mutation_stress_level(self):
        """Verify stress_level field can be modified."""
        record = WellbeingRecord(
            record_id=5,
            student_id=1005,
            week_start=date(2025, 2, 3),
            stress_level=3,
            sleep_hours=7.5,
        )

        record.stress_level = 5
        assert record.stress_level == 5

    def test_wellbeing_record_field_mutation_sleep_hours(self):
        """Verify sleep_hours field can be modified."""
        record = WellbeingRecord(
            record_id=6,
            student_id=1006,
            week_start=date(2025, 2, 10),
            stress_level=2,
            sleep_hours=6.0,
        )

        record.sleep_hours = 8.5
        assert record.sleep_hours == 8.5

    def test_wellbeing_record_field_mutation_source_type(self):
        """Verify source_type field can be modified."""
        record = WellbeingRecord(
            record_id=7,
            student_id=1007,
            week_start=date(2025, 2, 17),
            stress_level=3,
            sleep_hours=7.0,
            source_type="survey",
        )

        record.source_type = "wearable"
        assert record.source_type == "wearable"


class TestWellbeingRecordEquality:
    """Test suite for WellbeingRecord equality and comparison."""

    def test_wellbeing_record_equality_identical_records(self):
        """Verify two WellbeingRecord instances with same data are equal."""
        week_start = date(2025, 2, 24)
        record1 = WellbeingRecord(
            record_id=8,
            student_id=1008,
            week_start=week_start,
            stress_level=3,
            sleep_hours=7.5,
            source_type="survey",
        )
        record2 = WellbeingRecord(
            record_id=8,
            student_id=1008,
            week_start=week_start,
            stress_level=3,
            sleep_hours=7.5,
            source_type="survey",
        )

        assert record1 == record2

    def test_wellbeing_record_inequality_different_record_ids(self):
        """Verify records with different IDs are not equal."""
        week_start = date(2025, 3, 3)
        record1 = WellbeingRecord(
            record_id=9,
            student_id=1009,
            week_start=week_start,
            stress_level=2,
            sleep_hours=8.0,
        )
        record2 = WellbeingRecord(
            record_id=10,
            student_id=1009,
            week_start=week_start,
            stress_level=2,
            sleep_hours=8.0,
        )

        assert record1 != record2

    def test_wellbeing_record_inequality_different_stress_levels(self):
        """Verify records with different stress levels are not equal."""
        week_start = date(2025, 3, 10)
        record1 = WellbeingRecord(
            record_id=11,
            student_id=1010,
            week_start=week_start,
            stress_level=2,
            sleep_hours=7.0,
        )
        record2 = WellbeingRecord(
            record_id=11,
            student_id=1010,
            week_start=week_start,
            stress_level=4,
            sleep_hours=7.0,
        )

        assert record1 != record2

    def test_wellbeing_record_inequality_different_sleep_hours(self):
        """Verify records with different sleep hours are not equal."""
        week_start = date(2025, 3, 17)
        record1 = WellbeingRecord(
            record_id=12,
            student_id=1011,
            week_start=week_start,
            stress_level=3,
            sleep_hours=6.0,
        )
        record2 = WellbeingRecord(
            record_id=12,
            student_id=1011,
            week_start=week_start,
            stress_level=3,
            sleep_hours=8.0,
        )

        assert record1 != record2


class TestWellbeingRecordStressLevel:
    """Test suite for stress_level field (1-5 scale)."""

    def test_wellbeing_record_stress_level_minimum(self):
        """Verify stress_level can be set to 1 (minimum)."""
        record = WellbeingRecord(
            record_id=13,
            student_id=1012,
            week_start=date(2025, 3, 24),
            stress_level=1,
            sleep_hours=9.0,
        )

        assert record.stress_level == 1

    def test_wellbeing_record_stress_level_maximum(self):
        """Verify stress_level can be set to 5 (maximum)."""
        record = WellbeingRecord(
            record_id=14,
            student_id=1013,
            week_start=date(2025, 3, 31),
            stress_level=5,
            sleep_hours=5.0,
        )

        assert record.stress_level == 5

    def test_wellbeing_record_stress_level_mid_range(self):
        """Verify stress_level can be set to mid-range values."""
        for level in [1, 2, 3, 4, 5]:
            record = WellbeingRecord(
                record_id=15,
                student_id=1014,
                week_start=date(2025, 4, 7),
                stress_level=level,
                sleep_hours=7.0,
            )
            assert record.stress_level == level

    def test_wellbeing_record_stress_level_zero(self):
        """Verify stress_level can be set to 0 (edge case)."""
        record = WellbeingRecord(
            record_id=16,
            student_id=1015,
            week_start=date(2025, 4, 14),
            stress_level=0,
            sleep_hours=7.0,
        )

        assert record.stress_level == 0

    def test_wellbeing_record_stress_level_above_maximum(self):
        """Verify stress_level can accept values above 5."""
        record = WellbeingRecord(
            record_id=17,
            student_id=1016,
            week_start=date(2025, 4, 21),
            stress_level=10,
            sleep_hours=4.0,
        )

        assert record.stress_level == 10


class TestWellbeingRecordSleepHours:
    """Test suite for sleep_hours field handling."""

    def test_wellbeing_record_sleep_hours_integer(self):
        """Verify sleep_hours accepts integer values."""
        record = WellbeingRecord(
            record_id=18,
            student_id=1017,
            week_start=date(2025, 4, 28),
            stress_level=2,
            sleep_hours=8,
        )

        assert record.sleep_hours == 8

    def test_wellbeing_record_sleep_hours_float(self):
        """Verify sleep_hours accepts float values."""
        record = WellbeingRecord(
            record_id=19,
            student_id=1018,
            week_start=date(2025, 5, 5),
            stress_level=3,
            sleep_hours=7.5,
        )

        assert record.sleep_hours == 7.5

    def test_wellbeing_record_sleep_hours_precise_decimal(self):
        """Verify sleep_hours accepts precise decimal values."""
        record = WellbeingRecord(
            record_id=20,
            student_id=1019,
            week_start=date(2025, 5, 12),
            stress_level=2,
            sleep_hours=6.75,
        )

        assert record.sleep_hours == 6.75

    def test_wellbeing_record_sleep_hours_zero(self):
        """Verify sleep_hours can be set to 0."""
        record = WellbeingRecord(
            record_id=21,
            student_id=1020,
            week_start=date(2025, 5, 19),
            stress_level=5,
            sleep_hours=0.0,
        )

        assert record.sleep_hours == 0.0

    def test_wellbeing_record_sleep_hours_high_value(self):
        """Verify sleep_hours accepts high values."""
        record = WellbeingRecord(
            record_id=22,
            student_id=1021,
            week_start=date(2025, 5, 26),
            stress_level=1,
            sleep_hours=15.0,
        )

        assert record.sleep_hours == 15.0


class TestWellbeingRecordSourceType:
    """Test suite for source_type field."""

    def test_wellbeing_record_source_type_survey(self):
        """Verify source_type 'survey' is accepted."""
        record = WellbeingRecord(
            record_id=23,
            student_id=1022,
            week_start=date(2025, 6, 2),
            stress_level=3,
            sleep_hours=7.0,
            source_type="survey",
        )

        assert record.source_type == "survey"

    def test_wellbeing_record_source_type_app(self):
        """Verify source_type 'app' is accepted."""
        record = WellbeingRecord(
            record_id=24,
            student_id=1023,
            week_start=date(2025, 6, 9),
            stress_level=2,
            sleep_hours=8.0,
            source_type="app",
        )

        assert record.source_type == "app"

    def test_wellbeing_record_source_type_wearable(self):
        """Verify source_type 'wearable' is accepted."""
        record = WellbeingRecord(
            record_id=25,
            student_id=1024,
            week_start=date(2025, 6, 16),
            stress_level=3,
            sleep_hours=6.5,
            source_type="wearable",
        )

        assert record.source_type == "wearable"

    def test_wellbeing_record_source_type_custom(self):
        """Verify source_type accepts custom values."""
        record = WellbeingRecord(
            record_id=26,
            student_id=1025,
            week_start=date(2025, 6, 23),
            stress_level=4,
            sleep_hours=5.5,
            source_type="custom_source",
        )

        assert record.source_type == "custom_source"


class TestWellbeingRecordStudentId:
    """Test suite for student_id field."""

    def test_wellbeing_record_student_id_positive_integer(self):
        """Verify student_id accepts positive integers."""
        record = WellbeingRecord(
            record_id=27,
            student_id=9999,
            week_start=date(2025, 6, 30),
            stress_level=2,
            sleep_hours=7.5,
        )

        assert record.student_id == 9999

    def test_wellbeing_record_student_id_zero(self):
        """Verify student_id can be set to zero."""
        record = WellbeingRecord(
            record_id=28,
            student_id=0,
            week_start=date(2025, 7, 7),
            stress_level=3,
            sleep_hours=7.0,
        )

        assert record.student_id == 0

    def test_wellbeing_record_different_student_ids_distinguishable(self):
        """Verify records with different student IDs are distinguishable."""
        record1 = WellbeingRecord(
            record_id=29,
            student_id=1026,
            week_start=date(2025, 7, 14),
            stress_level=2,
            sleep_hours=8.0,
        )
        record2 = WellbeingRecord(
            record_id=30,
            student_id=1027,
            week_start=date(2025, 7, 21),
            stress_level=3,
            sleep_hours=7.0,
        )

        assert record1.student_id != record2.student_id


class TestWellbeingRecordWeekStart:
    """Test suite for week_start field."""

    def test_wellbeing_record_week_start_specific_date(self):
        """Verify week_start captures exact date."""
        start_date = date(2025, 7, 28)
        record = WellbeingRecord(
            record_id=31,
            student_id=1028,
            week_start=start_date,
            stress_level=3,
            sleep_hours=7.0,
        )

        assert record.week_start == start_date

    def test_wellbeing_record_week_start_monday_dates(self):
        """Verify week_start works with Monday dates."""
        mondays = [
            date(2025, 1, 6),
            date(2025, 1, 13),
            date(2025, 1, 20),
        ]

        for idx, monday in enumerate(mondays):
            record = WellbeingRecord(
                record_id=32 + idx,
                student_id=1029 + idx,
                week_start=monday,
                stress_level=3,
                sleep_hours=7.0,
            )
            assert record.week_start == monday

    def test_wellbeing_record_week_start_different_dates_distinguishable(self):
        """Verify records with different week_start dates are distinguishable."""
        record1 = WellbeingRecord(
            record_id=35,
            student_id=1032,
            week_start=date(2025, 8, 4),
            stress_level=2,
            sleep_hours=8.0,
        )
        record2 = WellbeingRecord(
            record_id=36,
            student_id=1033,
            week_start=date(2025, 8, 11),
            stress_level=2,
            sleep_hours=8.0,
        )

        assert record1.week_start != record2.week_start
        assert record1.week_start < record2.week_start


class TestWellbeingRecordDataIntegrity:
    """Test suite for data integrity and field types."""

    def test_record_id_is_integer(self):
        """Verify record_id field is an integer."""
        record = WellbeingRecord(
            record_id=37,
            student_id=1034,
            week_start=date(2025, 8, 18),
            stress_level=3,
            sleep_hours=7.0,
        )

        assert isinstance(record.record_id, int)

    def test_student_id_is_integer(self):
        """Verify student_id field is an integer."""
        record = WellbeingRecord(
            record_id=38,
            student_id=1035,
            week_start=date(2025, 8, 25),
            stress_level=3,
            sleep_hours=7.0,
        )

        assert isinstance(record.student_id, int)

    def test_week_start_is_date(self):
        """Verify week_start field is a date object."""
        record = WellbeingRecord(
            record_id=39,
            student_id=1036,
            week_start=date(2025, 9, 1),
            stress_level=3,
            sleep_hours=7.0,
        )

        assert isinstance(record.week_start, date)

    def test_stress_level_is_integer(self):
        """Verify stress_level field is an integer."""
        record = WellbeingRecord(
            record_id=40,
            student_id=1037,
            week_start=date(2025, 9, 8),
            stress_level=3,
            sleep_hours=7.0,
        )

        assert isinstance(record.stress_level, int)

    def test_sleep_hours_is_float(self):
        """Verify sleep_hours field is a float."""
        record = WellbeingRecord(
            record_id=41,
            student_id=1038,
            week_start=date(2025, 9, 15),
            stress_level=3,
            sleep_hours=7.5,
        )

        assert isinstance(record.sleep_hours, (int, float))

    def test_source_type_is_string(self):
        """Verify source_type field is a string."""
        record = WellbeingRecord(
            record_id=42,
            student_id=1039,
            week_start=date(2025, 9, 22),
            stress_level=3,
            sleep_hours=7.0,
            source_type="survey",
        )

        assert isinstance(record.source_type, str)


class TestWellbeingRecordRepr:
    """Test suite for WellbeingRecord string representation."""

    def test_wellbeing_record_has_repr(self):
        """Verify WellbeingRecord dataclass has a string representation."""
        record = WellbeingRecord(
            record_id=43,
            student_id=1040,
            week_start=date(2025, 9, 29),
            stress_level=3,
            sleep_hours=7.0,
        )

        repr_str = repr(record)
        assert "WellbeingRecord" in repr_str

    def test_wellbeing_record_repr_includes_key_fields(self):
        """Verify WellbeingRecord repr includes significant fields."""
        record = WellbeingRecord(
            record_id=44,
            student_id=1041,
            week_start=date(2025, 10, 6),
            stress_level=4,
            sleep_hours=6.0,
        )

        repr_str = repr(record)
        # Dataclass repr typically includes field names
        assert "record_id" in repr_str or "44" in repr_str

    def test_wellbeing_record_repr_distinct_for_different_records(self):
        """Verify repr differs for different records."""
        record1 = WellbeingRecord(
            record_id=45,
            student_id=1042,
            week_start=date(2025, 10, 13),
            stress_level=2,
            sleep_hours=8.5,
        )
        record2 = WellbeingRecord(
            record_id=46,
            student_id=1043,
            week_start=date(2025, 10, 20),
            stress_level=5,
            sleep_hours=5.5,
        )

        assert repr(record1) != repr(record2)

