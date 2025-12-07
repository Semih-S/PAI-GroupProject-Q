import tkinter as tk
from tkinter import ttk, messagebox

from src.Student_Wellbeing_App.core.models.User import User
from src.Student_Wellbeing_App.core.models.UserRole import UserRole
from src.Student_Wellbeing_App.core.services.StudentService import StudentService
from src.Student_Wellbeing_App.core.services.UserService import UserService
from src.Student_Wellbeing_App.core.ui.base_dashboard import BaseDashboard


class AddUserDialog(tk.Toplevel):
    """
    Dialog window to add a new user or student.
    For STUDENT role, extra fields (email, cohort_year) are required.
    """

    def __init__(
        self,
        master,
        user_service: UserService,
        student_service: StudentService,
        on_user_created=None,
    ):
        super().__init__(master)
        self.title("Add New User")
        self.user_service = user_service
        self.student_service = student_service
        self.on_user_created = on_user_created

        self.first_name_var = tk.StringVar()
        self.lastname_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.confirm_password_var = tk.StringVar()
        self.role_var = tk.StringVar()

        # Student-only fields
        self.email_var = tk.StringVar()
        self.cohort_year_var = tk.StringVar()

        container = ttk.Frame(self, padding=15)
        container.pack(fill="both", expand=True)

        # First name
        ttk.Label(container, text="First name").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(container, textvariable=self.first_name_var).grid(
            row=1, column=1, sticky="ew", pady=5
        )

        # Last name
        ttk.Label(container, text="Last name").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(container, textvariable=self.lastname_var).grid(
            row=2, column=1, sticky="ew", pady=5
        )

        # Password
        ttk.Label(container, text="Password").grid(row=3, column=0, sticky="w", pady=5)
        ttk.Entry(container, textvariable=self.password_var, show="*").grid(
            row=3, column=1, sticky="ew", pady=5
        )

        # Confirm password
        ttk.Label(container, text="Confirm Password").grid(row=4, column=0, sticky="w", pady=5)
        ttk.Entry(container, textvariable=self.confirm_password_var, show="*").grid(
            row=4, column=1, sticky="ew", pady=5
        )

        # Role
        ttk.Label(container, text="Role").grid(row=5, column=0, sticky="w", pady=5)
        self.role_combo = ttk.Combobox(
            container,
            textvariable=self.role_var,
            state="readonly",
        )
        self.role_combo["values"] = [role.name for role in UserRole]
        self.role_combo.grid(row=5, column=1, sticky="ew", pady=5)

        # Student-only fields (email, cohort year)
        self.email_label = ttk.Label(container, text="Email")
        self.email_entry = ttk.Entry(container, textvariable=self.email_var)

        self.cohort_label = ttk.Label(container, text="Cohort year")
        self.cohort_entry = ttk.Entry(container, textvariable=self.cohort_year_var)

        def show_student_fields():
            self.email_label.grid(row=6, column=0, sticky="w", pady=5)
            self.email_entry.grid(row=6, column=1, sticky="ew", pady=5)

            self.cohort_label.grid(row=7, column=0, sticky="w", pady=5)
            self.cohort_entry.grid(row=7, column=1, sticky="ew", pady=5)

        def hide_student_fields():
            self.email_label.grid_remove()
            self.email_entry.grid_remove()
            self.cohort_label.grid_remove()
            self.cohort_entry.grid_remove()

        def on_role_changed(*_):
            if self.role_var.get().strip() == "STUDENT":
                show_student_fields()
            else:
                hide_student_fields()

        self.role_var.trace_add("write", on_role_changed)

        container.columnconfigure(1, weight=1)

        # Buttons
        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=8, column=0, columnspan=2, pady=10, sticky="e")

        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Save", command=self._handle_save).pack(side="right", padx=5)

        self.transient(master)
        self.grab_set()
        self.role_combo.focus_set()

        # Ensure initial visibility is correct
        on_role_changed()

    def _handle_save(self):
        first_name = self.first_name_var.get().strip()
        lastname = self.lastname_var.get().strip()
        password = self.password_var.get()
        confirm_password = self.confirm_password_var.get()
        role_name = self.role_var.get().strip()

        if not first_name or not lastname or not password or not confirm_password or not role_name:
            messagebox.showerror("Error", "All fields are required.", parent=self)
            return

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.", parent=self)
            return

        try:
            role = UserRole[role_name]
        except KeyError:
            messagebox.showerror("Error", "Invalid role selected.", parent=self)
            return

        try:
            if role_name == "STUDENT":
                # Extra validation for student fields
                email = self.email_var.get().strip()
                cohort_text = self.cohort_year_var.get().strip()

                if not email or not cohort_text:
                    messagebox.showerror(
                        "Error",
                        "Email and cohort year are required for a student.",
                        parent=self,
                    )
                    return

                try:
                    cohort_year = int(cohort_text)
                except ValueError:
                    messagebox.showerror(
                        "Error",
                        "Cohort year must be a number.",
                        parent=self,
                    )
                    return

                # Create student via StudentService (new model)
                student_id = self.student_service.register_student(
                    first_name=first_name,
                    last_name=lastname,
                    email=email,
                    password=password,
                    cohort_year=cohort_year,
                )
                messagebox.showinfo(
                    "Success",
                    f"Student created with ID: {student_id}",
                    parent=self,
                )
            else:
                # Non-student staff user
                user_id = self.user_service.create_user(
                    first_name=first_name,
                    lastname=lastname,
                    plain_password=password,
                    role=role,
                )
                messagebox.showinfo(
                    "Success",
                    f"User created with ID: {user_id}",
                    parent=self,
                )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create account:\n{e}", parent=self)
            return

        if self.on_user_created:
            self.on_user_created()

        self.destroy()


