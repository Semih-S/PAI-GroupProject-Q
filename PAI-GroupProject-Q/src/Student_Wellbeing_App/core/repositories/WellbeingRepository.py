from src.Student_Wellbeing_App.core.models.WellbeingRecord import WellbeingRecord
from src.Student_Wellbeing_App.core.database.connection import get_db_connection

class WellbeingRepository:
    def save(self,w:WellbeingRecord):
        c=get_db_connection();
        x=c.cursor();
        x.execute("INSERT INTO wellbeing_record(record_id,student_id,week_start,stress_level,sleep_hours,source_type)VALUES(?,?,?,?,?,?)",
                  (w.record_id,w.student_id,w.week_start,w.stress_level,w.sleep_hours,w.source_type));
        x.close();
        c.close()

    def get_by_student(self,i:int):
        c=get_db_connection();
        x=c.cursor();
        x.execute("SELECT record_id,student_id,week_start,stress_level,sleep_hours,source_type FROM wellbeing_record WHERE student_id=?",(i,));
        r=x.fetchall();
        x.close();
        c.close();
        return [WellbeingRecord(a,b,c1,d,e,f) for a,b,c1,d,e,f in r]

    # def delete(self,i:int):
    #     c=get_db_connection();
    #     x=c.cursor();
    #     x.execute("DELETE FROM wellbeing_record WHERE record_id=?",(i,));
    #     x.close();
    #     c.close()