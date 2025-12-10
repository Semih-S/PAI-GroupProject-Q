from src.Student_Wellbeing_App.core.models.Alert import Alert
from src.Student_Wellbeing_App.core.models.AlertType import AlertType
from src.Student_Wellbeing_App.core.database.connection import get_db_connection

class AlertRepository:
    def save(self, a: Alert) -> int:
        con = get_db_connection()
        curs = con.cursor()
        curs.execute(
            "INSERT INTO alert(student_id, alert_type, reason, created_at, resolved) VALUES(?, ?, ?, ?, ?)",
            (a.student_id, a.alert_type, a.reason, a.created_at, int(a.resolved))
        )
        con.commit()
        new_id = curs.lastrowid
        curs.close()
        con.close()
        return new_id

    def list_active(self):
        """Fetch unresolved alerts (resolved = 0)"""
        con = get_db_connection()
        curs = con.cursor()
        curs.execute(
            "SELECT alert_id, student_id, alert_type, reason, created_at, resolved FROM alert WHERE resolved=0"
        )
        r = curs.fetchall()
        curs.close()
        con.close()
        # Convert rows to Alert objects
        return [Alert(row[0], row[1], row[2], row[3], row[4], bool(row[5])) for row in r]

    def list_resolved(self):
        """Fetch resolved alerts history (resolved = 1)"""
        con = get_db_connection()
        curs = con.cursor()
        curs.execute(
            "SELECT alert_id, student_id, alert_type, reason, created_at, resolved FROM alert WHERE resolved=1 ORDER BY created_at DESC"
        )
        r = curs.fetchall()
        curs.close()
        con.close()
        return [Alert(row[0], row[1], row[2], row[3], row[4], bool(row[5])) for row in r]

    def resolve(self, i: int):
        con = get_db_connection()
        curs = con.cursor()
        try:
            curs.execute("UPDATE alert SET resolved=1 WHERE alert_id=?", (i,))
            con.commit() # added commit to save changes
            print(f"[DB LOG] Resolved Alert ID {i}")
        except Exception as e:
            print(f"[DB ERROR] Failed to resolve alert {i}: {e}")
        finally:
            curs.close()
            con.close()