from datetime import datetime
from typing import Optional, List

from src.Student_Wellbeing_App.core.models.Alert import Alert
from src.Student_Wellbeing_App.core.models.AttendanceStatus import AttendanceStatus
from src.Student_Wellbeing_App.core.repositories.AlertRepository import AlertRepository
from src.Student_Wellbeing_App.core.repositories.AttendanceRepository import AttendanceRepository


class AlertService:
    """Coordinates creation and management of alerts."""

    def __init__(
            self,
            alert_repo: Optional[AlertRepository] = None,
            attendance_repo: Optional[AttendanceRepository] = None,
    ):
        self.alert_repo = alert_repo or AlertRepository()
        self.attendance_repo = attendance_repo or AttendanceRepository()

    def raise_alert(
            self,
            student_id: int,
            alert_type: str,
            reason: str,
            created_at: Optional[datetime] = None,
    ) -> int:
        alert = Alert(
            alert_id=0,
            student_id=student_id,
            alert_type=alert_type,
            reason=reason,
            created_at=created_at or datetime.utcnow(),
            resolved=False,
        )
        return self.alert_repo.save(alert)

    def generate_multiple_absence_alerts(
            self, student_id: int, threshold: int = 3
    ) -> Optional[int]:
        """Create an alert if absences for a student exceed threshold."""
        records = self.attendance_repo.get_by_student(student_id)
        absences = sum(1 for r in records if r.status == AttendanceStatus.ABSENT)
        if absences >= threshold:
            reason = f"Student {student_id} has {absences} absences (>= {threshold})."
            return self.raise_alert(
                student_id=student_id,
                alert_type="multiple_absences",
                reason=reason,
            )
        return None

    def get_active_alerts(self) -> List[Alert]:
        return self.alert_repo.list_active()