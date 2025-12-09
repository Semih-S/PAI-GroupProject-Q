from src.Student_Wellbeing_App.core.repositories.AuditRepository import AuditRepository

class AuditService:
    def __init__(self):
        self.repo = AuditRepository()

    def log(self, user_id: str, action: str, details: str):
        # Record an audit log entry
        # if user_id is None or empty, use "SYSTEM" as operator
        operator = user_id if user_id else "SYSTEM"
        self.repo.log_action(operator, action, details)

    def get_logs(self):
        return self.repo.get_recent_logs()