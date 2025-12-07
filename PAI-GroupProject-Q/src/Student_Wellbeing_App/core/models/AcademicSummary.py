from dataclasses import dataclass

from src.Student_Wellbeing_App.core.models.Student import Student
from src.Student_Wellbeing_App.core.models.SubmissionRecord import SubmissionRecord


@dataclass
class AcademicSummary:
    student: Student
    attendance_percentage: float
    submissions: list[SubmissionRecord]
    low_mark_submissions: list[SubmissionRecord]
