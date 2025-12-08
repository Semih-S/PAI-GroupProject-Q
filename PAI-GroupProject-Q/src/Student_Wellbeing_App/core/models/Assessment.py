from dataclasses import dataclass
from datetime import date

@dataclass
class Assessment:
    assessment_id: int
    module_code: str
    title: str
    due_date: date
    weight: float
