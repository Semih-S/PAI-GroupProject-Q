from dataclasses import dataclass

@dataclass
class RetentionRule:
    rule_id: int
    data_type: str
    retention_months: int 
    is_active: bool       