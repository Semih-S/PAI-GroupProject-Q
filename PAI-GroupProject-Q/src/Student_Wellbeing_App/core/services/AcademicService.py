# core/services/AcademicService.py
from src.Student_Wellbeing_App.core.models.AcademicSummary import AcademicSummary


class AcademicService:
    def __init__(self, submission_service, attendance_service):
        self.submission_service = submission_service
        self.attendance_service = attendance_service


    def get_student_academic_profile(self, student_id):
        submissions = self.submission_service.get_submissions_for_student(student_id)
        attendance_pct = self.attendance_service.get_attendance_percentage(student_id)
        low_marks = [s for s in submissions if s.mark < 70]

        return {
            "total_submissions": len(submissions),
            "low_marks": low_marks,
            "attendance_pct": attendance_pct,
            "submissions": submissions,
        }

    def get_low_attendance_students(self, students, threshold=75):
        results = []
        for s in students:
            pct = self.attendance_service.get_attendance_percentage(s.student_id)
            if pct is not None and pct < threshold:
                results.append((s, pct))
        return results

    def get_low_mark_students(self, students, threshold=70):
        low_marks = []
        for s in students:
            subs = self.submission_service.get_submissions_for_student(s.student_id)
            low = [x for x in subs if x.mark is not None and x.mark < threshold]
            if low:
                low_marks.append((s, len(low)))
        return low_marks

    def get_student_academic_summary(self, student_id: str) -> AcademicSummary:
        attendance_pct, absences = self.attendance_service.get_attendance_summary(student_id)
        submissions = self.assignment_service.get_marked_assignments_for_student(student_id)
        low_marks = self.assignment_service.get_low_mark_assignments_for_student(student_id)

        return AcademicSummary(
            student=...,  # you fill this from StudentService
            attendance_percentage=attendance_pct,
            absences=absences,
            submissions=submissions,
            low_mark_submissions=low_marks,
        )
