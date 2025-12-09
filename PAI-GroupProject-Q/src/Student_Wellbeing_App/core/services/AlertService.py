from datetime import datetime
from typing import Optional, List, Union

from src.Student_Wellbeing_App.core.models.Alert import Alert
from src.Student_Wellbeing_App.core.models.AttendanceStatus import AttendanceStatus
from src.Student_Wellbeing_App.core.repositories.AlertRepository import AlertRepository
from src.Student_Wellbeing_App.core.repositories.AttendanceRepository import AttendanceRepository
from src.Student_Wellbeing_App.core.services.AuditService import AuditService
from src.Student_Wellbeing_App.core.models.AlertType import AlertType

class AlertService:
    def __init__(
            self,
            alert_repo: Optional[AlertRepository] = None,
            attendance_repo: Optional[AttendanceRepository] = None,
            audit_service: Optional[AuditService] = None
    ):
        self.alert_repo = alert_repo or AlertRepository()
        self.attendance_repo = attendance_repo or AttendanceRepository()
        self.audit = AuditService() or audit_service

    def raise_alert(
            self,
            student_id: str,
            alert_type: Union[str, AlertType],  # Accept both string and AlertType
            reason: str,
            created_at: Optional[datetime] = None,
    ) -> int:
        alert = Alert(
            alert_id=0,
            student_id=student_id,
            alert_type=alert_type,
            reason=reason,
            created_at=created_at or datetime.now(),
            resolved=False,
        )
        new_id = self.alert_repo.save(alert)
        self.audit.log("SYSTEM", "RAISE_ALERT", f"Raised {alert_type} for {student_id}")
        return new_id

    def generate_multiple_absence_alerts(
            self, student_id: str, threshold: int = 3
    ) -> Optional[int]:
        records = self.attendance_repo.get_by_student(student_id)
        absences = sum(1 for r in records if r.status == AttendanceStatus.ABSENT)
        if absences >= threshold:
            reason = f"Student {student_id} has {absences} absences (>= {threshold})."
            return self.raise_alert(
                student_id=student_id,
                alert_type=AlertType.ATTENDANCE, 
                reason=reason,
            )
        return None

    def get_active_alerts(self) -> List[Alert]:
        return self.alert_repo.list_active()

    def get_resolved_alerts(self) -> List[Alert]:
        return self.alert_repo.list_resolved()
    
    # add perform action logging
    def resolve_alert(self, alert_id: int, performed_by: str = "UNKNOWN"):
        self.alert_repo.resolve(alert_id)
        self.audit.log(performed_by, "RESOLVE_ALERT", f"Resolved Alert ID {alert_id}")