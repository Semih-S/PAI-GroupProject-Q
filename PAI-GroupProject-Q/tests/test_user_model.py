"""
Tests for User model class.
Tests dataclass instantiation, field validation, and user permissions.
"""

import pytest

from Student_Wellbeing_App.core.models.User import User
from Student_Wellbeing_App.core.models.UserRole import UserRole


class TestUserInstantiation:
    """Test suite for User model instantiation."""

    def test_user_instantiation_with_all_fields(self):
        """Verify User can be created with all required fields."""
        user = User(
            user_id="admin1",
            first_name="John",
            lastname="Administrator",
            password_hash="hash_abc123",
            role=UserRole.ADMIN,
        )

        assert user.user_id == "admin1"
        assert user.first_name == "John"
        assert user.lastname == "Administrator"
        assert user.password_hash == "hash_abc123"
        assert user.role == UserRole.ADMIN

    def test_user_instantiation_with_wellbeing_officer_role(self):
        """Verify User can be created with WELLBEING_OFFICER role."""
        user = User(
            user_id="officer1",
            first_name="Sarah",
            lastname="Wellbeing",
            password_hash="hash_def456",
            role=UserRole.WELLBEING_OFFICER,
        )

        assert user.role == UserRole.WELLBEING_OFFICER

    def test_user_instantiation_with_course_director_role(self):
        """Verify User can be created with COURSE_DIRECTOR role."""
        user = User(
            user_id="advisor1",
            first_name="David",
            lastname="Director",
            password_hash="hash_ghi789",
            role=UserRole.COURSE_DIRECTOR,
        )

        assert user.role == UserRole.COURSE_DIRECTOR

    def test_user_instantiation_with_student_role(self):
        """Verify User can be created with STUDENT role."""
        user = User(
            user_id="student1",
            first_name="Emily",
            lastname="Pupil",
            password_hash="hash_jkl012",
            role=UserRole.STUDENT,
        )

        assert user.role == UserRole.STUDENT


class TestUserFieldAccess:
    """Test suite for accessing and modifying User fields."""

    def test_user_field_access(self):
        """Verify all User fields are accessible."""
        user = User(
            user_id="user001",
            first_name="Robert",
            lastname="Smith",
            password_hash="hash_mno345",
            role=UserRole.ADMIN,
        )

        assert user.user_id is not None
        assert user.first_name is not None
        assert user.lastname is not None
        assert user.password_hash is not None
        assert user.role is not None

    def test_user_field_mutation_first_name(self):
        """Verify first_name field can be modified."""
        user = User(
            user_id="user002",
            first_name="Michael",
            lastname="Johnson",
            password_hash="hash_pqr678",
            role=UserRole.WELLBEING_OFFICER,
        )

        user.first_name = "Mike"
        assert user.first_name == "Mike"

    def test_user_field_mutation_lastname(self):
        """Verify lastname field can be modified."""
        user = User(
            user_id="user003",
            first_name="Jessica",
            lastname="Brown",
            password_hash="hash_stu901",
            role=UserRole.COURSE_DIRECTOR,
        )

        user.lastname = "Browne"
        assert user.lastname == "Browne"

    def test_user_field_mutation_password_hash(self):
        """Verify password_hash field can be modified."""
        user = User(
            user_id="user004",
            first_name="Christopher",
            lastname="Davis",
            password_hash="old_hash",
            role=UserRole.STUDENT,
        )

        user.password_hash = "new_hash_secure"
        assert user.password_hash == "new_hash_secure"

    def test_user_field_mutation_role(self):
        """Verify role field can be modified."""
        user = User(
            user_id="user005",
            first_name="Amanda",
            lastname="Wilson",
            password_hash="hash_vwx234",
            role=UserRole.STUDENT,
        )

        user.role = UserRole.WELLBEING_OFFICER
        assert user.role == UserRole.WELLBEING_OFFICER


class TestUserCanViewPersonalWellbeing:
    """Test suite for can_view_personal_wellbeing method."""

    def test_admin_can_view_personal_wellbeing(self):
        """Verify ADMIN role can view personal wellbeing."""
        admin = User(
            user_id="admin_user",
            first_name="Admin",
            lastname="User",
            password_hash="hash_yz123",
            role=UserRole.ADMIN,
        )

        assert admin.can_view_personal_wellbeing() is True

    def test_wellbeing_officer_can_view_personal_wellbeing(self):
        """Verify WELLBEING_OFFICER role can view personal wellbeing."""
        officer = User(
            user_id="wellbeing_user",
            first_name="Wellbeing",
            lastname="Officer",
            password_hash="hash_ab456",
            role=UserRole.WELLBEING_OFFICER,
        )

        assert officer.can_view_personal_wellbeing() is True

    def test_course_director_cannot_view_personal_wellbeing(self):
        """Verify COURSE_DIRECTOR role cannot view personal wellbeing."""
        director = User(
            user_id="director_user",
            first_name="Course",
            lastname="Director",
            password_hash="hash_cd789",
            role=UserRole.COURSE_DIRECTOR,
        )

        assert director.can_view_personal_wellbeing() is False

    def test_student_cannot_view_personal_wellbeing(self):
        """Verify STUDENT role cannot view personal wellbeing."""
        student = User(
            user_id="student_user",
            first_name="Student",
            lastname="User",
            password_hash="hash_ef012",
            role=UserRole.STUDENT,
        )

        assert student.can_view_personal_wellbeing() is False


