from dataclasses import dataclass
from datetime import datetime
from src.Student_Wellbeing_App.core.models.AlertType import AlertType


@dataclass
class Alert:
    alert_id: int
    student_id: int
    alert_type: AlertType
    reason: str
    created_at: datetime
    resolved: bool = False

