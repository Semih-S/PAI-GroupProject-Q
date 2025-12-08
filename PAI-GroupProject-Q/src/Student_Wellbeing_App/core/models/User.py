from dataclasses import dataclass
from src.Student_Wellbeing_App.core.models.UserRole import UserRole

@dataclass
class User:
    user_id: str
    first_name: str
    lastname: str
    password_hash: str
    role: UserRole

    def can_view_personal_wellbeing(self) -> bool:
        return self.role in {UserRole.WELLBEING_OFFICER, UserRole.ADMIN}