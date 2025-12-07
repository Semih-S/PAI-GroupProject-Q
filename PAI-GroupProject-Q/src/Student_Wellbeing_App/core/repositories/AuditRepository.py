from src.Student_Wellbeing_App.core.models.AuditLog import AuditLog
from src.Student_Wellbeing_App.core.database.connection import get_db_connection

class AuditRepository:
    def log(self,l:AuditLog):
        c=get_db_connection();
        x=c.cursor();
        x.execute("INSERT INTO audit_log(user_id,entity_type,entity_id,action_type,timestamp,details)VALUES(?,?,?,?,?,?)",
                  (l.user_id,l.entity_type,l.entity_id,l.action_type,l.timestamp,l.details));
        x.close();
        c.close()