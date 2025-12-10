import hashlib
from typing import List, Optional

from src.Student_Wellbeing_App.core.models.User import User
from src.Student_Wellbeing_App.core.models.UserRole import UserRole
from src.Student_Wellbeing_App.core.repositories.UserRepository import UserRepository


def _hash_password(plain_password: str) -> str:
    # Simple hash – in a real app you’d use bcrypt/argon2
    return hashlib.sha256(plain_password.encode()).hexdigest()


class UserService:
    def __init__(self, user_repository: Optional[UserRepository] = None):
        self.user_repository = user_repository or UserRepository()

    # ---------- Creation / registration ----------

    def create_user(
            self,
            first_name: str,
            lastname: str,
            plain_password: str,
            role: UserRole,
    ) -> str:
        password_hash = _hash_password(plain_password)

        user = User(
            user_id="",
            first_name=first_name,
            lastname=lastname,
            password_hash=password_hash,
            role=role,
        )
        return self.user_repository.create(user)

    # ---------- Queries for dashboards ----------

    def get_all_users(self) -> List[User]:
        return self.user_repository.get_all()

    def get_users_by_role(self, role: UserRole) -> List[User]:
        return self.user_repository.get_by_role(role)

    # ---------- Authentication helper (for AuthenticationService) ----------

    def verify_credentials(
            self, user_id: str, plain_password: str
    ) -> Optional[User]:
        user = self.user_repository.get_by_id(user_id)
        if user is None:
            return None

        if user.password_hash == _hash_password(plain_password):
            return user
        return None

    def has_admin(self) -> bool:
        return self.user_repository.has_admin()
