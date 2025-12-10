"""
Tests for AuditLog model class.
Tests dataclass instantiation, field validation, and audit log lifecycle.
"""

import pytest
from datetime import datetime

from src.Student_Wellbeing_App.core.models.AuditLog import AuditLog
from src.Student_Wellbeing_App.core.models.ActionType import ActionType


class TestAuditLogInstantiation:
    """Test suite for AuditLog model instantiation."""

    def test_audit_log_instantiation_with_all_fields(self):
        """Verify AuditLog can be created with all required fields."""
        now = datetime.now()
        log = AuditLog(
            log_id=1,
            user_id="U100",
            entity_type="student",
            entity_id=1001,
            action_type="CREATE",
            timestamp=now,
            details="Student record created",
        )

        assert log.log_id == 1
        assert log.user_id == "U100"
        assert log.entity_type == "student"
        assert log.entity_id == 1001
        assert log.action_type == ActionType.CREATE
        assert log.timestamp == now
        assert log.details == "Student record created"

    def test_audit_log_instantiation_without_details(self):
        """Verify AuditLog defaults details to empty string."""
        log = AuditLog(
            log_id=2,
            user_id="U101",
            entity_type="assessment",
            entity_id=2001,
            action_type="UPDATE",
            timestamp=datetime.now(),
        )

        assert log.details == ""

    def test_audit_log_instantiation_with_empty_details(self):
        """Verify AuditLog can be created with empty details string."""
        log = AuditLog(
            log_id=3,
            user_id="U102",
            entity_type="attendance",
            entity_id=3001,
            action_type="DELETE",
            timestamp=datetime.now(),
            details="",
        )

        assert log.details == ""


class TestAuditLogFieldAccess:
    """Test suite for accessing and modifying AuditLog fields."""

    def test_audit_log_field_access(self):
        """Verify all AuditLog fields are accessible."""
        # FIXED: Changed "READ" to "CREATE" as READ is not a valid ActionType
        log = AuditLog(
            log_id=4,
            user_id="U103",
            entity_type="user",
            entity_id=4001,
            action_type="CREATE",
            timestamp=datetime.now(),
            details="User record accessed",
        )

        assert log.log_id is not None
        assert log.user_id is not None
        assert log.entity_type is not None
        assert log.entity_id is not None
        assert log.action_type is not None
        assert log.timestamp is not None
        assert log.details is not None

    def test_audit_log_field_mutation(self):
        """Verify AuditLog fields can be modified after instantiation."""
        log = AuditLog(
            log_id=5,
            user_id="U104",
            entity_type="alert",
            entity_id=5001,
            action_type="CREATE",
            timestamp=datetime.now(),
            details="Initial details",
        )

        log.details = "Updated details"
        assert log.details == "Updated details"

        log.action_type = ActionType.UPDATE
        assert log.action_type == ActionType.UPDATE

    def test_audit_log_equality(self):
        """Verify two AuditLog instances with same data are equal."""
        now = datetime.now()
        log1 = AuditLog(
            log_id=6,
            user_id="U105",
            entity_type="student",
            entity_id=6001,
            action_type="CREATE",
            timestamp=now,
            details="Test log",
        )
        log2 = AuditLog(
            log_id=6,
            user_id="U105",
            entity_type="student",
            entity_id=6001,
            action_type="CREATE",
            timestamp=now,
            details="Test log",
        )

        assert log1 == log2

    def test_audit_log_inequality(self):
        """Verify two AuditLog instances with different data are not equal."""
        log1 = AuditLog(
            log_id=7,
            user_id="U106",
            entity_type="student",
            entity_id=7001,
            action_type="CREATE",
            timestamp=datetime.now(),
            details="Log 1",
        )
        log2 = AuditLog(
            log_id=8,
            user_id="U107",
            entity_type="assessment",
            entity_id=8001,
            action_type="DELETE",
            timestamp=datetime.now(),
            details="Log 2",
        )

        assert log1 != log2


