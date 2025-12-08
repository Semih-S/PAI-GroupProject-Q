"""
Tests for Alert model class.
Tests dataclass instantiation, field validation, and alert lifecycle.
"""

import pytest
from datetime import datetime

from src.Student_Wellbeing_App.core.models.Alert import Alert
from src.Student_Wellbeing_App.core.models.AlertType import AlertType

class TestAlertInstantiation:
    """Test suite for Alert model instantiation and field assignment."""

    def test_alert_instantiation_with_all_fields(self):
        """Verify Alert can be created with all required fields."""
        now = datetime.now()
        alert = Alert(
            alert_id=1,
            student_id="S001",
            alert_type=AlertType.ATTENDANCE,
            reason="Missing 3 consecutive sessions",
            created_at=now,
        )

        assert alert.alert_id == 1
        assert alert.student_id == "S001"
        assert alert.alert_type == "low_attendance"
        assert alert.reason == "Missing 3 consecutive sessions"
        assert alert.created_at == now
        assert alert.resolved is False  # Default value

    def test_alert_instantiation_with_resolved_flag(self):
        """Verify Alert resolved field can be set at instantiation."""
        now = datetime.now()
        alert = Alert(
            alert_id=2,
            student_id="S002",
            alert_type=AlertType.WELLBEING,
            reason="Stress level elevated",
            created_at=now,
            resolved=True,
        )

        assert alert.resolved is True

    def test_alert_default_resolved_is_false(self):
        """Verify Alert defaults resolved to False when not specified."""
        alert = Alert(
            alert_id=3,
            student_id="S003",
            alert_type=AlertType.ACADEMIC,
            reason="Recent submissions below threshold",
            created_at=datetime.now(),
        )

        assert alert.resolved is False


class TestAlertFieldAccess:
    """Test suite for accessing and modifying Alert fields."""

    def test_alert_field_access(self):
        """Verify all Alert fields are accessible."""
        now = datetime.now()
        alert = Alert(
            alert_id=4,
            student_id="S004",
            alert_type=AlertType.OTHER,
            reason="Low platform engagement",
            created_at=now,
        )

        # Access each field
        assert alert.alert_id is not None
        assert alert.student_id is not None
        assert alert.alert_type is not None
        assert alert.reason is not None
        assert alert.created_at is not None
        assert alert.resolved is not None

    def test_alert_field_mutation(self):
        """Verify Alert fields can be modified after instantiation."""
        alert = Alert(
            alert_id=5,
            student_id="S005",
            alert_type=AlertType.WELLBEING,
            reason="Initial concern",
            created_at=datetime.now(),
            resolved=False,
        )

        # Modify resolved field
        alert.resolved = True
        assert alert.resolved is True

        # Modify reason field
        alert.reason = "Updated reason"
        assert alert.reason == "Updated reason"

    def test_alert_equality(self):
        """Verify two Alert instances with same data are equal."""
        now = datetime.now()
        alert1 = Alert(
            alert_id=6,
            student_id="S006",
            alert_type=AlertType.ACADEMIC,
            reason="GPA below 2.0",
            created_at=now,
        )
        alert2 = Alert(
            alert_id=6,
            student_id="S006",
            alert_type=AlertType.ACADEMIC,
            reason="GPA below 2.0",
            created_at=now,
        )

        assert alert1 == alert2

    def test_alert_inequality(self):
        """Verify two Alert instances with different data are not equal."""
        now = datetime.now()
        alert1 = Alert(
            alert_id=7,
            student_id="S007",
            alert_type=AlertType.OTHER,
            reason="Reason A",
            created_at=now,
        )
        alert2 = Alert(
            alert_id=8,
            student_id="S008",
            alert_type=AlertType.OTHER,
            reason="Reason B",
            created_at=now,
        )

        assert alert1 != alert2


