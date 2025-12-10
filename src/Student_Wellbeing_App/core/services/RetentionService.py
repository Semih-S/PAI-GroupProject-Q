from typing import List, Dict, Any
from src.Student_Wellbeing_App.core.repositories.RetentionRepository import RetentionRepository
from src.Student_Wellbeing_App.core.models.RetentionRule import RetentionRule
from src.Student_Wellbeing_App.core.services.AuditService import AuditService
import pandas as pd

class RetentionService:
    def __init__(self):
        self.repo = RetentionRepository()
        self.repo.init_default_rules()
        self.audit = AuditService()

    def get_all_rules(self) -> List[RetentionRule]:
        return self.repo.get_rules()

    # --- CRUD ---
    def create_rule(self, data_type: str, months: int, is_active: bool, performed_by: str = "ADMIN"):
        self.repo.add_rule(data_type, months, int(is_active))
        self.audit.log(performed_by, "CREATE_RULE", f"Added retention rule for {data_type} ({months}m)")

    def update_rule_settings(self, rule_id: int, months: int, is_active: bool, performed_by: str = "ADMIN"):
        self.repo.update_rule(rule_id, months, is_active)
        self.audit.log(performed_by, "UPDATE_RULE", f"Updated rule {rule_id} -> {months}m, Active:{is_active}")

    def delete_rule(self, rule_id: int, performed_by: str = "ADMIN"):
        self.repo.delete_rule(rule_id)
        self.audit.log(performed_by, "DELETE_RULE", f"Deleted rule {rule_id}")

    # --- Preview ---
    def get_preview_dataframe(self, rule_id: int) -> pd.DataFrame:
        rule = self.repo.get_rule_by_id(rule_id)
        if not rule: return pd.DataFrame()
        data = []
        if rule.data_type == 'RESOLVED_ALERTS':
            data = self.repo.preview_old_alerts(rule.retention_months)
        elif rule.data_type == 'GRADUATED_STUDENTS':
            data = self.repo.preview_graduated_students(rule.retention_months)
        return pd.DataFrame(data) if data else pd.DataFrame()

    # --- Execute ---
    def execute_specific_rule(self, rule_id: int, performed_by: str = "ADMIN") -> int:
        rule = self.repo.get_rule_by_id(rule_id)
        if not rule or not rule.is_active: return 0
        
        count = 0
        if rule.data_type == 'RESOLVED_ALERTS':
            count = self.repo.cleanup_old_alerts(rule.retention_months)
        elif rule.data_type == 'GRADUATED_STUDENTS':
            count = self.repo.cleanup_graduated_students(rule.retention_months)
            
        self.audit.log(performed_by, "EXECUTE_RETENTION", f"Rule {rule.data_type} cleaned {count} records")
        return count