import hashlib
import re
from datetime import datetime
from typing import Optional, List

from src.Student_Wellbeing_App.core.models.Student import Student
from src.Student_Wellbeing_App.core.repositories.StudentRepository import StudentRepository


class StudentService:
    """High-level operations related to students."""

    def __init__(self, repo: Optional[StudentRepository] = None):
        self.repo = repo or StudentRepository()

    def register_student(
            self,
            first_name: str,
            last_name: str,
            email: str,
            password: str,
            cohort_year: int,
    ) -> str:
        """
        Validate input, hash password, create Student domain object,
        and persist via repository.

        Returns the generated STUxxxx student_id.
        """
        if not first_name.strip() or not last_name.strip():
            raise ValueError("Name fields cannot be empty.")

        email = email.strip().lower()
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            raise ValueError("Invalid email format.")

        current_year = datetime.utcnow().year
        if cohort_year < 2000 or cohort_year > current_year + 1:
            raise ValueError("Cohort year is outside a sensible range.")

        # Hash the password before persisting
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        student = Student(
            student_id="",                               # will be set by repo (e.g. STU0001)
            first_name=first_name.strip().title(),
            lastname=last_name.strip().title(),
            email=email,
            password=password_hash,                      # store hash, not plain password
            year=cohort_year,
        )

        return self.repo.save(student)

    def list_students(self) -> List[Student]:
        """Return all students."""
        return self.repo.list_all()

    def remove_student(self, student_id: str) -> None:
        """Remove a student by STUxxxx ID."""
        self.repo.delete(student_id)

    def get_student_by_id(self, student_id):
        """Get student by ID."""
        return self.repo.get_student_by_id(student_id)