class TestUserEquality:
    """Test suite for User equality and comparison."""

    def test_user_equality_identical_users(self):
        """Verify two User instances with same data are equal."""
        user1 = User(
            user_id="equal_user",
            first_name="Equal",
            lastname="User",
            password_hash="hash_gh345",
            role=UserRole.ADMIN,
        )
        user2 = User(
            user_id="equal_user",
            first_name="Equal",
            lastname="User",
            password_hash="hash_gh345",
            role=UserRole.ADMIN,
        )

        assert user1 == user2

    def test_user_inequality_different_user_ids(self):
        """Verify users with different IDs are not equal."""
        user1 = User(
            user_id="user_one",
            first_name="Test",
            lastname="User",
            password_hash="hash_ij678",
            role=UserRole.ADMIN,
        )
        user2 = User(
            user_id="user_two",
            first_name="Test",
            lastname="User",
            password_hash="hash_ij678",
            role=UserRole.ADMIN,
        )

        assert user1 != user2

    def test_user_inequality_different_roles(self):
        """Verify users with different roles are not equal."""
        user1 = User(
            user_id="same_id",
            first_name="Test",
            lastname="User",
            password_hash="hash_kl901",
            role=UserRole.ADMIN,
        )
        user2 = User(
            user_id="same_id",
            first_name="Test",
            lastname="User",
            password_hash="hash_kl901",
            role=UserRole.STUDENT,
        )

        assert user1 != user2

    def test_user_inequality_different_password_hashes(self):
        """Verify users with different password hashes are not equal."""
        user1 = User(
            user_id="user_six",
            first_name="Test",
            lastname="User",
            password_hash="hash_old",
            role=UserRole.WELLBEING_OFFICER,
        )
        user2 = User(
            user_id="user_six",
            first_name="Test",
            lastname="User",
            password_hash="hash_new",
            role=UserRole.WELLBEING_OFFICER,
        )

        assert user1 != user2


class TestUserIdField:
    """Test suite for user_id field handling."""

    def test_user_id_text_format(self):
        """Verify user_id field accepts text format."""
        user = User(
            user_id="admin001",
            first_name="Test",
            lastname="User",
            password_hash="hash_mn234",
            role=UserRole.ADMIN,
        )

        assert user.user_id == "admin001"

    def test_user_id_with_underscore(self):
        """Verify user_id field accepts underscore."""
        user = User(
            user_id="admin_001",
            first_name="Test",
            lastname="User",
            password_hash="hash_op567",
            role=UserRole.ADMIN,
        )

        assert user.user_id == "admin_001"

    def test_user_id_with_numeric_suffix(self):
        """Verify user_id field accepts numeric suffix."""
        user = User(
            user_id="user12345",
            first_name="Test",
            lastname="User",
            password_hash="hash_qr890",
            role=UserRole.ADMIN,
        )

        assert user.user_id == "user12345"

    def test_different_user_ids_are_distinguishable(self):
        """Verify users with different IDs are distinguishable."""
        user1 = User(
            user_id="first_user",
            first_name="First",
            lastname="User",
            password_hash="hash_st123",
            role=UserRole.ADMIN,
        )
        user2 = User(
            user_id="second_user",
            first_name="Second",
            lastname="User",
            password_hash="hash_uv456",
            role=UserRole.ADMIN,
        )

        assert user1.user_id != user2.user_id


class TestUserPasswordHash:
    """Test suite for password_hash field."""

    def test_user_password_hash_bcrypt_format(self):
        """Verify user accepts bcrypt-style hashes."""
        bcrypt_hash = "$2b$12$abc123def456ghi789jkl"
        user = User(
            user_id="user007",
            first_name="Test",
            lastname="User",
            password_hash=bcrypt_hash,
            role=UserRole.ADMIN,
        )

        assert user.password_hash == bcrypt_hash

    def test_user_password_hash_long_string(self):
        """Verify user accepts long hash strings."""
        long_hash = "a" * 100
        user = User(
            user_id="user008",
            first_name="Test",
            lastname="User",
            password_hash=long_hash,
            role=UserRole.ADMIN,
        )

        assert user.password_hash == long_hash

    def test_user_password_hash_complex_characters(self):
        """Verify user accepts hashes with special characters."""
        complex_hash = "$2b$12$N9qo8uLO.Hek$qDdk.n8DQ90jJNknK3W8K"
        user = User(
            user_id="user009",
            first_name="Test",
            lastname="User",
            password_hash=complex_hash,
            role=UserRole.ADMIN,
        )

        assert user.password_hash == complex_hash


