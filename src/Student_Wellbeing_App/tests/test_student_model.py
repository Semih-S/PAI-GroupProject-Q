"""
Tests for Student model class.
Tests dataclass instantiation, field validation, and student lifecycle.
"""

import pytest

from src.Student_Wellbeing_App.core.models.Student import Student


class TestStudentInstantiation:
    """Test suite for Student model instantiation."""

    def test_student_instantiation_with_all_fields(self):
        """Verify Student can be created with all required fields."""
        student = Student(
            student_id="S001",
            first_name="John",
            lastname="Doe",
            email="john.doe@university.edu",
            password="SecurePass123!",
            year=2025,
        )

        assert student.student_id == "S001"
        assert student.first_name == "John"
        assert student.lastname == "Doe"
        assert student.email == "john.doe@university.edu"
        assert student.password == "SecurePass123!"
        assert student.year == 2025

    def test_student_instantiation_with_different_year(self):
        """Verify Student accepts different year values."""
        student = Student(
            student_id="S002",
            first_name="Jane",
            lastname="Smith",
            email="jane.smith@university.edu",
            password="AnotherPass456!",
            year=2024,
        )

        assert student.year == 2024

    def test_student_instantiation_with_various_student_ids(self):
        """Verify Student accepts various student ID formats."""
        formats = ["S001", "001", "A123456", "STUDENT2024"]

        for sid in formats:
            student = Student(
                student_id=sid,
                first_name="Test",
                lastname="User",
                email="test@university.edu",
                password="TestPass123!",
                year=2025,
            )
            assert student.student_id == sid


class TestStudentFieldAccess:
    """Test suite for accessing and modifying Student fields."""

    def test_student_field_access(self):
        """Verify all Student fields are accessible."""
        student = Student(
            student_id="S003",
            first_name="Alice",
            lastname="Johnson",
            email="alice.johnson@university.edu",
            password="AlicePass789!",
            year=2023,
        )

        assert student.student_id is not None
        assert student.first_name is not None
        assert student.lastname is not None
        assert student.email is not None
        assert student.password is not None
        assert student.year is not None

    def test_student_field_mutation_first_name(self):
        """Verify first_name field can be modified."""
        student = Student(
            student_id="S004",
            first_name="Robert",
            lastname="Brown",
            email="robert.brown@university.edu",
            password="RobertPass456!",
            year=2025,
        )

        student.first_name = "Bob"
        assert student.first_name == "Bob"

    def test_student_field_mutation_lastname(self):
        """Verify lastname field can be modified."""
        student = Student(
            student_id="S005",
            first_name="Michael",
            lastname="Davis",
            email="michael.davis@university.edu",
            password="MichaelPass123!",
            year=2025,
        )

        student.lastname = "Davies"
        assert student.lastname == "Davies"

    def test_student_field_mutation_email(self):
        """Verify email field can be modified."""
        student = Student(
            student_id="S006",
            first_name="Sarah",
            lastname="Wilson",
            email="sarah.wilson@university.edu",
            password="SarahPass789!",
            year=2024,
        )

        student.email = "sarah.w@university.edu"
        assert student.email == "sarah.w@university.edu"

    def test_student_field_mutation_password(self):
        """Verify password field can be modified."""
        student = Student(
            student_id="S007",
            first_name="Emma",
            lastname="Taylor",
            email="emma.taylor@university.edu",
            password="OldPassword123!",
            year=2025,
        )

        student.password = "NewPassword456!"
        assert student.password == "NewPassword456!"

    def test_student_field_mutation_year(self):
        """Verify year field can be modified."""
        student = Student(
            student_id="S008",
            first_name="David",
            lastname="Anderson",
            email="david.anderson@university.edu",
            password="DavidPass789!",
            year=2024,
        )

        student.year = 2025
        assert student.year == 2025


