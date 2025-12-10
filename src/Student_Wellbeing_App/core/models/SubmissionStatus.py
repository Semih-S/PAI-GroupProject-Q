from enum import Enum


class SubmissionStatus(str, Enum):
    PRESENT = "SUBMITTED"
    ABSENT = "MISSING"
    EXCUSED = "LATE"

    def __str__(self):
        return self.value