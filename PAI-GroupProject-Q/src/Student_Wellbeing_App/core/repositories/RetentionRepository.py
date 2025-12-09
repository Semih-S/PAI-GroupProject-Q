from typing import List, Dict, Any
from src.Student_Wellbeing_App.core.models.RetentionRule import RetentionRule
from src.Student_Wellbeing_App.core.database.connection import get_db_connection
import datetime

class RetentionRepository:
    def init_default_rules(self):
        conn = get_db_connection()
        conn.execute("INSERT OR IGNORE INTO retention_rule (rule_id, data_type, retention_months, is_active) VALUES (1, 'RESOLVED_ALERTS', 12, 1)")
        conn.execute("INSERT OR IGNORE INTO retention_rule (rule_id, data_type, retention_months, is_active) VALUES (2, 'GRADUATED_STUDENTS', 48, 1)")
        conn.commit()
        conn.close()

    def get_rules(self) -> List[RetentionRule]:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT rule_id, data_type, retention_months, is_active FROM retention_rule")
        rows = cur.fetchall()
        conn.close()
        return [RetentionRule(*r) for r in rows]

    def get_rule_by_id(self, rule_id: int) -> RetentionRule:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT rule_id, data_type, retention_months, is_active FROM retention_rule WHERE rule_id=?", (rule_id,))
        row = cur.fetchone()
        conn.close()
        if row:
            return RetentionRule(*row)
        return None

    # --- CRUD ---
    
    def add_rule(self, data_type: str, months: int, is_active: int):
        conn = get_db_connection()
        conn.execute("INSERT INTO retention_rule (data_type, retention_months, is_active) VALUES (?, ?, ?)", 
                     (data_type, months, is_active))
        conn.commit()
        conn.close()

    def update_rule(self, rule_id: int, months: int, is_active: bool):
        conn = get_db_connection()
        conn.execute("UPDATE retention_rule SET retention_months = ?, is_active = ? WHERE rule_id = ?", (months, int(is_active), rule_id))
        conn.commit()
        conn.close()

    def delete_rule(self, rule_id: int):
        conn = get_db_connection()
        conn.execute("DELETE FROM retention_rule WHERE rule_id = ?", (rule_id,))
        conn.commit()
        conn.close()

    # --- Preview Logic ---

    def preview_old_alerts(self, months: int) -> List[Dict[str, Any]]:
        """ preview alerts that will be deleted """
        conn = get_db_connection()
        conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r)) 
        cur = conn.cursor()
        
        query = f"SELECT * FROM alert WHERE resolved = 1 AND created_at < date('now', '-{months} months')"
        cur.execute(query)
        rows = cur.fetchall()
        conn.close()
        return rows

    def preview_graduated_students(self, months: int) -> List[Dict[str, Any]]:
        """preview students eligible for graduation cleanup"""
        total_months = 36 + months # assuming a 3-year program
        current_year = datetime.date.today().year
        cutoff_year = current_year - (total_months // 12)
        
        conn = get_db_connection()
        conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM student WHERE year < ?", (cutoff_year,))
        rows = cur.fetchall()
        conn.close()
        return rows

    # --- Execute Logic ---

    def cleanup_old_alerts(self, months: int) -> int:
        conn = get_db_connection()
        query = f"DELETE FROM alert WHERE resolved = 1 AND created_at < date('now', '-{months} months')"
        cur = conn.execute(query)
        count = cur.rowcount
        conn.commit()
        conn.close()
        return count

    def cleanup_graduated_students(self, months: int) -> int:
        total_months = 36 + months
        current_year = datetime.date.today().year
        cutoff_year = current_year - (total_months // 12)
        
        conn = get_db_connection()
        cur = conn.cursor()
        # 1. Check ID
        cur.execute("SELECT student_id FROM student WHERE year < ?", (cutoff_year,))
        students = [row[0] for row in cur.fetchall()]
        
        if not students:
            conn.close()
            return 0
            
        # 2. Delete related records
        placeholders = ','.join('?' for _ in students)
        tables = ['attendance', 'submission', 'wellbeing_record', 'alert', 'enrollment']
        for table in tables:
            conn.execute(f"DELETE FROM {table} WHERE student_id IN ({placeholders})", students)
        conn.execute(f"DELETE FROM student WHERE student_id IN ({placeholders})", students)
        
        conn.commit()
        conn.close()
        return len(students)