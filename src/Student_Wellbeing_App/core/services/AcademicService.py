from typing import Optional, List, Tuple
from src.Student_Wellbeing_App.core.models.AcademicSummary import AcademicSummary
from src.Student_Wellbeing_App.core.services.SubmissionService import SubmissionService
from src.Student_Wellbeing_App.core.services.AttendanceService import AttendanceService
from src.Student_Wellbeing_App.core.services.StudentService import StudentService

class AcademicService:
    def __init__(
        self, 
        submission_service: Optional[SubmissionService] = None, 
        attendance_service: Optional[AttendanceService] = None,
        student_service: Optional[StudentService] = None
    ):
        self.submission_service = submission_service or SubmissionService()
        self.attendance_service = attendance_service or AttendanceService()
        self.student_service = student_service or StudentService()

    def get_student_academic_profile(self, student_id: str):
        """
        Return a simple dictionary profile for dashboards.
        """
        submissions = self.submission_service.get_submissions_for_student(student_id)
        attendance_pct = self.attendance_service.get_attendance_percentage(student_id)
        
        # Define low mark threshold (e.g. < 50)
        low_marks = [s for s in submissions if s.mark is not None and s.mark < 50]

        return {
            "total_submissions": len(submissions),
            "low_marks_count": len(low_marks),
            "attendance_pct": attendance_pct,
            "submissions": submissions,
        }

    def get_low_attendance_students(self, students: list, threshold: float = 75.0) -> List[Tuple[object, float]]:
        results = []
        for s in students:
            pct = self.attendance_service.get_attendance_percentage(s.student_id)
            if pct is not None and pct < threshold:
                results.append((s, pct))
        return results

    def get_low_mark_students(self, students: list, threshold: float = 50.0) -> List[Tuple[object, int]]:
        low_marks_list = []
        for s in students:
            subs = self.submission_service.get_submissions_for_student(s.student_id)
            low = [x for x in subs if x.mark is not None and x.mark < threshold]
            if low:
                low_marks_list.append((s, len(low)))
        return low_marks_list

    def get_student_academic_summary(self, student_id: str) -> Optional[AcademicSummary]:
        """
        Build full AcademicSummary object.
        """
        student = self.student_service.get_student_by_id(student_id)
        if not student:
            return None

        attendance_pct = self.attendance_service.get_attendance_percentage(student_id)
        submissions = self.submission_service.get_submissions_for_student(student_id)
        low_marks = [s for s in submissions if s.mark is not None and s.mark < 50]

        return AcademicSummary(
            student=student,
            attendance_percentage=attendance_pct,
            submissions=submissions,
            low_mark_submissions=low_marks,
        )