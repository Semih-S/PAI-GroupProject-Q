import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from src.Student_Wellbeing_App.core.services.AuthenticationService import (
    AuthenticationService,
    AuthResult,
)


class LoginFrame(ttk.Frame):
    def __init__(
        self,
        master,
        auth_service: AuthenticationService,
        on_login_success,  # callback(auth_result: AuthResult)
        *args,
        **kwargs,
    ):
        """
        auth_service: AuthenticationService instance
        on_login_success: callback called when login succeeds
        """
        super().__init__(master, *args, **kwargs)

        self.auth_service = auth_service
        self.on_login_success = on_login_success

        self.columnconfigure(1, weight=1)

        ttk.Label(self, text="User / Student ID:").grid(
            row=0, column=0, padx=10, pady=10, sticky="e"
        )
        ttk.Label(self, text="Password:").grid(
            row=1, column=0, padx=10, pady=10, sticky="e"
        )

        self.id_var = tk.StringVar()
        self.password_var = tk.StringVar()

        ttk.Entry(self, textvariable=self.id_var).grid(
            row=0, column=1, padx=10, pady=10, sticky="ew"
        )
        ttk.Entry(self, textvariable=self.password_var, show="*").grid(
            row=1, column=1, padx=10, pady=10, sticky="ew"
        )

        login_btn = ttk.Button(self, text="Login", command=self.handle_login)
        login_btn.grid(row=2, column=0, columnspan=2, pady=15)

    def handle_login(self):
        identifier = self.id_var.get().strip()   # EMP0001 or STU0001
        password = self.password_var.get().strip()

        if not identifier or not password:
            messagebox.showwarning(
                "Missing data", "Please enter both ID and password.", parent=self
            )
            return

        auth_result = self.auth_service.authenticate_any(
            identifier, password
        )

        
        if auth_result is None:
            messagebox.showerror("Login failed", "Invalid ID or password.", parent=self)
            self.password_var.set("")
            return

        # success – hand off to app
        self.on_login_success(auth_result)

