# core/services/AuthenticationService.py

from dataclasses import dataclass
from typing import Optional, Literal, Union

from src.Student_Wellbeing_App.core.models.User import User
from src.Student_Wellbeing_App.core.models.Student import Student
from src.Student_Wellbeing_App.core.repositories.UserRepository import UserRepository
from src.Student_Wellbeing_App.core.repositories.StudentRepository import StudentRepository

AuthKind = Literal["user", "student"]


@dataclass
class AuthResult:
    kind: AuthKind                  # "user" or "student"
    principal: Union[User, Student] # the actual object


class AuthenticationService:
    """
    High-level authentication façade using ID patterns:
    - EMPxxxx → system users
    - STUxxxx (or any 'ST' prefix) → students
    """

    def __init__(
            self,
            user_repo: Optional[UserRepository] = None,
            student_repo: Optional[StudentRepository] = None,
    ):
        self.user_repo = user_repo or UserRepository()
        self.student_repo = student_repo or StudentRepository()

    def authenticate_user(self, user_id: str, password: str) -> Optional[User]:
        """Explicitly authenticate a system user by EMP-style user_id."""
        return self.user_repo.authenticate_by_id(user_id, password)

    def authenticate_student(self, student_id: str, password: str) -> Optional[Student]:
        """Explicitly authenticate a student by STU-style student_id."""
        return self.student_repo.authenticate_by_id(student_id, password)

    def authenticate_any(self, identifier: str, password: str) -> Optional[AuthResult]:

        code = identifier.strip().upper()

        # System user IDs: EMP0001, EMP0002, ...
        if code.startswith("EMP"):
            user = self.user_repo.authenticate_by_id(code, password)
            if user is not None:
                return AuthResult(kind="user", principal=user)
            return None

        # Student IDs: STU0001, STU0002, ... (or any 'ST' prefix)
        if code.startswith("ST"):
            student = self.student_repo.authenticate_by_id(code, password)
            if student is not None:
                return AuthResult(kind="student", principal=student)
            return None

        # Unknown prefix – you could optionally try both here, but for now we fail fast
        return None
