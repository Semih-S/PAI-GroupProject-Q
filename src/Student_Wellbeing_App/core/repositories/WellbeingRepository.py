from typing import List, Optional
from datetime import date
from src.Student_Wellbeing_App.core.models.WellbeingRecord import WellbeingRecord
from src.Student_Wellbeing_App.core.database.connection import get_db_connection

class WellbeingRepository:
    def upsert(self, w: WellbeingRecord) -> int:
        """
        Smart Insert/Update based on Student ID + Week Start Date.
        If a record exists for this student on this week_start, update it.
        Otherwise, insert a new one.
        """
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            # 1. Check if record exists for this week
            cur.execute(
                """
                SELECT record_id 
                FROM wellbeing_record 
                WHERE student_id = ? AND week_start = ?
                """,
                (w.student_id, w.week_start)
            )
            row = cur.fetchone()
            
            if row:
                # [Update]
                existing_id = row[0]
                cur.execute(
                    """
                    UPDATE wellbeing_record 
                    SET stress_level = ?, sleep_hours = ? 
                    WHERE record_id = ?
                    """,
                    (w.stress_level, w.sleep_hours, existing_id)
                )
                conn.commit()
                print(f"[DB LOG] Updated Wellbeing ID {existing_id}")
                return existing_id
            else:
                # [Insert]
                cur.execute(
                    """
                    INSERT INTO wellbeing_record(
                        student_id, week_start, stress_level, sleep_hours, source_type
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (w.student_id, w.week_start, w.stress_level, w.sleep_hours, w.source_type)
                )
                conn.commit()
                new_id = cur.lastrowid or 0
                print(f"[DB LOG] Inserted New Wellbeing ID {new_id}")
                return new_id
                
        except Exception as e:
            print(f"[DB ERROR] Upsert failed: {e}")
            raise e
        finally:
            cur.close()
            conn.close()

    def update_by_id(self, record_id: int, stress: int, sleep: float):
        """Direct update from data editor"""
        conn = get_db_connection()
        try:
            conn.execute(
                "UPDATE wellbeing_record SET stress_level = ?, sleep_hours = ? WHERE record_id = ?",
                (stress, sleep, record_id)
            )
            conn.commit()
        finally:
            conn.close()

    def delete_by_id(self, record_id: int):
        """Direct delete"""
        conn = get_db_connection()
        try:
            conn.execute("DELETE FROM wellbeing_record WHERE record_id = ?", (record_id,))
            conn.commit()
            print(f"[DB LOG] Deleted Wellbeing ID {record_id}")
        finally:
            conn.close()

    def get_by_student(self, student_id: str) -> List[WellbeingRecord]:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            """
            SELECT record_id, student_id, week_start, stress_level, sleep_hours, source_type 
            FROM wellbeing_record 
            WHERE student_id = ?
            ORDER BY week_start DESC
            """, 
            (student_id,)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        return [
            WellbeingRecord(
                record_id=r[0],
                student_id=r[1],
                week_start=r[2], 
                stress_level=r[3],
                sleep_hours=r[4],
                source_type=r[5]
            ) 
            for r in rows
        ]