class TestUserRoleField:
    """Test suite for role field."""

    def test_user_role_is_user_role_enum(self):
        """Verify role field is a UserRole enum."""
        user = User(
            user_id="user010",
            first_name="Test",
            lastname="User",
            password_hash="hash_wx789",
            role=UserRole.ADMIN,
        )

        assert isinstance(user.role, UserRole)

    def test_all_user_roles_accepted(self):
        """Verify all UserRole enum values are accepted."""
        roles = [
            UserRole.ADMIN,
            UserRole.WELLBEING_OFFICER,
            UserRole.COURSE_DIRECTOR,
            UserRole.STUDENT,
        ]

        for role in roles:
            user = User(
                user_id="user_role_test",
                first_name="Test",
                lastname="User",
                password_hash="hash_yz012",
                role=role,
            )
            assert user.role == role


class TestUserDataIntegrity:
    """Test suite for data integrity and field types."""

    def test_user_id_is_string(self):
        """Verify user_id field is a string."""
        user = User(
            user_id="user011",
            first_name="Test",
            lastname="User",
            password_hash="hash_ab345",
            role=UserRole.ADMIN,
        )

        assert isinstance(user.user_id, str)

    def test_first_name_is_string(self):
        """Verify first_name field is a string."""
        user = User(
            user_id="user012",
            first_name="John",
            lastname="Doe",
            password_hash="hash_cd678",
            role=UserRole.ADMIN,
        )

        assert isinstance(user.first_name, str)

    def test_lastname_is_string(self):
        """Verify lastname field is a string."""
        user = User(
            user_id="user013",
            first_name="Jane",
            lastname="Smith",
            password_hash="hash_ef901",
            role=UserRole.ADMIN,
        )

        assert isinstance(user.lastname, str)

    def test_password_hash_is_string(self):
        """Verify password_hash field is a string."""
        user = User(
            user_id="user014",
            first_name="Test",
            lastname="User",
            password_hash="hash_gh234",
            role=UserRole.ADMIN,
        )

        assert isinstance(user.password_hash, str)

    def test_role_is_user_role_type(self):
        """Verify role field is UserRole type."""
        user = User(
            user_id="user015",
            first_name="Test",
            lastname="User",
            password_hash="hash_ij567",
            role=UserRole.WELLBEING_OFFICER,
        )

        assert isinstance(user.role, UserRole)


class TestUserFullName:
    """Test suite for user full name composition."""

    def test_user_full_name_composition(self):
        """Verify full name can be composed from first and last name."""
        user = User(
            user_id="user016",
            first_name="Alexander",
            lastname="Hamilton",
            password_hash="hash_kl890",
            role=UserRole.ADMIN,
        )

        full_name = f"{user.first_name} {user.lastname}"
        assert full_name == "Alexander Hamilton"

    def test_user_full_name_with_single_char_names(self):
        """Verify full name works with single character names."""
        user = User(
            user_id="user017",
            first_name="A",
            lastname="B",
            password_hash="hash_mn123",
            role=UserRole.ADMIN,
        )

        full_name = f"{user.first_name} {user.lastname}"
        assert full_name == "A B"


class TestUserRepr:
    """Test suite for User string representation."""

    def test_user_has_repr(self):
        """Verify User dataclass has a string representation."""
        user = User(
            user_id="user018",
            first_name="Test",
            lastname="User",
            password_hash="hash_op456",
            role=UserRole.ADMIN,
        )

        repr_str = repr(user)
        assert "User" in repr_str

    def test_user_repr_includes_key_fields(self):
        """Verify User repr includes significant fields."""
        user = User(
            user_id="user019",
            first_name="Example",
            lastname="Admin",
            password_hash="hash_qr789",
            role=UserRole.ADMIN,
        )

        repr_str = repr(user)
        # Dataclass repr typically includes field names
        assert "user_id" in repr_str or "user019" in repr_str

    def test_user_repr_distinct_for_different_users(self):
        """Verify repr differs for different users."""
        user1 = User(
            user_id="user020",
            first_name="First",
            lastname="User",
            password_hash="hash_st012",
            role=UserRole.ADMIN,
        )
        user2 = User(
            user_id="user021",
            first_name="Second",
            lastname="Admin",
            password_hash="hash_uv345",
            role=UserRole.WELLBEING_OFFICER,
        )

        assert repr(user1) != repr(user2)
