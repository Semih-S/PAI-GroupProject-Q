from src.Student_Wellbeing_App.core.models.Alert import Alert
from src.Student_Wellbeing_App.core.database.connection import get_db_connection


class AlertRepository:
    def save(self, a: Alert):
        con = get_db_connection();
        curs = con.cursor();
        curs.execute("INSERT INTO alert(student_id,alert_type,reason,created_at,resolved)VALUES(%s,%s,%s,%s,%s)",
                     (a.student_id, a.alert_type, a.reason, a.created_at, a.resolved))
        curs.close()
        con.close()

    def list_active(self):
        con = get_db_connection()
        curs = con.cursor()
        curs.execute(
            "SELECT alert_id,student_id,alert_type,reason,created_at,resolved FROM alert WHERE resolved=false")
        r = curs.fetchall()
        curs.close()
        con.close()
        return [Alert(*a) for a in r]

    def resolve(self, i: int):
        con = get_db_connection()
        curs = con.cursor()
        curs.execute("UPDATE alert SET resolved=true WHERE alert_id=%s", (i,))
        curs.close()
        con.close()