class TestStudentFullName:
    """Test suite for full_name property."""

    def test_full_name_property_basic(self):
        """Verify full_name property returns first and last name combined."""
        student = Student(
            student_id="S009",
            first_name="Christopher",
            lastname="Martinez",
            email="christopher.martinez@university.edu",
            password="ChrisPass123!",
            year=2025,
        )

        assert student.full_name == "Christopher Martinez"

    def test_full_name_property_with_different_names(self):
        """Verify full_name property works with various name combinations."""
        test_cases = [
            ("John", "Doe", "John Doe"),
            ("Mary", "Smith", "Mary Smith"),
            ("José", "García", "José García"),
            ("李", "明", "李 明"),
            ("O", "Brien", "O Brien"),
        ]

        for first, last, expected in test_cases:
            student = Student(
                student_id="S010",
                first_name=first,
                lastname=last,
                email="test@university.edu",
                password="TestPass123!",
                year=2025,
            )
            assert student.full_name == expected

    def test_full_name_property_with_single_char_names(self):
        """Verify full_name property works with single character names."""
        student = Student(
            student_id="S011",
            first_name="A",
            lastname="B",
            email="ab@university.edu",
            password="ABPass123!",
            year=2025,
        )

        assert student.full_name == "A B"

    def test_full_name_property_with_long_names(self):
        """Verify full_name property works with long names."""
        long_first = "Christopher"
        long_last = "Schwarzenegger"
        student = Student(
            student_id="S012",
            first_name=long_first,
            lastname=long_last,
            email="chris@university.edu",
            password="ChrisPass123!",
            year=2025,
        )

        assert student.full_name == f"{long_first} {long_last}"

    def test_full_name_property_reflects_mutations(self):
        """Verify full_name property updates when first/last names change."""
        student = Student(
            student_id="S013",
            first_name="Original",
            lastname="Name",
            email="original@university.edu",
            password="OriginalPass123!",
            year=2025,
        )

        assert student.full_name == "Original Name"

        student.first_name = "Updated"
        student.lastname = "Identity"
        assert student.full_name == "Updated Identity"


class TestStudentEquality:
    """Test suite for Student equality and comparison."""

    def test_student_equality_identical_students(self):
        """Verify two Student instances with same data are equal."""
        student1 = Student(
            student_id="S014",
            first_name="Elizabeth",
            lastname="Thompson",
            email="elizabeth.thompson@university.edu",
            password="ElizPass789!",
            year=2024,
        )
        student2 = Student(
            student_id="S014",
            first_name="Elizabeth",
            lastname="Thompson",
            email="elizabeth.thompson@university.edu",
            password="ElizPass789!",
            year=2024,
        )

        assert student1 == student2

    def test_student_inequality_different_student_ids(self):
        """Verify students with different IDs are not equal."""
        student1 = Student(
            student_id="S015",
            first_name="Jennifer",
            lastname="White",
            email="jennifer.white@university.edu",
            password="JennyPass456!",
            year=2025,
        )
        student2 = Student(
            student_id="S016",
            first_name="Jennifer",
            lastname="White",
            email="jennifer.white@university.edu",
            password="JennyPass456!",
            year=2025,
        )

        assert student1 != student2

    def test_student_inequality_different_emails(self):
        """Verify students with different emails are not equal."""
        student1 = Student(
            student_id="S017",
            first_name="William",
            lastname="Harris",
            email="william1@university.edu",
            password="WilliamPass789!",
            year=2025,
        )
        student2 = Student(
            student_id="S017",
            first_name="William",
            lastname="Harris",
            email="william2@university.edu",
            password="WilliamPass789!",
            year=2025,
        )

        assert student1 != student2

    def test_student_inequality_different_passwords(self):
        """Verify students with different passwords are not equal."""
        student1 = Student(
            student_id="S018",
            first_name="Daniel",
            lastname="Clark",
            email="daniel.clark@university.edu",
            password="DanPass123!",
            year=2025,
        )
        student2 = Student(
            student_id="S018",
            first_name="Daniel",
            lastname="Clark",
            email="daniel.clark@university.edu",
            password="NewDanPass456!",
            year=2025,
        )

        assert student1 != student2

    def test_student_inequality_different_years(self):
        """Verify students with different years are not equal."""
        student1 = Student(
            student_id="S019",
            first_name="Laura",
            lastname="Lewis",
            email="laura.lewis@university.edu",
            password="LauraPass789!",
            year=2023,
        )
        student2 = Student(
            student_id="S019",
            first_name="Laura",
            lastname="Lewis",
            email="laura.lewis@university.edu",
            password="LauraPass789!",
            year=2024,
        )

        assert student1 != student2


class TestStudentEmailFormat:
    """Test suite for email field handling."""

    def test_student_email_standard_format(self):
        """Verify Student accepts standard email format."""
        student = Student(
            student_id="S020",
            first_name="Patrick",
            lastname="Walker",
            email="patrick.walker@university.edu",
            password="PatrickPass123!",
            year=2025,
        )

        assert student.email == "patrick.walker@university.edu"

    def test_student_email_with_numbers(self):
        """Verify Student accepts email with numbers."""
        student = Student(
            student_id="S021",
            first_name="Nancy",
            lastname="Hall",
            email="nancy.hall2024@university.edu",
            password="NancyPass456!",
            year=2025,
        )

        assert student.email == "nancy.hall2024@university.edu"

    def test_student_email_various_domains(self):
        """Verify Student accepts emails from different domains."""
        emails = [
            "student@university.edu",
            "user@college.ac.uk",
            "learner@school.org",
            "scholar@institute.com",
        ]

        for email in emails:
            student = Student(
                student_id="S022",
                first_name="Test",
                lastname="User",
                email=email,
                password="TestPass123!",
                year=2025,
            )
            assert student.email == email


