from datetime import datetime
from typing import Optional, List

from src.Student_Wellbeing_App.core.models.AuditLog import AuditLog
from src.Student_Wellbeing_App.core.repositories.AuditRepository import AuditRepository


class AuditService:
    """Records and retrieves audit events for key actions."""

    def __init__(self, repo: Optional[AuditRepository] = None):
        self.repo = repo or AuditRepository()

    def log_action(
            self,
            user_id: int,
            entity_type: str,
            entity_id: int,
            action_type: str,
            details: str = "",
    ) -> int:
        log = AuditLog(
            log_id=0,
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action_type=action_type,
            timestamp=datetime.utcnow(),
            details=details,
        )
        return self.repo.log(log)

    def list_logs(self) -> List[AuditLog]:
        return self.repo.list_all()
