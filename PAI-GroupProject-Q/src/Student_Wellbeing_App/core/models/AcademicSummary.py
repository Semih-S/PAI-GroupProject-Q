from dataclasses import dataclass

from src.Student_Wellbeing_App.core.models.Student import Student
from src.Student_Wellbeing_App.core.models.SubmissionRecord import SubmissionRecord


@dataclass
class AcademicSummary:
    # studen to whom this academic record belongs
    student: Student
    attendance_percentage: float
    # attendance percentage
    submissions: list[SubmissionRecord]
    # list of submission records
    low_mark_submissions: list[SubmissionRecord]

