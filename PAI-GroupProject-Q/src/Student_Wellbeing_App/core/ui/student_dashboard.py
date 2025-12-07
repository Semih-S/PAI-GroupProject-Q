import tkinter as tk
from tkinter import ttk
from datetime import datetime, date

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Models / Services
try:
    from src.Student_Wellbeing_App.core.models.Student import Student
except Exception:
    Student = object  # defensive fallback

from src.Student_Wellbeing_App.core.services.AttendanceService import AttendanceService
from src.Student_Wellbeing_App.core.services.AssignmentService import AssignmentService
from src.Student_Wellbeing_App.core.services.WellbeingService import WellbeingService
from src.Student_Wellbeing_App.core.services.AcademicService import AcademicService

from src.Student_Wellbeing_App.core.ui.base_dashboard import BaseDashboard


# ---------------------------------------------------------------
# Helper Conversion Functions
# ---------------------------------------------------------------

def _to_date(d):
    """
    Convert a value to a datetime.date.
    Accepts: datetime.date, datetime, ISO string.
    """
    if d is None:
        return None
    if isinstance(d, date) and not isinstance(d, datetime):
        return d
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, str):
        # try ISO then fallback
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(d, fmt).date()
            except Exception:
                continue
        return None
    return None


def _status_name(status):
    """
    Convert an enum or string to simple status text.
    """
    if status is None:
        return None
    if hasattr(status, "name"):
        return status.name
    return str(status)


# ---------------------------------------------------------------
# Student Dashboard
# ---------------------------------------------------------------

