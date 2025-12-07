# src/Student_Wellbeing_App/core/repositories/SubmissionRepository.py

from src.Student_Wellbeing_App.core.models.SubmissionRecord import SubmissionRecord
from src.Student_Wellbeing_App.core.database.connection import get_db_connection
from src.Student_Wellbeing_App.core.models.SubmissionStatus import SubmissionStatus


class SubmissionRepository:
    def save(self, a: SubmissionRecord) -> int:
        """
        Persist a submission record.

        Expected fields on SubmissionRecord:
          - submission_id
          - student_id
          - assessment_id
          - submitted_at
          - status (SubmissionStatus)
          - mark  (float/int)
        """
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO submission (
                submission_id,
                student_id,
                assessment_id,
                submitted_at,
                status,
                mark
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                a.submission_id,
                a.student_id,
                a.assessment_id,
                a.submitted_at,
                a.status.value,
                a.mark,
            ),
        )

        new_id = cur.lastrowid
        conn.commit()
        cur.close()
        conn.close()
        return new_id

    def get_by_student(self, student_id: int) -> list[SubmissionRecord]:
        """
        Return all submissions for a given student_id.
        """
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                submission_id,
                student_id,
                assessment_id,
                submitted_at,
                status,
                mark
            FROM submission
            WHERE student_id = ?
            """,
            (student_id,),
        )

        rows = cur.fetchall()
        cur.close()
        conn.close()

        records: list[SubmissionRecord] = []
        for (
                submission_id,
                sid,
                assessment_id,
                submitted_at,
                status,
                mark,
        ) in rows:
            records.append(
                SubmissionRecord(
                    submission_id=submission_id,
                    student_id=sid,
                    assessment_id=assessment_id,
                    submitted_at=submitted_at,
                    status=SubmissionStatus(status),
                    mark=mark,
                )
            )

        return records

    def delete(self, submission_id: int) -> None:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM submission WHERE submission_id = ?", (submission_id,))
        conn.commit()
        cur.close()
        conn.close()
