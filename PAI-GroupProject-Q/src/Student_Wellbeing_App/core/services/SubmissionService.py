# src/Student_Wellbeing_App/core/services/SubmissionService.py

from typing import List, Optional
from datetime import datetime

from src.Student_Wellbeing_App.core.models.SubmissionRecord import SubmissionRecord
from src.Student_Wellbeing_App.core.models.SubmissionStatus import SubmissionStatus
from src.Student_Wellbeing_App.core.repositories.SubmissionRepository import SubmissionRepository


class SubmissionService:
    """Encapsulates submission-related operations and rules."""

    def __init__(self, repo: Optional[SubmissionRepository] = None):
        self.repo = repo or SubmissionRepository()

    def record_submission(
            self,
            student_id: int,
            assessment_id: int,
            submitted_at: datetime,
            status: SubmissionStatus,
            mark: float,
    ) -> int:
        """
        Store a submission entry for a student.
        """

        record = SubmissionRecord(
            submission_id=0,          # will usually be auto-assigned by DB
            student_id=student_id,
            assessment_id=assessment_id,
            submitted_at=submitted_at,
            status=status,
            mark=mark,
        )
        return self.repo.save(record)

    def get_submissions_for_student(self, student_id: int) -> List[SubmissionRecord]:
        return self.repo.get_by_student(student_id)

    def count_non_submissions_for_student(self, student_id: int) -> int:
        records = self.repo.get_by_student(student_id)
        return sum(1 for r in records if r.status == SubmissionStatus.MISSING)