class StudentDashboard(BaseDashboard):
    ROLE_NAME = "Student"

    def __init__(
            self,
            master,
            student: Student,
            attendance_service: AttendanceService = None,
            assignment_service: AssignmentService = None,
            academic_service: AcademicService = None,
            wellbeing_service: WellbeingService = None,

    ):
        self.student = student

        # Prefer injected services; otherwise create our own
        self.attendance_service = attendance_service or AttendanceService()
        self.assignment_service = assignment_service or AssignmentService()
        self.academic_service = academic_service
        self.wellbeing_service = wellbeing_service or WellbeingService()

        # Defensive attribute fetch
        first_name = getattr(student, "first_name", getattr(student, "firstname", "Unknown"))
        last_name = getattr(student, "last_name", getattr(student, "lastname", "Unknown"))
        student_id = getattr(student, "student_id", getattr(student, "id", "Unknown"))

        header = (
            f"{self.ROLE_NAME} Dashboard – "
            f"Logged in as {first_name} {last_name} ({student_id})"
        )

        super().__init__(master, header)

        # Create UI Notebook Tabs
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)

        self._create_attendance_tab()
        self._create_submissions_tab()
        self._create_wellbeing_tab()
        self._create_logout_tab()

    # ===========================================================
    # ATTENDANCE TAB
    # ===========================================================

    def _load_attendance_records(self):
        sid = getattr(self.student, "student_id", getattr(self.student, "id", None))
        if sid is None:
            return []
        try:
            return self.attendance_service.get_attendance_for_student(sid) or []
        except Exception:
            return []

    def _create_attendance_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Attendance")

        ttk.Label(
            tab,
            text="Attendance Overview",
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", pady=(0, 5))

        records = self._load_attendance_records()

        # Compute simple stats from *all* available records (so it actually shows data)
        present = absent = late = 0
        for r in records:
            name = _status_name(getattr(r, "status", None)).upper()
            if name == "PRESENT":
                present += 1
            elif name == "ABSENT":
                absent += 1
            elif name == "LATE":
                late += 1

        total = present + absent + late
        attendance_pct = (present / total * 100.0) if total > 0 else 0.0

        # ---- Bar chart: Present / Absent / Late ----
        fig = Figure(figsize=(4.5, 3))
        ax = fig.add_subplot(111)

        labels = ["Present", "Absent", "Late"]
        values = [present, absent, late]

        if total == 0:
            ax.text(0.5, 0.5, "No attendance data available.", ha="center", va="center")
            ax.set_xticks([])
            ax.set_yticks([])
        else:
            ax.bar(labels, values)
            ax.set_ylabel("Sessions")
            ax.set_ylim(0, max(values) + 1)

        ax.set_title(f"Overall attendance – {attendance_pct:.1f}% present")

        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=5, fill="x")

        # Text summary underneath
        summary = ttk.Label(
            tab,
            text=(
                f"Total sessions: {total}  |  "
                f"Present: {present}  •  Absent: {absent}  •  Late: {late}"
            ),
            font=("Segoe UI", 9),
        )
        summary.pack(anchor="w", padx=5, pady=(5, 0))

    # ===========================================================
    # SUBMISSIONS TAB  (Assignment tab → SubmissionService)
    # ===========================================================

    def _create_submissions_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Submissions")

        ttk.Label(
            tab,
            text="Assessment Submissions",
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", pady=(0, 5))

        # --- summary area (optional but mirrors staff view) ---
        self.sub_summary_label = ttk.Label(tab, text="", font=("Segoe UI", 9))
        self.sub_summary_label.pack(anchor="w", padx=5, pady=(0, 5))

        # --- treeview with per-submission rows ---
        columns = ("assessment", "submitted_at", "status", "mark", "remark")
        self.submissions_tree = ttk.Treeview(
            tab, columns=columns, show="headings", height=12
        )

        self.submissions_tree.heading("assessment", text="Assessment")
        self.submissions_tree.heading("submitted_at", text="Submitted At")
        self.submissions_tree.heading("status", text="Status")
        self.submissions_tree.heading("mark", text="Mark")
        self.submissions_tree.heading("remark", text="Remark")

        self.submissions_tree.column("assessment", width=160, anchor="w")
        self.submissions_tree.column("submitted_at", width=130, anchor="center")
        self.submissions_tree.column("status", width=90, anchor="center")
        self.submissions_tree.column("mark", width=70, anchor="center")
        self.submissions_tree.column("remark", width=150, anchor="w")

        self.submissions_tree.pack(fill="both", expand=True, padx=5, pady=5)

        # load and render data
        self._load_and_display_student_submissions()


    def _load_and_display_student_submissions(self):
        """Fetch academic profile and render into the submissions tab."""
        if not self.academic_service:
            self.sub_summary_label.config(text="Academic service not configured")
            return

        sid = getattr(self.student, "student_id", getattr(self.student, "id", None))
        if not sid:
            self.sub_summary_label.config(text="No student ID found.")
            return

        try:
            profile = self.academic_service.get_student_academic_profile(sid)
            student = self.student
        except Exception as e:
            self.sub_summary_label.config(text=f"Error loading submissions: {e}")
            return

        self._display_student_submissions(student, profile)




    def _display_student_submissions(self, student, profile: dict):
        """
        Adaptation of display_student_academic_profile for the student's Submissions tab.
        Fills the Treeview and shows a one-line summary.
        """
        # clear old rows
        for row in self.submissions_tree.get_children():
            self.submissions_tree.delete(row)

        subs = profile.get("submissions", [])
        low_marks = profile.get("low_marks", [])

        # --- summary label text (top of tab) ---
        if subs:
            attendance_pct = profile.get("attendance_pct", 0.0)
            total_subs = profile.get("total_submissions", len(subs))
            summary_text = (
                f"Attendance: {attendance_pct:.1f}%   |   "
                f"Total submissions: {total_subs}   |   "
                f"Low marks (<70): {len(low_marks)}"
            )
        else:
            summary_text = "No submissions found for this student."

        self.sub_summary_label.config(text=summary_text)

        # --- populate tree rows ---
        for s in subs:
            assessment_id = getattr(s, "assessment_id", getattr(s, "assignment_id", "N/A"))

            submitted_at = getattr(s, "submitted_at", None)
            submitted_date = _to_date(submitted_at)
            submitted_str = submitted_date.isoformat() if submitted_date else "—"

            # status: submitted / missing
            if getattr(s, "submitted", None) is False:
                status_text = "Not submitted"
            elif submitted_date:
                status_text = "Submitted"
            else:
                status_text = "Unknown"

            mark = getattr(s, "mark", None)
            mark_str = f"{mark:.1f}%" if isinstance(mark, (int, float)) else "—"

            # remark mirroring staff logic
            if isinstance(mark, (int, float)):
                remark = "Low Mark" if mark < 70 else "Good Mark"
            else:
                remark = "Not graded"

            self.submissions_tree.insert(
                "",
                "end",
                values=(assessment_id, submitted_str, status_text, mark_str, remark),
            )


    # ===========================================================
    # TAB 3 – Wellbeing (using WellbeingService)
    # ===========================================================

    def _create_wellbeing_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Wellbeing")

        ttk.Label(
            tab,
            text="Wellbeing Overview",
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        # Text summary area
        self.wb_text = tk.Text(tab, height=8, wrap="word", state="disabled")
        self.wb_text.pack(fill="both", expand=False, padx=5, pady=5)

        # Graph area
        self._plot_wellbeing_graph(tab)
        self._load_wellbeing_summary()

    def _load_wellbeing_records(self):
        try:
            student_id = getattr(self.student, "student_id", getattr(self.student, "id", None))
            if not student_id:
                return []
            records = self.wellbeing_service.get_records_for_student(student_id)
            return records or []
        except Exception:
            return []

    def _load_wellbeing_summary(self):
        records = self._load_wellbeing_records()

        self.wb_text.config(state="normal")
        self.wb_text.delete("1.0", "end")

        if not records:
            self.wb_text.insert("1.0", "No wellbeing records found.")
        else:
            avg_stress = sum(r.stress_level for r in records) / len(records)
            avg_sleep = sum(r.sleep_hours for r in records) / len(records)
            self.wb_text.insert(
                "1.0",
                f"Total records: {len(records)}\n"
                f"Average stress: {avg_stress:.1f} / 5\n"
                f"Average sleep: {avg_sleep:.1f} hours\n",
            )

        self.wb_text.config(state="disabled")

    def _plot_wellbeing_graph(self, parent):
        records = self._load_wellbeing_records()
        if not records:
            fig = Figure(figsize=(5, 3))
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, "No wellbeing data available", ha="center", va="center")
        else:
            dates = [_to_date(r.week_start) for r in records]
            stress = [r.stress_level for r in records]
            sleep = [r.sleep_hours for r in records]

            fig = Figure(figsize=(5, 3))
            ax = fig.add_subplot(111)
            ax.plot(dates, stress, marker="o", label="Stress (0–5)")
            ax.set_ylabel("Stress Level")
            ax.set_xlabel("Week")
            ax.set_title("Stress Over Time")
            ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=5, fill="both", expand=True)

    # ===========================================================
    # TAB 4 – Logout
    # ===========================================================

    def _create_logout_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Logout")

        ttk.Label(
            tab,
            text="Logout",
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", pady=(10, 5), padx=10)

        ttk.Button(
            tab,
            text="Logout",
            command=self.master.show_login,
        ).pack(anchor="e", padx=10, pady=10)