class AdminDashboard(BaseDashboard):
    ROLE_NAME = "Admin"

    def __init__(
        self,
        master,
        user: User,
        user_service: UserService,
        student_service: StudentService,
        *args,
        **kwargs,
    ):
        self.user = user
        self.user_service = user_service
        self.student_service = student_service

        header = (
            f"{self.ROLE_NAME} Dashboard – "
            f"Logged in as {user.first_name} {user.lastname} "
            f"({user.user_id})"
        )

        super().__init__(master, header, *args, **kwargs)

        # Top bar
        top_bar = ttk.Frame(self)
        top_bar.pack(fill="x", padx=10, pady=(0, 10))

        ttk.Label(top_bar, text="Filter by role:").pack(side="left")

        self.role_filter_var = tk.StringVar(value="All")
        self.role_filter_combo = ttk.Combobox(
            top_bar,
            textvariable=self.role_filter_var,
            state="readonly",
            width=20,
        )
        role_values = ["All"] + [role.name for role in UserRole]
        self.role_filter_combo["values"] = role_values
        self.role_filter_combo.current(0)
        self.role_filter_combo.pack(side="left", padx=5)
        self.role_filter_combo.bind(
            "<<ComboboxSelected>>", lambda e: self.refresh_users()
        )

        ttk.Button(top_bar, text="Add User", command=self.open_add_user_dialog).pack(
            side="left", padx=10
        )

        ttk.Button(top_bar, text="Logout", command=master.show_login).pack(
            side="right"
        )

        # Table
        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(
            table_frame,
            columns=("user_id", "first_name", "lastname", "role"),
            show="headings",
        )
        self.tree.heading("user_id", text="User ID")
        self.tree.heading("first_name", text="First name")
        self.tree.heading("lastname", text="Last name")
        self.tree.heading("role", text="Role")

        self.tree.column("user_id", width=120, anchor="center")
        self.tree.column("first_name", width=150, anchor="w")
        self.tree.column("lastname", width=150, anchor="w")
        self.tree.column("role", width=100, anchor="center")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)

        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.refresh_users()

    def refresh_users(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        role_filter = self.role_filter_var.get()

        try:
            if role_filter == "All":
                users = self.user_service.get_all_users()
            else:
                role = UserRole[role_filter]
                users = self.user_service.get_users_by_role(role)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load users:\n{e}", parent=self)
            return

        for u in users:
            self.tree.insert(
                "",
                "end",
                values=(u.user_id, u.first_name, u.lastname, u.role.name),
            )

    def open_add_user_dialog(self):
        AddUserDialog(
            master=self,
            user_service=self.user_service,
            student_service=self.student_service,
            on_user_created=self.refresh_users,
        )
