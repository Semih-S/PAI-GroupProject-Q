from enum import Enum


class SubmissionStatus(str, Enum):
    PRESENT = "SUBMITTED"
    ABSENT = "MISSING"
    EXCUSED = "LATE"
