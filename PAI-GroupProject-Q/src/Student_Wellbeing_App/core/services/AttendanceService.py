from typing import List, Optional

from src.Student_Wellbeing_App.core.models.AttendanceRecord import AttendanceRecord
from src.Student_Wellbeing_App.core.models.AttendanceStatus import AttendanceStatus
from src.Student_Wellbeing_App.core.repositories.AttendanceRepository import AttendanceRepository


class AttendanceService:
    """Encapsulates attendance-related operations and rules."""

    def __init__(self, repo: Optional[AttendanceRepository] = None):
        self.repo = repo or AttendanceRepository()

    def record_attendance(
            self,
            student_id: int,
            session_date,
            session_id: str,
            status: AttendanceStatus,
    ) -> int:
        record = AttendanceRecord(
            attendance_id=0,
            student_id=student_id,
            session_date=session_date,
            session_id=session_id,
            status=status,
        )
        return self.repo.save(record)

    def get_attendance_for_student(self, student_id: int) -> List[AttendanceRecord]:
        return self.repo.get_by_student(student_id)

    def count_absences_for_student(self, student_id: int) -> int:
        records = self.repo.get_by_student(student_id)
        return sum(1 for r in records if r.status == AttendanceStatus.ABSENT)

    def count_all_student_entries(self, student_id: int) -> int:
        records = self.repo.get_by_student(student_id)
        return sum(1 for r in records)

    def get_attendance_percentage(self, student_id: int) -> float:
        records = self.repo.get_by_student(student_id)
        total = len(records)
        if total == 0:
            return 100.0  # or 0.0, depending on how you want to treat “no data”
        absences = sum(1 for r in records if r.status == AttendanceStatus.ABSENT)
        presents = total - absences
        return (presents / total) * 100.0