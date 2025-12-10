from dataclasses import dataclass
from datetime import date


@dataclass
class WellbeingRecord:
    record_id: int
    student_id: int
    week_start: date
    stress_level: int  # 1–5
    sleep_hours: float
    source_type: str = "survey"
