import hashlib
from typing import List, Optional

from src.Student_Wellbeing_App.core.models.User import User
from src.Student_Wellbeing_App.core.models.UserRole import UserRole
from src.Student_Wellbeing_App.core.database.connection import get_db_connection


class UserRepository:
    def __init__(self):
        self._conn = get_db_connection()


    def _next_emp_id(self, cursor) -> str:
        """
        Generate the next EMP-style user_id: EMP0001, EMP0002, ...
        """
        cursor.execute(
            "SELECT user_id FROM user WHERE user_id LIKE 'EMP%' ORDER BY user_id DESC LIMIT 1"
        )
        row = cursor.fetchone()

        if row is None:
            return "EMP0001"

        last_id = row[0]          # e.g. "EMP0012"
        num_part = last_id[3:]    # "0012"
        try:
            last_num = int(num_part)
        except ValueError:
            last_num = 0

        return f"EMP{last_num + 1:04d}"

    # ---------- Creation ----------

    def create(self, user: User) -> str:
        cur = self._conn.cursor()
        user_id = self._next_emp_id(cur)

        cur.execute(
            """
            INSERT INTO user (user_id, first_name, lastname, password_hash, role)
            VALUES (?, ?, ?, ?, ?);
            """,
            (
                user_id,
                user.first_name,
                user.lastname,
                user.password_hash,
                user.role.name,
            ),
        )
        self._conn.commit()
        return user_id

    # ---------- Queries ----------

    def has_admin(self) -> bool:
        cur = self._conn.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM user WHERE role = ? LIMIT 1;",
            (UserRole.ADMIN.name,),
        )
        return cur.fetchone() is not None

    def get_by_id(self, user_id: str) -> Optional[User]:
        cur = self._conn.cursor()
        cur.execute(
            """
            SELECT user_id, first_name, lastname, password_hash, role
            FROM user
            WHERE user_id = ?;
            """,
            (user_id,),
        )
        row = cur.fetchone()
        if row is None:
            return None

        return User(
            user_id=row["user_id"],
            first_name=row["first_name"],
            lastname=row["lastname"],
            password_hash=row["password_hash"],
            role=UserRole[row["role"]],
        )

    def get_all(self) -> List[User]:
        cur = self._conn.cursor()
        cur.execute(
            """
            SELECT user_id, first_name, lastname, password_hash, role
            FROM user
            ORDER BY first_name, lastname;
            """
        )
        rows = cur.fetchall()

        return [
            User(
                user_id=row["user_id"],
                first_name=row["first_name"],
                lastname=row["lastname"],
                password_hash=row["password_hash"],
                role=UserRole[row["role"]],
            )
            for row in rows
        ]

    def get_by_role(self, role: UserRole) -> List[User]:
        cur = self._conn.cursor()
        cur.execute(
            """
            SELECT user_id, first_name, lastname, password_hash, role
            FROM user
            WHERE role = ?
            ORDER BY first_name, lastname;
            """,
            (role.name,),
        )
        rows = cur.fetchall()

        return [
            User(
                user_id=row["user_id"],
                first_name=row["first_name"],
                lastname=row["lastname"],
                password_hash=row["password_hash"],
                role=UserRole[row["role"]],
            )
            for row in rows
        ]

    def authenticate_by_id(self, user_id: int, password: str) -> Optional[User]:
        """
        Authenticate a system user by user_id + password.
        Assumes password_hash is stored in the DB (SHA-256).
        """
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT user_id, first_name, lastname, password_hash, role
            FROM user
            WHERE user_id = ?
            """,
            (user_id,),
        )
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row is None:
            return None

        db_user_id, first_name, lastname, db_hash, role_str = row
        input_hash = hashlib.sha256(password.encode()).hexdigest()

        if input_hash != db_hash:
            return None

        return User(
            user_id=db_user_id,
            first_name=first_name,
            lastname=lastname,
            password_hash=db_hash,
            role=UserRole(role_str),
        )