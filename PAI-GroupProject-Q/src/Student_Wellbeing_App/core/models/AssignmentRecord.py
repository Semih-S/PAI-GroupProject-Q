# core/models/AssignmentRecord.py

from dataclasses import dataclass
from typing import Optional


@dataclass
class AssignmentRecord:
    """
    Represents a single assignment *instance* for a given student.

    There might be a separate `Assignment` table (module, title, etc.),
    but this model is for the student's record: submitted/marked/etc.
    """
    assignment_record_id: int
    student_id: str            # keep this consistent with Student.student_id
    assignment_id: str         # could be code, UUID, etc.
    submitted: bool = False
    submitted_date: Optional[str] = None  # ISO "YYYY-MM-DD"
    due_date: Optional[str] = None        # ISO "YYYY-MM-DD"
    mark: Optional[float] = None
    feedback: Optional[str] = None


# Backwards-compat alias if any existing code imports `Submission` from here
Submission = AssignmentRecord
