from typing import Optional, List, Union
from datetime import date, timedelta, datetime
from src.Student_Wellbeing_App.core.models.WellbeingRecord import WellbeingRecord
from src.Student_Wellbeing_App.core.repositories.WellbeingRepository import WellbeingRepository

class WellbeingService:
    def __init__(self, repo: Optional[WellbeingRepository] = None):
        self.repo = repo or WellbeingRepository()

    def add_or_update_record(
            self,
            student_id: str,
            week_start: date,
            stress_level: int,
            sleep_hours: float,
            source_type: str = "survey",
    ) -> int:
        """
        Record a survey entry. If exists for this week, updates it.
        """
        record = WellbeingRecord(
            record_id=0, 
            student_id=student_id,
            week_start=week_start,
            stress_level=stress_level,
            sleep_hours=sleep_hours,
            source_type=source_type,
        )
        return self.repo.upsert(record)

    def is_editable(self, record_date: Union[date, str]) -> bool:
        """
        Only allow editing records from the current week
        """
        today = date.today()
        # calculate the start of the current week (Monday)
        current_week_start = today - timedelta(days=today.weekday())
        
        # SQLite sometimes returns date as string, handle both cases
        target_date = record_date
        if isinstance(target_date, str):
            try:
                # try parsing as date string
                target_date = datetime.strptime(target_date, "%Y-%m-%d").date()
            except ValueError:
                return False # if parsing fails, not editable
            
        # can only edit if the record_date is within this week
        return target_date >= current_week_start

    def delete_record(self, record_id: int):
        self.repo.delete_by_id(record_id)

    def update_record_direct(self, record_id: int, stress: int, sleep: float):
        self.repo.update_by_id(record_id, stress, sleep)

    def get_records_for_student(self, student_id: str) -> List[WellbeingRecord]:
        return self.repo.get_by_student(student_id)

    def high_stress_weeks(self, student_id: str, threshold: int = 4) -> List[WellbeingRecord]:
        records = self.repo.get_by_student(student_id)
        return [r for r in records if r.stress_level >= threshold]