class TestAlertTypes:
    """Test suite for different alert type values."""

    def test_alert_low_attendance_type(self):
        """Verify low_attendance alert type is recognized."""
        alert = Alert(
            alert_id=9,
            student_id="S009",
            alert_type=AlertType.ATTENDANCE,
            reason="Missed 5+ sessions",
            created_at=datetime.now(),
        )

        assert alert.alert_type == "low_attendance"

    def test_alert_low_wellbeing_type(self):
        """Verify low_wellbeing alert type is recognized."""
        alert = Alert(
            alert_id=10,
            student_id="S010",
            alert_type=AlertType.WELLBEING,
            reason="Wellbeing score declined",
            created_at=datetime.now(),
        )

        assert alert.alert_type == "low_wellbeing"

    def test_alert_low_performance_type(self):
        """Verify low_performance alert type is recognized."""
        alert = Alert(
            alert_id=11,
            student_id="S011",
            alert_type=AlertType.ACADEMIC,
            reason="Assessment scores below average",
            created_at=datetime.now(),
        )

        assert alert.alert_type == "low_performance"

    def test_alert_custom_type(self):
        """Verify Alert accepts custom alert types."""
        alert = Alert(
            alert_id=12,
            student_id="S012",
            alert_type=AlertType.OTHER,
            reason="Custom reason",
            created_at=datetime.now(),
        )

        assert alert.alert_type == AlertType.OTHER


class TestAlertLifecycle:
    """Test suite for alert lifecycle and state changes."""

    def test_alert_creation_unresolved(self):
        """Verify newly created alert is unresolved by default."""
        alert = Alert(
            alert_id=13,
            student_id="S013",
            alert_type=AlertType.OTHER,
            reason="Test alert",
            created_at=datetime.now(),
        )

        assert alert.resolved is False

    def test_alert_resolution(self):
        """Verify alert can transition from unresolved to resolved."""
        alert = Alert(
            alert_id=14,
            student_id="S014",
            alert_type=AlertType.OTHER,
            reason="Test alert",
            created_at=datetime.now(),
            resolved=False,
        )

        # Simulate resolution
        alert.resolved = True

        assert alert.resolved is True

    def test_alert_unresolve(self):
        """Verify alert can transition from resolved back to unresolved."""
        alert = Alert(
            alert_id=15,
            student_id="S015",
            alert_type=AlertType.OTHER,
            reason="Test alert",
            created_at=datetime.now(),
            resolved=True,
        )

        # Simulate un-resolution
        alert.resolved = False

        assert alert.resolved is False


class TestAlertTimestamp:
    """Test suite for alert creation timestamp handling."""

    def test_alert_created_at_exact_time(self):
        """Verify Alert captures exact creation time."""
        now = datetime(2025, 1, 15, 10, 30, 45)
        alert = Alert(
            alert_id=16,
            student_id="S016",
            alert_type=AlertType.OTHER,
            reason="Test alert",
            created_at=now,
        )

        assert alert.created_at == now

    def test_alert_created_at_different_times(self):
        """Verify alerts with different creation times are distinguishable."""
        time1 = datetime(2025, 1, 15, 10, 0, 0)
        time2 = datetime(2025, 1, 15, 11, 0, 0)

        alert1 = Alert(
            alert_id=17,
            student_id="S017",
            alert_type=AlertType.OTHER,
            reason="Test alert",
            created_at=time1,
        )
        alert2 = Alert(
            alert_id=18,
            student_id="S018",
            alert_type=AlertType.OTHER,
            reason="Test alert",
            created_at=time2,
        )

        assert alert1.created_at != alert2.created_at
        assert alert1.created_at < alert2.created_at

    def test_alert_created_at_with_microseconds(self):
        """Verify Alert preserves microsecond precision in timestamps."""
        now = datetime(2025, 1, 15, 10, 30, 45, 123456)
        alert = Alert(
            alert_id=19,
            student_id="S019",
            alert_type=AlertType.OTHER,
            reason="Test alert",
            created_at=now,
        )

        assert alert.created_at.microsecond == 123456


