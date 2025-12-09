# ui/app.py

import tkinter as tk

from src.Student_Wellbeing_App.core.models.Student import Student
from src.Student_Wellbeing_App.core.models.User import User
from src.Student_Wellbeing_App.core.models.UserRole import UserRole
from src.Student_Wellbeing_App.core.services.AcademicService import AcademicService
from src.Student_Wellbeing_App.core.services.AssignmentService import AssignmentService
from src.Student_Wellbeing_App.core.services.AttendanceService import AttendanceService
from src.Student_Wellbeing_App.core.services.AuthenticationService import (
    AuthenticationService,
    AuthResult,
)
from src.Student_Wellbeing_App.core.services.SubmissionService import SubmissionService
from src.Student_Wellbeing_App.core.services.UserService import UserService
from src.Student_Wellbeing_App.core.repositories.UserRepository import UserRepository
from src.Student_Wellbeing_App.core.services.StudentService import StudentService
from src.Student_Wellbeing_App.core.repositories.StudentRepository import StudentRepository
from src.Student_Wellbeing_App.core.database.migrations import run_migrations
from src.Student_Wellbeing_App.core.services.WellbeingService import WellbeingService


class WellbeingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Wellbeing System")
        self.geometry("800x550")

        # 1. Ensure DB + tables exist
        run_migrations()

        # 2. Set up services & repos
        self.user_repo = UserRepository()
        self.user_service = UserService(self.user_repo)
        self.student_service = StudentService(StudentRepository())
        self.wellbeing_service = WellbeingService()
        self.auth_service = AuthenticationService()
        self.submission_service = SubmissionService()
        self.attendance_service = AttendanceService()
        self.assignment_service = AssignmentService()

        self.academic_service = AcademicService(
            self.submission_service,
            self.attendance_service,
        )

        self._current_screen = None

        self._screen_factories = {
            "login": self._create_login_screen,
            "bootstrap_admin": self._create_bootstrap_admin_screen

        }

        # First-run bootstrap check: do we have any ADMIN users?
        if not self.user_repo.has_admin():
            self.show_screen("bootstrap_admin")
        else:
            self.show_screen("login")



    def _clear_screen(self):
        if self._current_screen is not None:
            self._current_screen.destroy()
            self._current_screen = None

    def show_screen(self, name: str, **kwargs):
       
        self._clear_screen()

        factory = self._screen_factories.get(name)
        if factory is None:
            raise ValueError(f"Unknown screen: {name}")

        screen = factory(**kwargs)
        screen.pack(fill="both", expand=True)
        self._current_screen = screen

    def show_login(self):
        """Public helper for Logout buttons etc."""
        self.show_screen("login")

   
    def _create_login_screen(self):
        from src.Student_Wellbeing_App.core.ui.login_frame import LoginFrame

        return LoginFrame(
            master=self,
            auth_service=self.auth_service,
            on_login_success=self.handle_login_success,
        )

    def _create_bootstrap_admin_screen(self):
        from src.Student_Wellbeing_App.core.ui.bootstrap_admin_frame import BootstrapAdminFrame

        return BootstrapAdminFrame(
            master=self,
            on_admin_created=self.show_login,
            user_service=self.user_service,
        )

    def _create_student_dashboard(self, student: Student):
        from src.Student_Wellbeing_App.core.ui.student_dashboard import StudentDashboard
        return StudentDashboard(
            self,
            student,
            attendance_service=self.attendance_service,
            wellbeing_service=self.wellbeing_service,
            academic_service=self.academic_service,
        )

    def _create_staff_dashboard(self, user: User):
       
        from src.Student_Wellbeing_App.core.ui.staff_dashboard import StaffDashboard

        return StaffDashboard(
            master=self,
            user=user,
            student_service=self.student_service,
            wellbeing_service=self.wellbeing_service,
            academic_service=self.academic_service,
        )

    def _create_admin_dashboard(self, user: User):
        from src.Student_Wellbeing_App.core.ui.admin_dashboard import AdminDashboard

        return AdminDashboard(
            self,
            user=user,
            user_service=self.user_service,
            student_service=self.student_service,
        )


    def _create_generic_dashboard(self, header: str):
        from src.Student_Wellbeing_App.core.ui.base_dashboard import BaseDashboard

        return BaseDashboard(self, header)



    def handle_login_success(self, auth_result: AuthResult):
        
        if auth_result.kind == "student":
            student: Student = auth_result.principal
            self._screen_factories["student_dashboard"] = (
                lambda student=student: self._create_student_dashboard(student)
            )
            self.show_screen("student_dashboard")
        else:
            user: User = auth_result.principal

            # Shared staff dashboard for both roles
            if user.role in (UserRole.WELLBEING_OFFICER, UserRole.COURSE_DIRECTOR):
                self._screen_factories["staff_dashboard"] = (
                    lambda user=user: self._create_staff_dashboard(user)
                )
                self.show_screen("staff_dashboard")

            elif user.role == UserRole.ADMIN:
                self._screen_factories["admin_dashboard"] = (
                    lambda user=user: self._create_admin_dashboard(user)
                )
                self.show_screen("admin_dashboard")

            else:
                # fallback generic dashboard
                header = (
                    f"Dashboard – Logged in as "
                    f"{user.first_name} {user.lastname} ({user.user_id})"
                )
                self._screen_factories["generic_dashboard"] = (
                    lambda header=header: self._create_generic_dashboard(header)
                )
                self.show_screen("generic_dashboard")


if __name__ == "__main__":
    app = WellbeingApp()
    app.mainloop()

