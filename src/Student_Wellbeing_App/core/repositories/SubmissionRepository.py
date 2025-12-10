from typing import List, Optional, Dict
from src.Student_Wellbeing_App.core.models.SubmissionRecord import SubmissionRecord
from src.Student_Wellbeing_App.core.models.SubmissionStatus import SubmissionStatus
from src.Student_Wellbeing_App.core.database.connection import get_db_connection

class SubmissionRepository:
    def upsert_grade(self, student_id: str, assessment_id: int, mark: float) -> int:
        """
        mark intelligently:
        - if submission exists for student & assessment -> UPDATE mark
        - else -> INSERT new submission with mark
        """
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT submission_id FROM submission WHERE student_id = ? AND assessment_id = ?",
                (student_id, assessment_id)
            )
            row = cur.fetchone()

            if row:
                # Update existing submission
                existing_id = row[0]
                cur.execute(
                    "UPDATE submission SET mark = ?, submitted_at = datetime('now') WHERE submission_id = ?",
                    (mark, existing_id)
                )
                conn.commit()
                print(f"[DB LOG] Updated Grade for Submission ID {existing_id} -> {mark}")
                return existing_id
            else:
                # Insert new submission
                cur.execute(
                    """
                    INSERT INTO submission (student_id, assessment_id, submitted_at, status, mark)
                    VALUES (?, ?, datetime('now'), 'SUBMITTED', ?)
                    """,
                    (student_id, assessment_id, mark)
                )
                conn.commit()
                new_id = cur.lastrowid or 0
                print(f"[DB LOG] Inserted New Grade Submission ID {new_id}")
                return new_id
        finally:
            cur.close()
            conn.close()

    # --- Data Editor ---
    
    def update_mark_by_id(self, submission_id: int, new_mark: float):
        """Directly update the mark of a submission by its ID"""
        conn = get_db_connection()
        try:
            conn.execute("UPDATE submission SET mark = ? WHERE submission_id = ?", (new_mark, submission_id))
            conn.commit()
            print(f"[DB LOG] Updated Mark for Submission ID {submission_id}")
        finally:
            conn.close()

    def delete_by_id(self, submission_id: int):
        """Delete a submission record by its ID"""
        conn = get_db_connection()
        try:
            conn.execute("DELETE FROM submission WHERE submission_id = ?", (submission_id,))
            conn.commit()
            print(f"[DB LOG] Deleted Submission ID {submission_id}")
        finally:
            conn.close()

    def get_by_assessment(self, assessment_id: int) -> List[dict]:
        """Get all submissions for a specific assessment"""
        conn = get_db_connection()
        cur = conn.cursor()
        # Here we return a list of dicts for easier JSON serialization
        cur.execute(
            "SELECT submission_id, student_id, mark, status FROM submission WHERE assessment_id = ?", 
            (assessment_id,)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [{"id": r[0], "student_id": r[1], "mark": r[2], "status": r[3]} for r in rows]

    # keep for legacy compatibility
    def save_legacy(self, student_id: str, assessment_id: int, mark: float) -> int:
        return self.upsert_grade(student_id, assessment_id, mark)
        
    def get_by_student(self, student_id: str) -> List[SubmissionRecord]:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT submission_id, student_id, assessment_id, submitted_at, status, mark FROM submission WHERE student_id=?", (student_id,))
        rows = cur.fetchall()
        conn.close()
        return [SubmissionRecord(r[0], r[1], r[2], r[3], SubmissionStatus(r[4] if r[4] in [s.value for s in SubmissionStatus] else 'SUBMITTED'), r[5]) for r in rows]