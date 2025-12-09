from typing import List
from src.Student_Wellbeing_App.core.models.Assessment import Assessment
from src.Student_Wellbeing_App.core.database.connection import get_db_connection

class AssessmentRepository:
    def save(self, a: Assessment) -> int:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO assessment (module_code, title, due_date, weight) VALUES (?, ?, ?, ?)",
            (a.module_code, a.title, a.due_date, a.weight)
        )
        new_id = cur.lastrowid
        conn.commit()
        cur.close()
        conn.close()
        return new_id

    def get_by_module(self, module_code: str) -> List[Assessment]:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT assessment_id, module_code, title, due_date, weight FROM assessment WHERE module_code = ?",
            (module_code,)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [Assessment(r[0], r[1], r[2], r[3], r[4]) for r in rows]