from src.Student_Wellbeing_App.core.models.AttendanceRecord import AttendanceRecord
from src.Student_Wellbeing_App.core.database.connection import get_db_connection
from src.Student_Wellbeing_App.core.models.AttendanceStatus import AttendanceStatus


class AttendanceRepository:
    def save(self, a: AttendanceRecord) -> int:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO attendance (
                attendance_id,
                student_id,
                session_date,
                session_id,
                status
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                a.attendance_id,
                a.student_id,
                a.session_date,
                a.session_id,
                a.status.value,
            ),
        )
        new_id = cur.lastrowid
        conn.commit()
        cur.close()
        conn.close()
        return new_id

    def get_by_student(self, i: int) -> list[AttendanceRecord]:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT attendance_id, student_id, session_date, session_id, status
            FROM attendance
            WHERE student_id = ?
            """,
            (i,),
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()

        return [
            AttendanceRecord(
                attendance_id=a,
                student_id=b,
                session_date=c1,
                session_id=d,
                status=AttendanceStatus(e),
            )
            for a, b, c1, d, e in rows
        ]

    def delete(self, i: int) -> None:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM attendance WHERE attendance_id = ?", (i,))
        conn.commit()
        cur.close()
        conn.close()