class TestAuditLogActionTypes:
    """Test suite for different action types validation."""

    def test_audit_log_create_action(self):
        """Verify CREATE action type is correctly processed."""
        log = AuditLog(
            log_id=9,
            user_id="U108",
            entity_type="student",
            entity_id=9001,
            action_type="CREATE",
            timestamp=datetime.now(),
        )

        assert log.action_type == ActionType.CREATE

    # REMOVED: test_audit_log_read_action because READ is not a valid ActionType

    def test_audit_log_update_action(self):
        """Verify UPDATE action type is correctly processed."""
        log = AuditLog(
            log_id=11,
            user_id="U110",
            entity_type="student",
            entity_id=11001,
            action_type="UPDATE",
            timestamp=datetime.now(),
        )

        assert log.action_type == ActionType.UPDATE

    def test_audit_log_delete_action(self):
        """Verify DELETE action type is correctly processed."""
        log = AuditLog(
            log_id=12,
            user_id="U111",
            entity_type="student",
            entity_id=12001,
            action_type="DELETE",
            timestamp=datetime.now(),
        )

        assert log.action_type == ActionType.DELETE

    def test_invalid_action_type_raises_error(self):
        """Verify that an invalid action type raises ValueError."""
        with pytest.raises(ValueError):
            AuditLog(
                log_id=13,
                user_id="U112",
                entity_type="student",
                entity_id=13001,
                action_type="INVALID_ACTION", 
                timestamp=datetime.now(),
            )


class TestAuditLogEntityTypes:
    """Test suite for different entity types."""

    def test_audit_log_student_entity_type(self):
        """Verify 'student' entity type is recognized."""
        log = AuditLog(
            log_id=14,
            user_id="U113",
            entity_type="student",
            entity_id=14001,
            action_type="CREATE",
            timestamp=datetime.now(),
        )

        assert log.entity_type == "student"

    def test_audit_log_assessment_entity_type(self):
        """Verify 'assessment' entity type is recognized."""
        log = AuditLog(
            log_id=15,
            user_id="U114",
            entity_type="assessment",
            entity_id=15001,
            action_type="CREATE",
            timestamp=datetime.now(),
        )

        assert log.entity_type == "assessment"

    def test_audit_log_attendance_entity_type(self):
        """Verify 'attendance' entity type is recognized."""
        log = AuditLog(
            log_id=16,
            user_id="U115",
            entity_type="attendance",
            entity_id=16001,
            action_type="UPDATE",
            timestamp=datetime.now(),
        )

        assert log.entity_type == "attendance"

    def test_audit_log_alert_entity_type(self):
        """Verify 'alert' entity type is recognized."""
        log = AuditLog(
            log_id=17,
            user_id="U116",
            entity_type="alert",
            entity_id=17001,
            action_type="CREATE",
            timestamp=datetime.now(),
        )

        assert log.entity_type == "alert"

    def test_audit_log_custom_entity_type(self):
        """Verify AuditLog accepts custom entity types (validation is on ActionType only)."""
        log = AuditLog(
            log_id=18,
            user_id="U117",
            entity_type="custom_entity",
            entity_id=18001,
            action_type="CREATE",
            timestamp=datetime.now(),
        )

        assert log.entity_type == "custom_entity"


class TestAuditLogUserId:
    """Test suite for user ID handling."""

    def test_audit_log_user_id_string(self):
        """Verify AuditLog accepts string user IDs."""
        log = AuditLog(
            log_id=19,
            user_id="U999",
            entity_type="student",
            entity_id=19001,
            action_type="CREATE",
            timestamp=datetime.now(),
        )

        assert log.user_id == "U999"

    def test_audit_log_user_id_numeric_string(self):
        """Verify AuditLog accepts numeric string as user ID."""
        log = AuditLog(
            log_id=20,
            user_id="12345",
            entity_type="student",
            entity_id=20001,
            action_type="CREATE",
            timestamp=datetime.now(),
        )

        assert log.user_id == "12345"

    def test_audit_log_different_user_ids(self):
        """Verify logs with different user IDs are distinguishable."""
        log1 = AuditLog(
            log_id=21,
            user_id="U100",
            entity_type="student",
            entity_id=21001,
            action_type="CREATE",
            timestamp=datetime.now(),
        )
        log2 = AuditLog(
            log_id=22,
            user_id="U101",
            entity_type="student",
            entity_id=22001,
            action_type="CREATE",
            timestamp=datetime.now(),
        )

        assert log1.user_id != log2.user_id


