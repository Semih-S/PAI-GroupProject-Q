from dataclasses import dataclass
from datetime import datetime
from .ActionType import ActionType

@dataclass
class AuditLog:
    log_id: int
    user_id: int
    entity_type: str
    entity_id: int
    action_type: str
    timestamp: datetime
    details: str = ""

#

    def __post_init__(self):
        if not isinstance(self.action_type, ActionType):
            try:
                self.action_type = ActionType(self.action_type)
            except ValueError:
                raise ValueError(f"Invalid action_type: {self.action_type}")