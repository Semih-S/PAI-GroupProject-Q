# core/services/AssignmentService.py

from __future__ import annotations

from typing import List, Optional, Iterable, Tuple
from datetime import datetime, date

from src.Student_Wellbeing_App.core.models.AssignmentRecord import AssignmentRecord
from src.Student_Wellbeing_App.core.repositories.AssignmentRepository import (
    AssignmentRepository,
)


class AssignmentService:
    """
    Business logic around assignment records.
    """

    def __init__(self, repo: Optional[AssignmentRepository] = None):
        self.repo = repo or AssignmentRepository()

    # ---------- Mutations ----------

    def submit_assignment(
            self,
            student_id: str,
            assignment_id: str,
            submitted_date: Optional[date] = None,
            mark: Optional[float] = None,
            feedback: Optional[str] = None,
    ) -> int:
        """
        Record an assignment submission; optionally include mark/feedback.
        """
        submitted_date_str = (
            (submitted_date or date.today()).strftime("%Y-%m-%d")
        )

        record = AssignmentRecord(
            assignment_record_id=0,
            student_id=student_id,
            assignment_id=assignment_id,
            submitted=True,
            submitted_date=submitted_date_str,
            # due_date can be set later if needed
            mark=mark,
            feedback=feedback,
        )
        return self.repo.save(record)

    # ---------- Queries for a single student ----------

    def get_assignments_for_student(self, student_id: str) -> List[AssignmentRecord]:
        return self.repo.get_by_student(student_id)

    def get_pending_assignments_for_student(
            self, student_id: str
    ) -> List[AssignmentRecord]:
        return self.repo.get_pending_by_student(student_id)

    def get_marked_assignments_for_student(
            self, student_id: str
    ) -> List[AssignmentRecord]:
        return self.repo.get_marked_by_student(student_id)

    def get_low_mark_assignments_for_student(
            self, student_id: str, threshold: float = 50.0
    ) -> List[AssignmentRecord]:
        """
        Return all marked assignments where mark < threshold.
        """
        marked = self.get_marked_assignments_for_student(student_id)
        return [r for r in marked if r.mark is not None and r.mark < threshold]

    # ---------- Aggregates over many students (for staff dashboards) ----------

    def get_low_mark_students(
            self,
            students: Iterable,
            threshold: float = 50.0,
    ) -> List[Tuple[object, int]]:
        """
        For each student in the iterable, count low-mark assignments.
        Returns list of (student_obj, low_mark_count), filtered to > 0.
        """
        results: List[Tuple[object, int]] = []

        for s in students:
            lows = self.get_low_mark_assignments_for_student(
                s.student_id, threshold=threshold
            )
            if lows:
                results.append((s, len(lows)))

        return results
