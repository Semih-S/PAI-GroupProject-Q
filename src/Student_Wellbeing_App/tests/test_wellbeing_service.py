import pytest
from datetime import date, timedelta

from src.Student_Wellbeing_App.core.services.WellbeingService import WellbeingService
from src.Student_Wellbeing_App.core.models.WellbeingRecord import WellbeingRecord


class FakeWellbeingRepository:
    """
    Simple in-memory double for WellbeingRepository to test the service
    without touching the real DB.
    """

    def __init__(self):
        self.records = {}  # record_id -> WellbeingRecord
        self.next_id = 1

        # For verifying calls
        self.last_upsert_record = None
        self.deleted_ids = []
        self.updated_calls = []  # list of (record_id, stress, sleep)

    def upsert(self, record: WellbeingRecord) -> int:
        # Simulate "upsert" by student_id + week_start uniqueness
        self.last_upsert_record = record

        existing_id = None
        for r_id, r in self.records.items():
            if r.student_id == record.student_id and r.week_start == record.week_start:
                existing_id = r_id
                break

        if existing_id is not None:
            record.record_id = existing_id
        else:
            record.record_id = self.next_id
            self.next_id += 1

        self.records[record.record_id] = record
        return record.record_id

    def delete_by_id(self, record_id: int):
        self.deleted_ids.append(record_id)
        self.records.pop(record_id, None)

    def update_by_id(self, record_id: int, stress: int, sleep: float):
        self.updated_calls.append((record_id, stress, sleep))
        if record_id in self.records:
            r = self.records[record_id]
            r.stress_level = stress
            r.sleep_hours = sleep

    def get_by_student(self, student_id: str):
        return [r for r in self.records.values() if r.student_id == student_id]


@pytest.fixture
def repo():
    return FakeWellbeingRepository()


@pytest.fixture
def service(repo):
    return WellbeingService(repo=repo)


# -------------------------------------------------------------------
# add_or_update_record
# -------------------------------------------------------------------

def test_add_or_update_record_creates_new_record_and_returns_id(service, repo):
    week_start = date.today()
    record_id = service.add_or_update_record(
        student_id="STU0001",
        week_start=week_start,
        stress_level=4,
        sleep_hours=6.5,
        source_type="survey",
    )

    assert record_id == 1
    assert record_id in repo.records
    stored = repo.records[record_id]
    assert stored.student_id == "STU0001"
    assert stored.week_start == week_start
    assert stored.stress_level == 4
    assert stored.sleep_hours == 6.5
    assert stored.source_type == "survey"


def test_add_or_update_record_upserts_same_week(service, repo):
    week_start = date.today()
    # First call
    id1 = service.add_or_update_record("STU0001", week_start, 3, 7.0)
    # Second call for the same week & student should update existing record
    id2 = service.add_or_update_record("STU0001", week_start, 5, 5.0)

    assert id1 == id2  # upsert: same record ID
    stored = repo.records[id1]
    assert stored.stress_level == 5
    assert stored.sleep_hours == 5.0


# -------------------------------------------------------------------
# is_editable
# -------------------------------------------------------------------

def _start_of_current_week():
    today = date.today()
    return today - timedelta(days=today.weekday())


def test_is_editable_true_for_current_week_date(service):
    current_week_start = _start_of_current_week()
    # Any date from Monday of this week up to today should be editable
    editable_date = current_week_start + timedelta(days=2)  # e.g. Wednesday
    assert service.is_editable(editable_date) is True


def test_is_editable_false_for_previous_week_date(service):
    current_week_start = _start_of_current_week()
    last_week_date = current_week_start - timedelta(days=1)
    assert service.is_editable(last_week_date) is False


def test_is_editable_accepts_valid_date_string(service):
    today = date.today()
    date_str = today.strftime("%Y-%m-%d")
    # Depending on the weekday, this might or might not be editable.
    # We just assert it does NOT crash and returns a boolean.
    result = service.is_editable(date_str)
    assert isinstance(result, bool)


def test_is_editable_invalid_string_returns_false(service):
    assert service.is_editable("not-a-date") is False


# -------------------------------------------------------------------
# delete_record / update_record_direct
# -------------------------------------------------------------------

def test_delete_record_calls_repo_delete(service, repo):
    # Pre-load a record
    week_start = date.today()
    rec_id = service.add_or_update_record("STU0001", week_start, 3, 7.0)

    service.delete_record(rec_id)

    assert rec_id in repo.deleted_ids
    assert rec_id not in repo.records


def test_update_record_direct_calls_repo_update(service, repo):
    week_start = date.today()
    rec_id = service.add_or_update_record("STU0001", week_start, 3, 7.0)

    service.update_record_direct(rec_id, stress=5, sleep=4.5)

    assert (rec_id, 5, 4.5) in repo.updated_calls
    updated = repo.records[rec_id]
    assert updated.stress_level == 5
    assert updated.sleep_hours == 4.5


# -------------------------------------------------------------------
# get_records_for_student
# -------------------------------------------------------------------

def test_get_records_for_student_returns_repo_data(service, repo):
    w1 = date.today()
    w2 = w1 - timedelta(days=7)

    repo.upsert(WellbeingRecord(0, "STU0001", w1, 3, 7.0, "survey"))
    repo.upsert(WellbeingRecord(0, "STU0001", w2, 4, 6.0, "survey"))
    repo.upsert(WellbeingRecord(0, "STU0002", w1, 2, 8.0, "survey"))

    records = service.get_records_for_student("STU0001")

    assert len(records) == 2
    assert all(r.student_id == "STU0001" for r in records)


# -------------------------------------------------------------------
# high_stress_weeks
# -------------------------------------------------------------------

def test_high_stress_weeks_filters_on_threshold(service, repo):
    w1 = date.today()
    w2 = w1 - timedelta(days=7)
    w3 = w1 - timedelta(days=14)

    repo.upsert(WellbeingRecord(0, "STU0001", w1, 5, 6.0, "survey"))  # high
    repo.upsert(WellbeingRecord(0, "STU0001", w2, 4, 7.0, "survey"))  # borderline
    repo.upsert(WellbeingRecord(0, "STU0001", w3, 3, 8.0, "survey"))  # below
    repo.upsert(WellbeingRecord(0, "STU0002", w1, 5, 5.0, "survey"))  # other student

    high_weeks_default = service.high_stress_weeks("STU0001")  # threshold=4
    assert len(high_weeks_default) == 2
    assert all(r.stress_level >= 4 for r in high_weeks_default)
    assert all(r.student_id == "STU0001" for r in high_weeks_default)

    high_weeks_strict = service.high_stress_weeks("STU0001", threshold=5)
    assert len(high_weeks_strict) == 1
    assert high_weeks_strict[0].stress_level == 5
