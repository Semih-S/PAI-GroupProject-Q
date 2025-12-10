from typing import List, Optional
from src.Student_Wellbeing_App.core.models.AttendanceRecord import AttendanceRecord
from src.Student_Wellbeing_App.core.models.AttendanceStatus import AttendanceStatus
from src.Student_Wellbeing_App.core.repositories.AttendanceRepository import AttendanceRepository
from src.Student_Wellbeing_App.core.services.AuditService import AuditService

class AttendanceService:
    def __init__(self, repo: Optional[AttendanceRepository] = None):
        self.repo = repo or AttendanceRepository()
        self.audit = AuditService()

    def record_attendance(self, student_id: str, session_date, session_id: str, status: AttendanceStatus, performed_by: str = "UNKNOWN") -> int:
        record = AttendanceRecord(0, student_id, session_date, session_id, status)
        new_id = self.repo.upsert(record)
        self.audit.log(performed_by, "UPSERT_ATTENDANCE", f"Recorded {status.value} for {student_id} in {session_id}")
        return new_id

    def update_attendance_status(self, attendance_id: int, new_status: str, performed_by: str = "UNKNOWN"):
        self.repo.update_status_by_id(attendance_id, new_status)
        self.audit.log(performed_by, "UPDATE_ATTENDANCE", f"ID {attendance_id} status changed to {new_status}")

    def delete_attendance(self, attendance_id: int, performed_by: str = "UNKNOWN"):
        self.repo.delete_by_id(attendance_id)
        self.audit.log(performed_by, "DELETE_ATTENDANCE", f"Deleted attendance record ID {attendance_id}")

    # --- Read Methods (Reads usually don't need audit) ---
    def get_attendance_for_student(self, student_id: str) -> List[AttendanceRecord]:
        return self.repo.get_by_student(student_id)

    def count_absences_for_student(self, student_id: str) -> int:
        records = self.repo.get_by_student(student_id)
        return sum(1 for r in records if r.status == AttendanceStatus.ABSENT)

    def count_all_student_entries(self, student_id: str) -> int:
        records = self.repo.get_by_student(student_id)
        return sum(1 for r in records)

    def get_attendance_percentage(self, student_id: str) -> float:
        records = self.repo.get_by_student(student_id)
        total = len(records)
        if total == 0: return 100.0
        absences = sum(1 for r in records if r.status == AttendanceStatus.ABSENT)
        return ((total - absences) / total) * 100.0