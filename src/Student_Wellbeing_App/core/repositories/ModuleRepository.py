from typing import List
from src.Student_Wellbeing_App.core.database.connection import get_db_connection
from src.Student_Wellbeing_App.core.models.Module import Module

class ModuleRepository:
    # --- Module CRUD ---
    def create_module(self, code: str, title: str):
        conn = get_db_connection()
        try:
            conn.execute("INSERT OR IGNORE INTO module (module_code, title) VALUES (?, ?)", (code, title))
            conn.commit()
        finally:
            conn.close()

    def get_all_modules(self) -> List[Module]:
        # Get all modules in the system
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT module_code, title FROM module")
        rows = cur.fetchall()
        conn.close()
        # transform to List[Module]
        return [Module(module_code=r[0], title=r[1]) for r in rows]

    def get_module_by_code(self, code: str) -> Module:
        # Get module by its code
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT module_code, title FROM module WHERE module_code = ?", (code,))
        row = cur.fetchone()
        conn.close()
        if row:
            return Module(module_code=row[0], title=row[1])
        return None

    # --- Teaching Assignment (Teacher <-> Module) ---
    def assign_teacher(self, user_id: str, module_code: str):
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO teaching_assignment (user_id, module_code) VALUES (?, ?)", (user_id, module_code))
            conn.commit()
        finally:
            conn.close()

    def get_modules_by_teacher(self, user_id: str) -> List[str]:
        # return list of module_codes taught by the teacher
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT module_code FROM teaching_assignment WHERE user_id = ?", (user_id,))
        rows = cur.fetchall()
        conn.close()
        return [r[0] for r in rows]

    # --- Enrollment (Student <-> Module) ---
    def enroll_student(self, student_id: str, module_code: str):
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO enrollment (student_id, module_code) VALUES (?, ?)", (student_id, module_code))
            conn.commit()
        finally:
            conn.close()

    def get_students_by_module(self, module_code: str) -> List[str]:
        # return list of student_ids enrolled in the module
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT student_id FROM enrollment WHERE module_code = ?", (module_code,))
        rows = cur.fetchall()
        conn.close()
        return [r[0] for r in rows]