import hashlib
from typing import Optional, List

from src.Student_Wellbeing_App.core.models.Student import Student
from src.Student_Wellbeing_App.core.database.connection import get_db_connection


class StudentRepository:
    def _next_stu_id(self, cursor) -> str:
        """
        Generate the next STU-style student_id: STU0001, STU0002, ...
        """
        cursor.execute(
            "SELECT student_id FROM student WHERE student_id LIKE 'STU%' "
            "ORDER BY student_id DESC LIMIT 1"
        )
        row = cursor.fetchone()

        if row is None:
            return "STU0001"

        last_id = row[0]          # e.g. "STU0012"
        num_part = last_id[3:]    # "0012"
        try:
            last_num = int(num_part)
        except ValueError:
            last_num = 0

        return f"STU{last_num + 1:04d}"

    def save(self, s: Student) -> str:
        """
        Create a new student with a STUxxxx ID.
        Assumes s.password is already a hash when called from the service.
        Returns the generated student_id.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        student_id = self._next_stu_id(cursor)

        cursor.execute(
            """
            INSERT INTO student(student_id, first_name, lastname, email, password, year)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                student_id,
                s.first_name,
                s.lastname,
                s.email,
                s.password,   # should be hash
                s.year,
            ),
        )

        conn.commit()
        cursor.close()
        conn.close()

        s.student_id = student_id
        return student_id

    def list_all(self) -> List[Student]:
        """
        Return all students as Student objects.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT student_id, first_name, lastname, email, password, year FROM student"
        )
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return [
            Student(
                student_id=row[0],
                first_name=row[1],
                lastname=row[2],
                email=row[3],
                password=row[4],
                year=row[5],
            )
            for row in rows
        ]

    def delete(self, student_id: str) -> None:
        """
        Delete a student by STU-style ID.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM student WHERE student_id = ?", (student_id,))
        conn.commit()

        cursor.close()
        conn.close()

    def authenticate_by_id(self, student_id: str, password: str) -> Optional[Student]:
        """
        Authenticate a student by STUxxxx ID and password.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT student_id, first_name, lastname, email, password, year
            FROM student
            WHERE student_id = ?
            """,
            (student_id,),
        )
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if row is None:
            return None

        db_student_id, first_name, lastname, email, db_hash, year = row
        input_hash = hashlib.sha256(password.encode()).hexdigest()

        if input_hash != db_hash:
            return None

        return Student(
            student_id=db_student_id,
            first_name=first_name,
            lastname=lastname,
            email=email,
            password=db_hash,  # keep hash, never plain
            year=year,
        )

    def get_student_by_id(self, student_id: str) -> Optional[Student]:
        """
        Get a student by their student_id.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT student_id, first_name, lastname, email, password, year
            FROM student
            WHERE student_id = ?
            """,
            (student_id,),
        )
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if row is None:
            return None

        return Student(
            student_id=row[0],
            first_name=row[1],
            lastname=row[2],
            email=row[3],
            password=row[4],
            year=row[5],
        )