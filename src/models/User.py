from dataclasses import dataclass

from .UserRole import UserRole


@dataclass
class User:
    user_id: str
    first_name: str
    last_name: str
    password_hash: str
    role: UserRole


    def can_view_personal_wellbeing(self) -> bool:
        return self.role in {UserRole.WELLBEING_OFFICER, UserRole.ADMIN}
