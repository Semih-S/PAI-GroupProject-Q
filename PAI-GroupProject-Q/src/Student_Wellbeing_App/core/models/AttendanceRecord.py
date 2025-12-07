from dataclasses import dataclass
from datetime import date

from src.Student_Wellbeing_App.core.models.AttendanceStatus import AttendanceStatus


@dataclass
class AttendanceRecord:
    attendance_id: int
    student_id: int
    session_date: date
    session_id: str
    status: AttendanceStatus
