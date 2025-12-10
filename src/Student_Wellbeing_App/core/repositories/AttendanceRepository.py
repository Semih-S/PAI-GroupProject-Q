# src/Student_Wellbeing_App/core/repositories/AttendanceRepository.py

from typing import List, Optional
from src.Student_Wellbeing_App.core.models.AttendanceRecord import AttendanceRecord
from src.Student_Wellbeing_App.core.database.connection import get_db_connection
from src.Student_Wellbeing_App.core.models.AttendanceStatus import AttendanceStatus

class AttendanceRepository:
    def upsert(self, a: AttendanceRecord) -> int:
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            # 1. check if record exists
            cur.execute("SELECT attendance_id FROM attendance WHERE student_id=? AND session_date=? AND session_id=?", 
                        (a.student_id, a.session_date, a.session_id))
            row = cur.fetchone()
            
            if row:
                # 2. if exist -> UPDATE
                cur.execute("UPDATE attendance SET status=? WHERE attendance_id=?", (a.status.value, row[0]))
                conn.commit()
                return row[0]
            else:
                # 3. if did not exist -> INSERT
                cur.execute("INSERT INTO attendance(student_id, session_date, session_id, status) VALUES(?, ?, ?, ?)", 
                            (a.student_id, a.session_date, a.session_id, a.status.value))
                conn.commit()
                return cur.lastrowid or 0
        finally:
            conn.close()

    # update attendance status by attendance_id
    def update_status_by_id(self, attendance_id: int, new_status: str):
        conn = get_db_connection()
        try:
            conn.execute(
                "UPDATE attendance SET status = ? WHERE attendance_id = ?",
                (new_status, attendance_id)
            )
            conn.commit()
            print(f"[DB LOG] Updated Status for ID {attendance_id} to {new_status}")
        except Exception as e:
            print(f"[DB ERROR] Update failed: {e}")
            raise e
        finally:
            conn.close()

    # delete attendance record by attendance_id
    def delete_by_id(self, attendance_id: int):
        conn = get_db_connection()
        try:
            # insure attendance_id is an integer
            id_val = int(attendance_id)
            
            print(f"👉 [REPO] Attempting to DELETE attendance_id: {id_val}")
            
            cursor = conn.cursor()
            cursor.execute("DELETE FROM attendance WHERE attendance_id = ?", (id_val,))
            
            # check how many rows were affected
            deleted_count = cursor.rowcount
            conn.commit() # <--- use conn.commit() to persist changes
            
            print(f"✅ [REPO] Committed! Rows affected: {deleted_count}")
            
        except Exception as e:
            print(f"❌ [REPO] Delete failed: {e}")
            raise e
        finally:
            conn.close()

    #  get attendance record by attendance_id
    def get_by_student(self, student_id: str) -> List[AttendanceRecord]:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT attendance_id, student_id, session_date, session_id, status FROM attendance WHERE student_id = ?",
            (student_id,),
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [AttendanceRecord(r[0], r[1], r[2], r[3], AttendanceStatus(r[4])) for r in rows]

    #  get attendance records by session_id
    def get_by_session(self, session_id: str) -> List[AttendanceRecord]:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT attendance_id, student_id, session_date, session_id, status FROM attendance WHERE session_id = ?",
            (session_id,),
        )
        rows = cur.fetchall()
        cur.close()
        return [AttendanceRecord(r[0], r[1], r[2], r[3], AttendanceStatus(r[4])) for r in rows]