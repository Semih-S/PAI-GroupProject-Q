import tkinter as tk
from tkinter import ttk, messagebox

from src.Student_Wellbeing_App.core.models.User import User
from src.Student_Wellbeing_App.core.models.UserRole import UserRole
from src.Student_Wellbeing_App.core.services.StudentService import StudentService
from src.Student_Wellbeing_App.core.services.WellbeingService import WellbeingService
from src.Student_Wellbeing_App.core.services.AcademicService import AcademicService
from src.Student_Wellbeing_App.core.ui.base_dashboard import BaseDashboard


class StaffDashboard(BaseDashboard):
    

    ROLE_LABELS = {
        UserRole.WELLBEING_OFFICER: "Wellbeing Officer",
        UserRole.COURSE_DIRECTOR: "Course Director",
    }

    def __init__(
            self,
            master,
            user: User,
            student_service: StudentService,
            wellbeing_service: WellbeingService,
            academic_service: AcademicService,
            *args,
            **kwargs,
    ):
        self.user = user
        self.student_service = student_service
        self.wellbeing_service = wellbeing_service
        self.academic_service = academic_service

        header = (
            f"{self.ROLE_LABELS.get(user.role)} Dashboard – "
            f"{user.first_name} {user.lastname} ({user.user_id})"
        )

        super().__init__(master, header, *args, **kwargs)
        self._build_ui()

  
    def _build_ui(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        if self.user.role == UserRole.COURSE_DIRECTOR:
            academics_tab = ttk.Frame(notebook)
            notebook.add(academics_tab, text="Academics")
            self._build_academics_tab(academics_tab)

        if self.user.role == UserRole.WELLBEING_OFFICER:
            wellbeing_tab = ttk.Frame(notebook)
            notebook.add(wellbeing_tab, text="Wellbeing")
            self._build_wellbeing_tab(wellbeing_tab)

        logout_tab = ttk.Frame(notebook)
        notebook.add(logout_tab, text="Logout")
        self._build_logout_tab(logout_tab)

 
    def _build_academics_tab(self, parent: ttk.Frame):
        ttk.Label(
            parent,
            text="Student Academic Monitoring",
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", pady=5)

        input_frame = ttk.Frame(parent)
        input_frame.pack(fill="x", pady=10)

        self.ac_student_id_var = tk.StringVar()
        ttk.Label(input_frame, text="Student ID:").pack(side="left", padx=5)
        ttk.Entry(
            input_frame, textvariable=self.ac_student_id_var, width=15
        ).pack(side="left", padx=5)

        ttk.Button(
            input_frame,
            text="View Academic Data",
            command=self.view_student_academic_record,
        ).pack(side="left", padx=5)

        ttk.Button(
            input_frame,
            text="View Attendance Detail",
            command=self._view_student_attendance,
        ).pack(side="left", padx=5)

        self.ac_results_text = tk.Text(
            parent, height=16, wrap="word", state="disabled"
        )
        self.ac_results_text.pack(fill="both", expand=True, padx=10, pady=10)

        actions = ttk.Frame(parent)
        actions.pack(fill="x", pady=5)

        ttk.Button(
            actions,
            text="⚠ Low Attendance Students",
            command=self._show_low_attendance_students,
        ).pack(side="left", padx=10, pady=5)

        ttk.Button(
            actions,
            text="📉 Low-Mark Students",
            command=self._show_low_mark_students,
        ).pack(side="left", padx=5)

    def view_student_academic_record(self):
        student_id = self.ac_student_id_var.get().strip()

        if not student_id:
            messagebox.showwarning("Input Required", "Enter a student ID", parent=self)
            return

        try:
            profile = self.academic_service.get_student_academic_profile(student_id)
            student = self.student_service.get_student_by_id(student_id)
            if not student:
                messagebox.showerror("Not Found", f"Student ID {student_id} not found.", parent=self)
                return

            self.display_student_academic_profile(student, profile)

        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)

    def display_student_academic_profile(self, student, profile: dict):
        self.ac_results_text.config(state="normal")
        self.ac_results_text.delete("1.0", "end")

        subs = profile.get("submissions", [])
        low_marks = profile.get("low_marks", [])

        content = (
            f"STUDENT ACADEMIC PROFILE\n"
            f"{'=' * 60}\n"
            f"Name: {student.first_name} {student.lastname}\n"
            f"Student ID: {student.student_id}\n"
            f"Cohort Year: {student.year}\n\n"
            f"Attendance: {profile['attendance_pct']:.1f}%\n"
            f"Total submissions: {profile['total_submissions']}\n"
            f"Low marks (<70): {len(low_marks)}\n"
            f"{'-' * 60}\n"
        )

        if subs:
            content += "Submissions:\n"
            for s in subs[-10:]:
                if s.mark < 70:
                    remark = "Low Mark"
                else:
                    remark = "Good Mark"

                content += f"  • {s.assessment_id}: {s.mark}% : {remark}\n"

        self.ac_results_text.insert("1.0", content)
        self.ac_results_text.config(state="disabled")

    def _show_low_attendance_students(self):
        """List all students below the attendance threshold."""
        try:
            students = self.student_service.list_students()
            results = self.academic_service.get_low_attendance_students(students)
        except Exception as e:
            return messagebox.showerror("Error", str(e), parent=self)

        self.ac_results_text.config(state="normal")
        self.ac_results_text.delete("1.0", "end")

        if not results:
            self.ac_results_text.insert("1.0", "✅ No low-attendance students.")
        else:
            for student, pct in results:
                self.ac_results_text.insert(
                    "end",
                    f"{student.first_name} {student.lastname} "
                    f"({student.student_id}) – {pct:.1f}%\n",
                )

        self.ac_results_text.config(state="disabled")

    def _show_low_mark_students(self):
        
        try:
            students = self.student_service.list_students()
            low_mark_students = self.academic_service.get_low_mark_students(students)
        except Exception as e:
            return messagebox.showerror("Error", str(e), parent=self)

        self._display_low_mark_students(low_mark_students)

    def _display_low_mark_students(self, low_mark_students):
        self.ac_results_text.config(state="normal")
        self.ac_results_text.delete("1.0", "end")

        if not low_mark_students:
            content = "✓ No low-mark students. All students are performing above threshold.\n"
        else:
            content = (
                    f"⚠️ LOW-MARK STUDENTS: {len(low_mark_students)} students with concern\n"
                    + "=" * 70 + "\n\n"
            )
            for student, count in sorted(low_mark_students, key=lambda x: x[1], reverse=True):
                content += (
                    f"• {student.first_name} {student.lastname} "
                    f"(ID: {student.student_id}) – {count} low-mark submissions\n"
                )

        self.ac_results_text.insert("1.0", content)
        self.ac_results_text.config(state="disabled")

    def _view_student_attendance(self):
        student_id = self.ac_student_id_var.get().strip()
        if not student_id:
            messagebox.showwarning("Input Required", "Enter a student ID", parent=self)
            return

        try:
            student = self.student_service.get_student_by_id(student_id)
            if not student:
                messagebox.showerror("Not Found", f"Student ID {student_id} not found.", parent=self)
                return

            records = self.academic_service.attendance_service.get_attendance_for_student(student_id)

            self._display_attendance_records(student, records)

        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)

    def _display_attendance_records(self, student, records):
        self.ac_results_text.config(state="normal")
        self.ac_results_text.delete("1.0", "end")

        content = (
                f"Attendance for {student.first_name} {student.lastname} ({student.student_id})\n"
                + "=" * 70 + "\n\n"
        )

        if not records:
            content += "No attendance data.\n"
        else:
            for r in records[-20:]:
                content += f"{r.session_date} – {r.session_id}: {r.status.name}\n"

        self.ac_results_text.insert("1.0", content)
        self.ac_results_text.config(state="disabled")

   

    def _build_wellbeing_tab(self, parent):
        ttk.Label(
            parent, text="Student Wellbeing Monitoring",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=5)

        search = ttk.Frame(parent)
        search.pack(fill="x", pady=5)

        self.wb_student_id_var = tk.StringVar()
        ttk.Label(search, text="Student ID:").pack(side="left", padx=5)
        ttk.Entry(search, textvariable=self.wb_student_id_var, width=15).pack(
            side="left", padx=5
        )

        ttk.Button(
            search,
            text="View Wellbeing",
            command=self.view_student_wellbeing,
        ).pack(side="left", padx=5)

        self.wb_results_text = tk.Text(
            parent, height=15, wrap="word", state="disabled"
        )
        self.wb_results_text.pack(fill="both", expand=True, padx=10, pady=10)

        actions = ttk.Frame(parent)
        actions.pack(fill="x", pady=5)

        ttk.Button(
            actions,
            text="📊 High-Risk Students",
            command=self._show_high_risk_students,
        ).pack(side="left", padx=5)

        ttk.Button(
            actions,
            text="📈 Cohort Stress Overview",
            command=self._show_cohort_stress_overview,
        ).pack(side="left", padx=5)

        ttk.Button(
            actions,
            text="⚠ Alerts",
            command=self.show_alerts,
        ).pack(side="left", padx=5)

    def view_student_wellbeing(self):
        student_id = self.wb_student_id_var.get().strip()
        if not student_id:
            return messagebox.showwarning("Input Required", "Please enter a student ID.", parent=self)

        try:
            student = self.student_service.get_student_by_id(student_id)

            if not student:
                messagebox.showerror(
                    "Not Found", f"Student ID {student_id} not found.")
                return

            records = self.wellbeing_service.get_records_for_student(student_id)
            high_stress = self.wellbeing_service.high_stress_weeks(student_id)
        except Exception as e:
            return messagebox.showerror("Error", str(e), parent=self)

        self.display_student_wellbeing(student, records, high_stress)

    def display_student_wellbeing(self, student, records, high_stress_weeks):
        self.wb_results_text.config(state="normal")
        self.wb_results_text.delete("1.0", "end")

        content = (
            f"STUDENT WELLBEING PROFILE\n"
            f"{'=' * 70}\n"
            f"Name: {student.first_name} {student.lastname}\n"
            f"Student ID: {student.student_id}\n\n"
            f"Email: {student.email}\n"
            f"Cohort Year: {student.year}\n"
            f"{'=' * 70}\n\n"
        )

        if not records:
            content += "No wellbeing data available.\n"
        else:
            content += f"Total Records: {len(records)}\n"
            content += f"High-Stress Weeks (stress ≥ 4): {len(high_stress_weeks)}\n\n"

            content += "Recent Wellbeing Records:\n"
            content += "-" * 70 + "\n"

            for r in records[-5:]:
                content += (
                    f"{r.week_start}: Stress={r.stress_level}/5, "
                    f"Sleep={r.sleep_hours} hrs\n"
                )

            if high_stress_weeks:
                content += "\n" + "=" * 70 + "\n"
                content += "⚠️ HIGH STRESS WEEKS (Intervention Recommended):\n"
                content += "-" * 70 + "\n"
                for record in high_stress_weeks[-5:]:
                    content += (
                        f"Week of {record.week_start}: "
                        f"Stress={record.stress_level}/10, Sleep={record.sleep_hours}hrs\n"
                    )

        self.wb_results_text.insert("1.0", content)
        self.wb_results_text.config(state="disabled")

    def _show_high_risk_students(self):
        students = self.student_service.list_students()
        results = [
            (s, len(self.wellbeing_service.high_stress_weeks(s.student_id)))
            for s in students
            if self.wellbeing_service.high_stress_weeks(s.student_id)
        ]

        self.display_high_risk_results(results)

    def display_high_risk_results(self, results):
        self.wb_results_text.config(state="normal")
        self.wb_results_text.delete("1.0", "end")

        if not results:
            content = "✅ No high-risk students. \n"
        else:
            content = (
                    f"⚠️ HIGH-RISK STUDENTS: {len(results)} requiring attention\n"
                    + "=" * 70 + "\n\n"
            )

            for s, count in sorted(results, key=lambda x: x[1], reverse=True):
                content += (
                    f"• {s.first_name} {s.lastname}  "
                    f"(ID: {s.student_id}) - "
                    f"{count} high-stress weeks\n"
                )
        self.wb_results_text.insert("1.0", content)
        self.wb_results_text.config(state="disabled")

    def _show_cohort_stress_overview(self):
        """Compute wellbeing stats per cohort and render them."""
        students = self.student_service.list_students()
        cohort_data = {}

        for s in students:
            records = self.wellbeing_service.get_records_for_student(s.student_id)

            if records:

                cohort = s.year
                if cohort not in cohort_data:
                    cohort_data[cohort] = {
                        "total_students": 0,
                        "total_records": 0,
                        "high_stress_count": 0,
                        "sum_stress": 0.0,
                        "sum_sleep": 0.0,
                        "avg_stress": 0.0,
                        "avg_sleep": 0.0,
                    }

                data = cohort_data[cohort]
                high_stress_weeks = self.wellbeing_service.high_stress_weeks(s.student_id)

                data["total_students"] += 1
                data["total_records"] += len(records)
                data["high_stress_count"] += len(high_stress_weeks)
                data["sum_stress"] += sum(r.stress_level for r in records)
                data["sum_sleep"] += sum(r.sleep_hours for r in records)

        # Finalise averages
        for data in cohort_data.values():
            if data["total_records"] > 0:
                data["avg_stress"] = data["sum_stress"] / data["total_records"]
                data["avg_sleep"] = data["sum_sleep"] / data["total_records"]
            else:
                data["avg_stress"] = 0.0
                data["avg_sleep"] = 0.0

        self.display_cohort_overview(cohort_data)

    def display_cohort_overview(self, cohort_data):
        """Display stress overview by cohort."""
        self.wb_results_text.config(state="normal")
        self.wb_results_text.delete("1.0", "end")

        content = "COHORT STRESS OVERVIEW\n"
        content += "=" * 70 + "\n\n"

        if not cohort_data:
            content += "No data available.\n"
        else:
            for cohort in sorted(cohort_data.keys()):
                data = cohort_data[cohort]
                high_stress_pct = (
                        data["high_stress_count"] / data["total_students"] * 100) if data["total_students"] > 0 else 0

                content += f"Year {cohort} Cohort:\n"
                content += f"  • Students: {data['total_students']}\n"
                content += f"  • Average Stress Level: {data['avg_stress']:.1f}/5\n"
                content += f"  • Average Sleep: {data['avg_sleep']:.1f}hrs\n"
                content += f"  • High-Risk Students: {data['high_stress_count']} ({high_stress_pct:.0f}%)\n"
                content += "-" * 70 + "\n"

        self.wb_results_text.insert("1.0", content)
        self.wb_results_text.config(state="disabled")

    def show_alerts(self):
        """Collect wellbeing alerts for all students and render them."""
        try:
            students = self.student_service.list_students()
            alerts = []

            for s in students:
                # All wellbeing records for the student
                records = self.wellbeing_service.get_records_for_student(s.student_id)
                # High-stress weeks
                weeks = self.wellbeing_service.high_stress_weeks(s.student_id)

                # High stress alert
                if weeks:
                    alerts.append({
                        "student": s,
                        "type": "High Stress",
                        "severity": len(weeks),
                        "message": f"{len(weeks)} weeks with high stress levels",
                    })

                # Low sleep alert (based on last 5 records, if any)
                if records:
                    recent_records = records[-5:]
                    avg_sleep = sum(r.sleep_hours for r in recent_records) / len(recent_records)
                    if avg_sleep < 6:
                        alerts.append({
                            "student": s,
                            "type": "Low Sleep",
                            "severity": 6 - avg_sleep,
                            "message": f"Average sleep: {avg_sleep:.1f}hrs (below recommended 6hrs)",
                        })

            self.display_alerts(alerts)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve data: {e}", parent=self)

    def display_alerts(self, alerts):
        """Render wellbeing alerts grouped by student."""
        self.wb_results_text.config(state="normal")
        self.wb_results_text.delete("1.0", "end")

        if not alerts:
            content = "✓ No active wellbeing alerts. All students are in good standing.\n"
            self.wb_results_text.insert("1.0", content)
            self.wb_results_text.config(state="disabled")
            return

        # Group alerts by student
        student_alerts = {}
        for alert in alerts:
            s = alert["student"]
            sid = s.student_id

            if sid not in student_alerts:
                student_alerts[sid] = {
                    "student": s,
                    "issues": [],
                }

            student_alerts[sid]["issues"].append(alert)

        content = f"⚠️ ACTIVE WELLBEING ALERTS: {len(alerts)} issues detected\n"
        content += "=" * 70 + "\n\n"

        # Print grouped per student
        for sid in sorted(student_alerts.keys()):
            entry = student_alerts[sid]
            student = entry["student"]
            issues = entry["issues"]

            content += f"{student.first_name} {student.lastname} (ID: {sid}):\n"
            for issue in issues:
                content += f"  ⚠️ {issue['type']}: {issue['message']}\n"
            content += "\n"

        self.wb_results_text.insert("1.0", content)
        self.wb_results_text.config(state="disabled")

  

    def _build_logout_tab(self, parent):
        ttk.Button(
            parent, text="Logout", command=self.master.show_login
        ).pack(anchor="e", padx=10, pady=10)

