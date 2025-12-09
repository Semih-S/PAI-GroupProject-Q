from typing import Dict, List, Optional, Any
from datetime import date

# Repositories
from src.Student_Wellbeing_App.core.repositories.StudentRepository import StudentRepository
from src.Student_Wellbeing_App.core.repositories.AlertRepository import AlertRepository
from src.Student_Wellbeing_App.core.repositories.AttendanceRepository import AttendanceRepository
from src.Student_Wellbeing_App.core.repositories.WellbeingRepository import WellbeingRepository
from src.Student_Wellbeing_App.core.repositories.AssessmentRepository import AssessmentRepository
from src.Student_Wellbeing_App.core.repositories.SubmissionRepository import SubmissionRepository
from src.Student_Wellbeing_App.core.repositories.ModuleRepository import ModuleRepository
from src.Student_Wellbeing_App.core.services.AuditService import AuditService

from src.Student_Wellbeing_App.core.models.AttendanceStatus import AttendanceStatus
from src.Student_Wellbeing_App.core.models.Assessment import Assessment

class DashboardService:
    def __init__(self):
        self.student_repo = StudentRepository()
        self.alert_repo = AlertRepository()
        self.attendance_repo = AttendanceRepository()
        self.wellbeing_repo = WellbeingRepository()
        self.assessment_repo = AssessmentRepository()
        self.submission_repo = SubmissionRepository()
        self.module_repo = ModuleRepository()
        self.audit = AuditService()

    # --- Course Management ---
    def create_new_module(self, code, title, performed_by="ADMIN"):
        self.module_repo.create_module(code, title)
        self.audit.log(performed_by, "CREATE_MODULE", f"Created {code}: {title}")

    def assign_teacher_to_module(self, tid, code, performed_by="ADMIN"):
        self.module_repo.assign_teacher(tid, code)
        self.audit.log(performed_by, "ASSIGN_TEACHER", f"Assigned {tid} to {code}")

    def enroll_student_to_module(self, sid, code, performed_by="ADMIN"):
        self.module_repo.enroll_student(sid, code)
        self.audit.log(performed_by, "ENROLL_STUDENT", f"Enrolled {sid} in {code}")

    def get_teacher_modules(self, tid): return self.module_repo.get_modules_by_teacher(tid)

    def get_enrolled_students(self, code): return self.module_repo.get_students_by_module(code)

    # --- Assessments & Grades ---
    
    def create_assessment(self, module_code, title, due_date, weight, performed_by="TEACHER"):
        a = Assessment(0, module_code, title, due_date, weight)
        new_id = self.assessment_repo.save(a)
        self.audit.log(performed_by, "CREATE_ASSESSMENT", f"Created {title} for {module_code}")
        return new_id

    def get_module_assessments(self, module_code: str):
        return self.assessment_repo.get_by_module(module_code)

    def get_assessment_grades(self, assessment_id: int) -> List[Dict]:
        return self.submission_repo.get_by_assessment(assessment_id)

    # added methods for editing grades directly
    def submit_grade(self, student_id, assessment_id, mark, performed_by="TEACHER"):
        self.submission_repo.upsert_grade(student_id, assessment_id, mark)
        self.audit.log(performed_by, "SUBMIT_GRADE", f"Graded {student_id} on Assmt {assessment_id}: {mark}")

    def update_grade_direct(self, submission_id: int, mark: float, performed_by="TEACHER"):
        self.submission_repo.update_mark_by_id(submission_id, mark)
        self.audit.log(performed_by, "UPDATE_GRADE", f"Updated Submission {submission_id} mark to {mark}")

    def delete_grade_entry(self, submission_id: int, performed_by="TEACHER"):
        self.submission_repo.delete_by_id(submission_id)
        self.audit.log(performed_by, "DELETE_GRADE", f"Deleted Submission {submission_id}")

    # --- Stats (No changes) ---
    def get_admin_stats(self):
        return {"total_students": len(self.student_repo.list_all()), "active_alerts": len(self.alert_repo.list_active())}

    def calculate_attendance_rate(self, sid):
        records = self.attendance_repo.get_by_student(sid)
        if not records: return 100.0
        total = len(records)
        absences = sum(1 for r in records if r.status == AttendanceStatus.ABSENT)
        return round(((total - absences) / total) * 100, 1)

    def get_student_wellbeing_trend(self, sid):
        records = self.wellbeing_repo.get_by_student(sid)
        records.sort(key=lambda r: r.week_start)
        return {"dates": [r.week_start for r in records], "stress": [r.stress_level for r in records], "sleep": [r.sleep_hours for r in records]}

    def get_module_attendance_records(self, session_id):
        records = self.attendance_repo.get_by_session(session_id)
        return [{"id": r.attendance_id, "student_id": r.student_id, "date": r.session_date, "status": r.status.value} for r in records]

    def get_module_stats(self, session_id):
        records = self.attendance_repo.get_by_session(session_id)
        if not records: return {"avg_attendance": 0.0, "total_sessions": 0, "absent_count": 0}
        total = len(records)
        absences = sum(1 for r in records if r.status == AttendanceStatus.ABSENT)
        return {"avg_attendance": round(((total - absences) / total) * 100, 1), "total_sessions": total, "absent_count": absences}

    def generate_plain_text_report(self):
        return f"System Status: {len(self.student_repo.list_all())} Students."