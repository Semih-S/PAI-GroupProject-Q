from src.Student_Wellbeing_App.core.database.connection import get_db_connection
from datetime import datetime

class AuditRepository:
    def __init__(self):
        self._ensure_table_exists()

    def _ensure_table_exists(self):
        conn = get_db_connection()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                action TEXT,
                details TEXT, 
                timestamp DATETIME
            )
        """)
        conn.commit()
        conn.close()

    def log_action(self, user_id: str, action: str, details: str):
        """write an audit log entry"""
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO audit_log (user_id, action, details, timestamp) VALUES (?, ?, ?, ?)",
            (user_id, action, details, datetime.now())
        )
        conn.commit()
        conn.close()
        print(f"📝 [AUDIT] {user_id} performed {action}: {details}")

    def get_recent_logs(self, limit: int = 50):
        """Get recent audit logs"""
        conn = get_db_connection()
        conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
        cur = conn.cursor()
        cur.execute("SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        conn.close()
        return rows