class TestStudentPasswordHandling:
    """Test suite for password field."""

    def test_student_password_complex(self):
        """Verify Student accepts complex passwords."""
        student = Student(
            student_id="S023",
            first_name="Kevin",
            lastname="Martin",
            email="kevin.martin@university.edu",
            password="C0mpl3x!P@ssw0rd#2025",
            year=2025,
        )

        assert student.password == "C0mpl3x!P@ssw0rd#2025"

    def test_student_password_simple(self):
        """Verify Student accepts simple passwords."""
        student = Student(
            student_id="S024",
            first_name="Sandra",
            lastname="Garcia",
            email="sandra.garcia@university.edu",
            password="password",
            year=2025,
        )

        assert student.password == "password"

    def test_student_password_long(self):
        """Verify Student accepts long passwords."""
        long_password = "A" * 100 + "1!@"
        student = Student(
            student_id="S025",
            first_name="Thomas",
            lastname="Rodriguez",
            email="thomas.rodriguez@university.edu",
            password=long_password,
            year=2025,
        )

        assert student.password == long_password


class TestStudentYearField:
    """Test suite for year field."""

    def test_student_year_numeric_string(self):
        """Verify Student accepts numeric year strings."""
        years = [2023, 2024, 2025, 2026]

        for year in years:
            student = Student(
                student_id="S026",
                first_name="Test",
                lastname="User",
                email="test@university.edu",
                password="TestPass123!",
                year=year,
            )
            assert student.year == year

    def test_student_year_custom_format(self):
        """Verify Student accepts custom year formats."""
        student = Student(
            student_id="S027",
            first_name="Grace",
            lastname="Lee",
            email="grace.lee@university.edu",
            password="GracePass123!",
            year="Year 2",
        )

        assert student.year == "Year 2"


class TestStudentDataIntegrity:
    """Test suite for data integrity and field types."""

    def test_student_id_is_string(self):
        """Verify student_id field is a string."""
        student = Student(
            student_id="S028",
            first_name="Ryan",
            lastname="Scott",
            email="ryan.scott@university.edu",
            password="RyanPass789!",
            year=2025,
        )

        assert isinstance(student.student_id, str)

    def test_first_name_is_string(self):
        """Verify first_name field is a string."""
        student = Student(
            student_id="S029",
            first_name="Michelle",
            lastname="Green",
            email="michelle.green@university.edu",
            password="MichellePass456!",
            year=2025,
        )

        assert isinstance(student.first_name, str)

    def test_lastname_is_string(self):
        """Verify lastname field is a string."""
        student = Student(
            student_id="S030",
            first_name="Brandon",
            lastname="Adams",
            email="brandon.adams@university.edu",
            password="BrandonPass123!",
            year=2025,
        )

        assert isinstance(student.lastname, str)

    def test_email_is_string(self):
        """Verify email field is a string."""
        student = Student(
            student_id="S031",
            first_name="Sophia",
            lastname="Nelson",
            email="sophia.nelson@university.edu",
            password="SophiaPass789!",
            year=2025,
        )

        assert isinstance(student.email, str)

    def test_password_is_string(self):
        """Verify password field is a string."""
        student = Student(
            student_id="S032",
            first_name="Joshua",
            lastname="Carter",
            email="joshua.carter@university.edu",
            password="JoshuaPass456!",
            year=2025,
        )

        assert isinstance(student.password, str)


class TestStudentRepr:
    """Test suite for Student string representation."""

    def test_student_has_repr(self):
        """Verify Student dataclass has a string representation."""
        student = Student(
            student_id="S034",
            first_name="Ethan",
            lastname="Perez",
            email="ethan.perez@university.edu",
            password="EthanPass789!",
            year=2025,
        )

        repr_str = repr(student)
        assert "Student" in repr_str

    def test_student_repr_includes_key_fields(self):
        """Verify Student repr includes significant fields."""
        student = Student(
            student_id="S035",
            first_name="Ava",
            lastname="Roberts",
            email="ava.roberts@university.edu",
            password="AvaPass456!",
            year=2025,
        )

        repr_str = repr(student)
        # Dataclass repr typically includes field names
        assert "student_id" in repr_str or "S035" in repr_str

    def test_student_repr_distinct_for_different_students(self):
        """Verify repr differs for different students."""
        student1 = Student(
            student_id="S036",
            first_name="Mason",
            lastname="Phillips",
            email="mason.phillips@university.edu",
            password="MasonPass123!",
            year=2025,
        )
        student2 = Student(
            student_id="S037",
            first_name="Isabella",
            lastname="Campbell",
            email="isabella.campbell@university.edu",
            password="IsabellaPass789!",
            year=2024,
        )

        assert repr(student1) != repr(student2)
