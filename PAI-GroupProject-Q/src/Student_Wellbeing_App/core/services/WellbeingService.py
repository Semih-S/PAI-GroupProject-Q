from typing import Optional, List

from src.Student_Wellbeing_App.core.models.WellbeingRecord import WellbeingRecord
from src.Student_Wellbeing_App.core.repositories.WellbeingRepository import WellbeingRepository


class WellbeingService:

    def __init__(self, repo: Optional[WellbeingRepository] = None):
        self.repo = repo or WellbeingRepository()

    def add_wellbeing_record(
            self,
            student_id: int,
            week_start,
            stress_level: int,
            sleep_hours: float,
            source_type: str = "survey",
    ) -> int:
        record = WellbeingRecord(
            record_id=0,
            student_id=student_id,
            week_start=week_start,
            stress_level=stress_level,
            sleep_hours=sleep_hours,
            source_type=source_type,
        )
        return self.repo.save(record)

    def get_records_for_student(self, student_id: int) -> List[WellbeingRecord]:
        return self.repo.get_by_student(student_id)

    def high_stress_weeks(
            self, student_id: int, threshold: int = 4
    ) -> List[WellbeingRecord]:
        records = self.repo.get_by_student(student_id)
        return [r for r in records if r.stress_level >= threshold]