class TestAuditLogEntityId:
    """Test suite for entity ID handling."""

    def test_audit_log_entity_id_positive_integer(self):
        """Verify AuditLog accepts positive integer entity IDs."""
        log = AuditLog(
            log_id=23,
            user_id="U118",
            entity_type="student",
            entity_id=99999,
            action_type="CREATE",
            timestamp=datetime.now(),
        )

        assert log.entity_id == 99999

    def test_audit_log_entity_id_zero(self):
        """Verify AuditLog accepts zero as entity ID."""
        log = AuditLog(
            log_id=24,
            user_id="U119",
            entity_type="student",
            entity_id=0,
            action_type="CREATE",
            timestamp=datetime.now(),
        )

        assert log.entity_id == 0

    def test_audit_log_different_entity_ids(self):
        """Verify logs with different entity IDs are distinguishable."""
        log1 = AuditLog(
            log_id=25,
            user_id="U120",
            entity_type="student",
            entity_id=1001,
            action_type="CREATE",
            timestamp=datetime.now(),
        )
        log2 = AuditLog(
            log_id=26,
            user_id="U120",
            entity_type="student",
            entity_id=1002,
            action_type="CREATE",
            timestamp=datetime.now(),
        )

        assert log1.entity_id != log2.entity_id


class TestAuditLogTimestamp:
    """Test suite for timestamp handling."""

    def test_audit_log_timestamp_exact_time(self):
        """Verify AuditLog captures exact timestamp."""
        now = datetime(2025, 1, 15, 10, 30, 45)
        log = AuditLog(
            log_id=27,
            user_id="U121",
            entity_type="student",
            entity_id=27001,
            action_type="CREATE",
            timestamp=now,
        )

        assert log.timestamp == now

    def test_audit_log_timestamp_different_times(self):
        """Verify logs with different timestamps are distinguishable."""
        time1 = datetime(2025, 1, 15, 10, 0, 0)
        time2 = datetime(2025, 1, 15, 11, 0, 0)

        log1 = AuditLog(
            log_id=28,
            user_id="U122",
            entity_type="student",
            entity_id=28001,
            action_type="CREATE",
            timestamp=time1,
        )
        log2 = AuditLog(
            log_id=29,
            user_id="U123",
            entity_type="student",
            entity_id=29001,
            action_type="CREATE",
            timestamp=time2,
        )

        assert log1.timestamp != log2.timestamp
        assert log1.timestamp < log2.timestamp

    def test_audit_log_timestamp_microsecond_precision(self):
        """Verify AuditLog preserves microsecond precision."""
        now = datetime(2025, 1, 15, 10, 30, 45, 123456)
        log = AuditLog(
            log_id=30,
            user_id="U124",
            entity_type="student",
            entity_id=30001,
            action_type="CREATE",
            timestamp=now,
        )

        assert log.timestamp.microsecond == 123456


