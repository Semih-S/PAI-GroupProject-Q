from dataclasses import dataclass
from datetime import date

from src.Student_Wellbeing_App.core.models.SubmissionStatus import SubmissionStatus


@dataclass
class SubmissionRecord:
    submission_id: int
    student_id: int
    assessment_id: int
    submitted_at: date
    status: SubmissionStatus
    mark: float
