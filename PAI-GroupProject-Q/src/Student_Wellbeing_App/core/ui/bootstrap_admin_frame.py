# src/Student_Wellbeing_App/core/ui/bootstrap_admin_frame.py

import tkinter as tk
from tkinter import ttk, messagebox

from src.Student_Wellbeing_App.core.models.UserRole import UserRole
from src.Student_Wellbeing_App.core.services.UserService import UserService


class BootstrapAdminFrame(ttk.Frame):
    """
    Screen shown on first run if no ADMIN user exists.
    Prompts to create the first admin account.
    """

    def __init__(
        self,
        master,
        on_admin_created,
        user_service: UserService,
        *args,
        **kwargs,
    ):
        super().__init__(master, *args, **kwargs)
        self.on_admin_created = on_admin_created
        self.user_service = user_service

        ttk.Label(
            self,
            text="Create First Admin User",
            font=("Segoe UI", 14, "bold"),
        ).pack(pady=15)

        self.first_name_var = tk.StringVar()
        self.lastname_var = tk.StringVar()
        self.password_var = tk.StringVar()

        ttk.Label(self, text="First name").pack(pady=(10, 0))
        ttk.Entry(self, textvariable=self.first_name_var).pack(pady=5)

        ttk.Label(self, text="Last name").pack(pady=(10, 0))
        ttk.Entry(self, textvariable=self.lastname_var).pack(pady=5)

        ttk.Label(self, text="Admin Password").pack(pady=(10, 0))
        ttk.Entry(self, textvariable=self.password_var, show="*").pack(pady=5)

        ttk.Button(self, text="Create Admin", command=self.handle_create_admin).pack(
            pady=15
        )

    def handle_create_admin(self):
        first_name = self.first_name_var.get().strip()
        lastname = self.lastname_var.get().strip()
        password = self.password_var.get().strip()

        if not first_name or not lastname or not password:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        try:
            admin_id = self.user_service.create_user(
                first_name=first_name,
                lastname=lastname,
                plain_password=password,
                role=UserRole.ADMIN,
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create admin: {e}")
            return

        messagebox.showinfo("Success", f"Admin created with ID: {admin_id}")
        self.on_admin_created()
