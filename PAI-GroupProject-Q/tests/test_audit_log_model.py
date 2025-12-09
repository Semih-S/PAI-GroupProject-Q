"""
Tests for AuditLog model class.
Tests dataclass instantiation, field validation, and audit log lifecycle.
"""

import pytest
from datetime import datetime

from src.Student_Wellbeing_App.core.models.AuditLog import AuditLog


class TestAuditLogInstantiation:
    """Test suite for AuditLog model instantiation."""

    def test_audit_log_instantiation_with_all_fields(self):
        """Verify AuditLog can be created with all required fields."""
        now = datetime.now()
        log = AuditLog(
            log_id=1,
            user_id=100,
            entitiy_type="student",
            entity_id=1001,
            action_type="CREATE",
            timestamp=now,
            details="Student record created",
        )

        assert log.log_id == 1
        assert log.user_id == 100
        assert log.entitiy_type == "student"
        assert log.entity_id == 1001
        assert log.action_type == "CREATE"
        assert log.timestamp == now
        assert log.details == "Student record created"

    def test_audit_log_instantiation_without_details(self):
        """Verify AuditLog defaults details to empty string."""
        log = AuditLog(
            log_id=2,
            user_id=101,
            entitiy_type="assessment",
            entity_id=2001,
            action_type="UPDATE",
            timestamp=datetime.now(),
        )

        assert log.details == ""

    def test_audit_log_instantiation_with_empty_details(self):
        """Verify AuditLog can be created with empty details string."""
        log = AuditLog(
            log_id=3,
            user_id=102,
            entitiy_type="attendance",
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
        log = AuditLog(
            log_id=4,
            user_id=103,
            entitiy_type="user",
            entity_id=4001,
            action_type="READ",
            timestamp=datetime.now(),
            details="User record accessed",
        )

        assert log.log_id is not None
        assert log.user_id is not None
        assert log.entitiy_type is not None
        assert log.entity_id is not None
        assert log.action_type is not None
        assert log.timestamp is not None
        assert log.details is not None

    def test_audit_log_field_mutation(self):
        """Verify AuditLog fields can be modified after instantiation."""
        log = AuditLog(
            log_id=5,
            user_id=104,
            entitiy_type="alert",
            entity_id=5001,
            action_type="CREATE",
            timestamp=datetime.now(),
            details="Initial details",
        )

        log.details = "Updated details"
        assert log.details == "Updated details"

        log.action_type = "UPDATE"
        assert log.action_type == "UPDATE"

    def test_audit_log_equality(self):
        """Verify two AuditLog instances with same data are equal."""
        now = datetime.now()
        log1 = AuditLog(
            log_id=6,
            user_id=105,
            entitiy_type="student",
            entity_id=6001,
            action_type="CREATE",
            timestamp=now,
            details="Test log",
        )
        log2 = AuditLog(
            log_id=6,
            user_id=105,
            entitiy_type="student",
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
            user_id=106,
            entitiy_type="student",
            entity_id=7001,
            action_type="CREATE",
            timestamp=datetime.now(),
            details="Log 1",
        )
        log2 = AuditLog(
            log_id=8,
            user_id=107,
            entitiy_type="assessment",
            entity_id=8001,
            action_type="DELETE",
            timestamp=datetime.now(),
            details="Log 2",
        )

        assert log1 != log2


class TestAuditLogActionTypes:
    """Test suite for different action types."""

    def test_audit_log_create_action(self):
        """Verify CREATE action type is recognized."""
        log = AuditLog(
            log_id=9,
            user_id=108,
            entitiy_type="student",
            entity_id=9001,
            action_type="CREATE",
            timestamp=datetime.now(),
        )

        assert log.action_type == "CREATE"

    def test_audit_log_read_action(self):
        """Verify READ action type is recognized."""
        log = AuditLog(
            log_id=10,
            user_id=109,
            entitiy_type="student",
            entity_id=10001,
            action_type="READ",
            timestamp=datetime.now(),
        )

        assert log.action_type == "READ"

    def test_audit_log_update_action(self):
        """Verify UPDATE action type is recognized."""
        log = AuditLog(
            log_id=11,
            user_id=110,
            entitiy_type="student",
            entity_id=11001,
            action_type="UPDATE",
            timestamp=datetime.now(),
        )

        assert log.action_type == "UPDATE"

    def test_audit_log_delete_action(self):
        """Verify DELETE action type is recognized."""
        log = AuditLog(
            log_id=12,
            user_id=111,
            entitiy_type="student",
            entity_id=12001,
            action_type="DELETE",
            timestamp=datetime.now(),
        )

        assert log.action_type == "DELETE"

    def test_audit_log_custom_action_type(self):
        """Verify AuditLog accepts custom action types."""
        log = AuditLog(
            log_id=13,
            user_id=112,
            entitiy_type="student",
            entity_id=13001,
            action_type="EXPORT",
            timestamp=datetime.now(),
        )

        assert log.action_type == "EXPORT"


class TestAuditLogEntityTypes:
    """Test suite for different entity types."""

    def test_audit_log_student_entity_type(self):
        """Verify 'student' entity type is recognized."""
        log = AuditLog(
            log_id=14,
            user_id=113,
            entitiy_type="student",
            entity_id=14001,
            action_type="CREATE",
            timestamp=datetime.now(),
        )

        assert log.entitiy_type == "student"

    def test_audit_log_assessment_entity_type(self):
        """Verify 'assessment' entity type is recognized."""
        log = AuditLog(
            log_id=15,
            user_id=114,
            entitiy_type="assessment",
            entity_id=15001,
            action_type="CREATE",
            timestamp=datetime.now(),
        )

        assert log.entitiy_type == "assessment"

    def test_audit_log_attendance_entity_type(self):
        """Verify 'attendance' entity type is recognized."""
        log = AuditLog(
            log_id=16,
            user_id=115,
            entitiy_type="attendance",
            entity_id=16001,
            action_type="UPDATE",
            timestamp=datetime.now(),
        )

        assert log.entitiy_type == "attendance"

    def test_audit_log_alert_entity_type(self):
        """Verify 'alert' entity type is recognized."""
        log = AuditLog(
            log_id=17,
            user_id=116,
            entitiy_type="alert",
            entity_id=17001,
            action_type="CREATE",
            timestamp=datetime.now(),
        )

        assert log.entitiy_type == "alert"

    def test_audit_log_custom_entity_type(self):
        """Verify AuditLog accepts custom entity types."""
        log = AuditLog(
            log_id=18,
            user_id=117,
            entitiy_type="custom_entity",
            entity_id=18001,
            action_type="CREATE",
            timestamp=datetime.now(),
        )

        assert log.entitiy_type == "custom_entity"


class TestAuditLogUserId:
    """Test suite for user ID handling."""

    def test_audit_log_user_id_positive_integer(self):
        """Verify AuditLog accepts positive integer user IDs."""
        log = AuditLog(
            log_id=19,
            user_id=999,
            entitiy_type="student",
            entity_id=19001,
            action_type="CREATE",
            timestamp=datetime.now(),
        )

        assert log.user_id == 999

    def test_audit_log_user_id_zero(self):
        """Verify AuditLog accepts zero as user ID."""
        log = AuditLog(
            log_id=20,
            user_id=0,
            entitiy_type="student",
            entity_id=20001,
            action_type="CREATE",
            timestamp=datetime.now(),
        )

        assert log.user_id == 0

    def test_audit_log_different_user_ids(self):
        """Verify logs with different user IDs are distinguishable."""
        log1 = AuditLog(
            log_id=21,
            user_id=100,
            entitiy_type="student",
            entity_id=21001,
            action_type="CREATE",
            timestamp=datetime.now(),
        )
        log2 = AuditLog(
            log_id=22,
            user_id=101,
            entitiy_type="student",
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
            user_id=118,
            entitiy_type="student",
            entity_id=99999,
            action_type="CREATE",
            timestamp=datetime.now(),
        )

        assert log.entity_id == 99999

    def test_audit_log_entity_id_zero(self):
        """Verify AuditLog accepts zero as entity ID."""
        log = AuditLog(
            log_id=24,
            user_id=119,
            entitiy_type="student",
            entity_id=0,
            action_type="CREATE",
            timestamp=datetime.now(),
        )

        assert log.entity_id == 0

    def test_audit_log_different_entity_ids(self):
        """Verify logs with different entity IDs are distinguishable."""
        log1 = AuditLog(
            log_id=25,
            user_id=120,
            entitiy_type="student",
            entity_id=1001,
            action_type="CREATE",
            timestamp=datetime.now(),
        )
        log2 = AuditLog(
            log_id=26,
            user_id=120,
            entitiy_type="student",
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
            user_id=121,
            entitiy_type="student",
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
            user_id=122,
            entitiy_type="student",
            entity_id=28001,
            action_type="CREATE",
            timestamp=time1,
        )
        log2 = AuditLog(
            log_id=29,
            user_id=123,
            entitiy_type="student",
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
            user_id=124,
            entitiy_type="student",
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
            user_id=125,
            entitiy_type="student",
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
            user_id=126,
            entitiy_type="student",
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
            user_id=127,
            entitiy_type="student",
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
            user_id=128,
            entitiy_type="student",
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
            user_id=129,
            entitiy_type="student",
            entity_id=35001,
            action_type="CREATE",
            timestamp=datetime.now(),
        )

        assert isinstance(log.log_id, int)

    def test_user_id_is_integer(self):
        """Verify user_id field is an integer."""
        log = AuditLog(
            log_id=36,
            user_id=130,
            entitiy_type="student",
            entity_id=36001,
            action_type="CREATE",
            timestamp=datetime.now(),
        )

        assert isinstance(log.user_id, int)

    def test_entitiy_type_is_string(self):
        """Verify entitiy_type field is a string."""
        log = AuditLog(
            log_id=37,
            user_id=131,
            entitiy_type="student",
            entity_id=37001,
            action_type="CREATE",
            timestamp=datetime.now(),
        )

        assert isinstance(log.entitiy_type, str)

    def test_entity_id_is_integer(self):
        """Verify entity_id field is an integer."""
        log = AuditLog(
            log_id=38,
            user_id=132,
            entitiy_type="student",
            entity_id=38001,
            action_type="CREATE",
            timestamp=datetime.now(),
        )

        assert isinstance(log.entity_id, int)

    def test_action_type_is_string(self):
        """Verify action_type field is a string."""
        log = AuditLog(
            log_id=39,
            user_id=133,
            entitiy_type="student",
            entity_id=39001,
            action_type="CREATE",
            timestamp=datetime.now(),
        )

        assert isinstance(log.action_type, str)

    def test_timestamp_is_datetime(self):
        """Verify timestamp field is a datetime object."""
        log = AuditLog(
            log_id=40,
            user_id=134,
            entitiy_type="student",
            entity_id=40001,
            action_type="CREATE",
            timestamp=datetime.now(),
        )

        assert isinstance(log.timestamp, datetime)

    def test_details_is_string(self):
        """Verify details field is a string."""
        log = AuditLog(
            log_id=41,
            user_id=135,
            entitiy_type="student",
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
            user_id=136,
            entitiy_type="student",
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
            user_id=137,
            entitiy_type="student",
            entity_id=43001,
            action_type="DELETE",
            timestamp=datetime(2025, 1, 20, 15, 30, 0),
            details="Record deleted",
        )

        repr_str = repr(log)
        # Dataclass repr typically includes field names
        assert "log_id" in repr_str or "43" in repr_str