class TestAlertStudentId:
    """Test suite for student ID handling in alerts."""

    def test_alert_with_numeric_student_id(self):
        """Verify Alert accepts numeric string student IDs."""
        alert = Alert(
            alert_id=20,
            student_id="123456",
            alert_type=AlertType.OTHER,
            reason="Test alert",
            created_at=datetime.now(),
        )

        assert alert.student_id == "123456"

    def test_alert_with_alphanumeric_student_id(self):
        """Verify Alert accepts alphanumeric student IDs."""
        alert = Alert(
            alert_id=21,
            student_id="S2025001",
            alert_type=AlertType.OTHER,
            reason="Test alert",
            created_at=datetime.now(),
        )

        assert alert.student_id == "S2025001"

    def test_alert_student_id_case_sensitive(self):
        """Verify Alert treats student IDs as case-sensitive."""
        alert1 = Alert(
            alert_id=22,
            student_id="S001",
            alert_type=AlertType.OTHER,
            reason="Test alert",
            created_at=datetime.now(),
        )
        alert2 = Alert(
            alert_id=23,
            student_id="s001",
            alert_type=AlertType.OTHER,
            reason="Test alert",
            created_at=datetime.now(),
        )

        assert alert1.student_id != alert2.student_id


class TestAlertDataIntegrity:
    """Test suite for data integrity and field types."""

    def test_alert_id_is_integer(self):
        """Verify alert_id field is an integer."""
        alert = Alert(
            alert_id=24,
            student_id="S024",
            alert_type=AlertType.OTHER,
            reason="Test alert",
            created_at=datetime.now(),
        )

        assert isinstance(alert.alert_id, int)

    def test_alert_student_id_is_string(self):
        """Verify student_id field is a string."""
        alert = Alert(
            alert_id=25,
            student_id="S025",
            alert_type=AlertType.OTHER,
            reason="Test alert",
            created_at=datetime.now(),
        )

        assert isinstance(alert.student_id, str)

    def test_alert_type_is_string(self):
        """Verify alert_type field is a string."""
        alert = Alert(
            alert_id=26,
            student_id="S026",
            alert_type=AlertType.OTHER,
            reason="Test alert",
            created_at=datetime.now(),
        )

        assert isinstance(alert.alert_type, str)

    def test_alert_reason_is_string(self):
        """Verify reason field is a string."""
        alert = Alert(
            alert_id=27,
            student_id="S027",
            alert_type=AlertType.OTHER,
            reason="Test alert",
            created_at=datetime.now(),
        )

        assert isinstance(alert.reason, str)

    def test_alert_created_at_is_datetime(self):
        """Verify created_at field is a datetime object."""
        alert = Alert(
            alert_id=28,
            student_id="S028",
            alert_type=AlertType.OTHER,
            reason="Test alert",
            created_at=datetime.now(),
        )

        assert isinstance(alert.created_at, datetime)

    def test_alert_resolved_is_boolean(self):
        """Verify resolved field is a boolean."""
        alert = Alert(
            alert_id=29,
            student_id="S029",
            alert_type=AlertType.OTHER,
            reason="Test alert",
            created_at=datetime.now(),
            resolved=True,
        )

        assert isinstance(alert.resolved, bool)


class TestAlertRepr:
    """Test suite for Alert string representation."""

    def test_alert_has_repr(self):
        """Verify Alert dataclass has a string representation."""
        alert = Alert(
            alert_id=30,
            student_id="S030",
            alert_type=AlertType.OTHER,
            reason="Test alert",
            created_at=datetime.now(),
        )

        repr_str = repr(alert)
        assert "Alert" in repr_str
        assert "S030" in repr_str

    def test_alert_repr_includes_fields(self):
        """Verify Alert repr includes all significant fields."""
        now = datetime(2025, 1, 15, 10, 30, 45)
        alert = Alert(
            alert_id=31,
            student_id="S031",
            alert_type=AlertType.OTHER,
            reason="Critical alert",
            created_at=now,
            resolved=True,
        )

        repr_str = repr(alert)
        # Dataclass repr typically includes all fields
        assert "alert_id" in repr_str or "31" in repr_str
