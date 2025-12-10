from enum import Enum

class AlertType(str, Enum):
    ACADEMIC = "low_performance"       # Low grades
    ATTENDANCE = "low_attendance"   # Missed 3 classes in a row
    WELLBEING =  "low_wellbeing"   # High stress level
    OTHER = "Other"

    def __str__(self):
        return self.value