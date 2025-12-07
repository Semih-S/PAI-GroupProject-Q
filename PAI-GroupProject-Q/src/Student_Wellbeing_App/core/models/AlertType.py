from enum import Enum

class AlertType(str, Enum):
    ACADEMIC = "Academic"       # Low grades
    ATTENDANCE = "Attendance"   # Missed 3 classes in a row
    WELLBEING = "Wellbeing"     # High stress level
    """ add more here
    ...
    ...
    """
    OTHER = "Other"

    def __str__(self):
        return self.value