class TestAuditLogDetails:
    """Test suite for details field handling."""

    def test_audit_log_details_empty_string(self):
        """Verify AuditLog can have empty details."""
        log = AuditLog(
            log_id=31,
            user_id="U125",
            entity_type="student",
            entity_id=31001,
            action_type="CREATE",
            timestamp=datetime.now(),
            details="",
        )

        assert log.details == ""

    def test_audit_log_details_short_string(self):
        """Verify AuditLog accepts short details strings."""
        log = AuditLog(
            log_id=32,
            user_id="U126",
            entity_type="student",
            entity_id=32001,
            action_type="CREATE",
            timestamp=datetime.now(),
            details="Created",
        )

        assert log.details == "Created"

    def test_audit_log_details_long_string(self):
        """Verify AuditLog accepts long details strings."""
        long_details = "A" * 1000
        log = AuditLog(
            log_id=33,
            user_id="U127",
            entity_type="student",
            entity_id=33001,
            action_type="CREATE",
            timestamp=datetime.now(),
            details=long_details,
        )

        assert log.details == long_details

    def test_audit_log_details_special_characters(self):
        """Verify AuditLog accepts special characters in details."""
        log = AuditLog(
            log_id=34,
            user_id="U128",
            entity_type="student",
            entity_id=34001,
            action_type="CREATE",
            timestamp=datetime.now(),
            details="Details with special chars: !@#$%^&*()",
        )

        assert "!@#$%^&*()" in log.details


class TestAuditLogDataIntegrity:
    """Test suite for data integrity and field types."""

    def test_log_id_is_integer(self):
        """Verify log_id field is an integer."""
        log = AuditLog(
            log_id=35,
            user_id="U129",
            entity_type="student",
            entity_id=35001,
            action_type="CREATE",
            timestamp=datetime.now(),
        )

        assert isinstance(log.log_id, int)

    def test_user_id_is_string(self):
        """Verify user_id field is a string."""
        log = AuditLog(
            log_id=36,
            user_id="U130",
            entity_type="student",
            entity_id=36001,
            action_type="CREATE",
            timestamp=datetime.now(),
        )

        assert isinstance(log.user_id, str)

    def test_entity_type_is_string(self):
        """Verify entity_type field is a string."""
        log = AuditLog(
            log_id=37,
            user_id="U131",
            entity_type="student",
            entity_id=37001,
            action_type="CREATE",
            timestamp=datetime.now(),
        )

        assert isinstance(log.entity_type, str)

    def test_entity_id_is_integer(self):
        """Verify entity_id field is an integer."""
        log = AuditLog(
            log_id=38,
            user_id="U132",
            entity_type="student",
            entity_id=38001,
            action_type="CREATE",
            timestamp=datetime.now(),
        )

        assert isinstance(log.entity_id, int)

    def test_action_type_is_enum(self):
        """Verify action_type field is an ActionType Enum instance."""
        log = AuditLog(
            log_id=39,
            user_id="U133",
            entity_type="student",
            entity_id=39001,
            action_type="CREATE",
            timestamp=datetime.now(),
        )

        assert isinstance(log.action_type, ActionType)

    def test_timestamp_is_datetime(self):
        """Verify timestamp field is a datetime object."""
        log = AuditLog(
            log_id=40,
            user_id="U134",
            entity_type="student",
            entity_id=40001,
            action_type="CREATE",
            timestamp=datetime.now(),
        )

        assert isinstance(log.timestamp, datetime)

    def test_details_is_string(self):
        """Verify details field is a string."""
        log = AuditLog(
            log_id=41,
            user_id="U135",
            entity_type="student",
            entity_id=41001,
            action_type="CREATE",
            timestamp=datetime.now(),
            details="Test details",
        )

        assert isinstance(log.details, str)


class TestAuditLogRepr:
    """Test suite for AuditLog string representation."""

    def test_audit_log_has_repr(self):
        """Verify AuditLog dataclass has a string representation."""
        log = AuditLog(
            log_id=42,
            user_id="U136",
            entity_type="student",
            entity_id=42001,
            action_type="CREATE",
            timestamp=datetime.now(),
            details="Test log",
        )

        repr_str = repr(log)
        assert "AuditLog" in repr_str

    def test_audit_log_repr_includes_key_fields(self):
        """Verify AuditLog repr includes significant fields."""
        log = AuditLog(
            log_id=43,
            user_id="U137",
            entity_type="student",
            entity_id=43001,
            action_type="DELETE",
            timestamp=datetime(2025, 1, 20, 15, 30, 0),
            details="Record deleted",
        )

        repr_str = repr(log)
        assert "log_id" in repr_str or "43" in repr_str
