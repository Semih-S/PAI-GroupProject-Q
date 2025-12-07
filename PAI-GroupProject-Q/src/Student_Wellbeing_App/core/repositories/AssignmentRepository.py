# core/repositories/AssignmentRepository.py

import sqlite3
from pathlib import Path
from typing import List, Optional

from src.Student_Wellbeing_App.core.models.AssignmentRecord import AssignmentRecord

# Same pattern as your AttendanceRepository
DB_PATH = (
        Path(__file__).resolve().parents[2]
        / "database"
        / "student_wellbeing_db.sqlite3"
)


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


class AssignmentRepository:
    """
    Low-level DB access for assignment_records table.
    """

    def _row_to_model(self, row: sqlite3.Row) -> AssignmentRecord:
        return AssignmentRecord(
            assignment_record_id=row["assignment_record_id"],
            student_id=row["student_id"],
            assignment_id=row["assignment_id"],
            submitted=bool(row["submitted"]),
            submitted_date=row["submitted_date"],
            due_date=row["due_date"],
            mark=row["mark"],
            feedback=row["feedback"],
        )

    # ---------- CRUD ----------

    def save(self, record: AssignmentRecord) -> int:
        """
        Insert or update an AssignmentRecord.
        Returns the assignment_record_id.
        """
        with get_db_connection() as conn:
            cur = conn.cursor()

            if record.assignment_record_id == 0:
                cur.execute(
                    """
                    INSERT INTO assignment_records(
                        student_id,
                        assignment_id,
                        submitted,
                        submitted_date,
                        due_date,
                        mark,
                        feedback
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.student_id,
                        record.assignment_id,
                        int(record.submitted),
                        record.submitted_date,
                        record.due_date,
                        record.mark,
                        record.feedback,
                    ),
                )
                conn.commit()
                return cur.lastrowid
            else:
                cur.execute(
                    """
                    UPDATE assignment_records
                    SET
                        student_id = ?,
                        assignment_id = ?,
                        submitted = ?,
                        submitted_date = ?,
                        due_date = ?,
                        mark = ?,
                        feedback = ?
                    WHERE assignment_record_id = ?
                    """,
                    (
                        record.student_id,
                        record.assignment_id,
                        int(record.submitted),
                        record.submitted_date,
                        record.due_date,
                        record.mark,
                        record.feedback,
                        record.assignment_record_id,
                    ),
                )
                conn.commit()
                return record.assignment_record_id

    def get(self, assignment_record_id: int) -> Optional[AssignmentRecord]:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT *
                FROM assignment_records
                WHERE assignment_record_id = ?
                """,
                (assignment_record_id,),
            )
            row = cur.fetchone()
            return self._row_to_model(row) if row else None

    def get_by_student(self, student_id: str) -> List[AssignmentRecord]:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT *
                FROM assignment_records
                WHERE student_id = ?
                ORDER BY due_date ASC
                """,
                (student_id,),
            )
            return [self._row_to_model(r) for r in cur.fetchall()]

    def get_pending_by_student(self, student_id: str) -> List[AssignmentRecord]:
        """
        Assignments not yet submitted (submitted = 0).
        """
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT *
                FROM assignment_records
                WHERE student_id = ?
                  AND submitted = 0
                ORDER BY due_date ASC
                """,
                (student_id,),
            )
            return [self._row_to_model(r) for r in cur.fetchall()]

    def get_marked_by_student(self, student_id: str) -> List[AssignmentRecord]:
        """
        Assignments that have a mark.
        """
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT *
                FROM assignment_records
                WHERE student_id = ?
                  AND mark IS NOT NULL
                ORDER BY due_date ASC
                """,
                (student_id,),
            )
            return [self._row_to_model(r) for r in cur.fetchall()]
