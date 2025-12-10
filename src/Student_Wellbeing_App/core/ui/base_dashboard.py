from tkinter import ttk


class BaseDashboard(ttk.Frame):
    def __init__(self, master, header_text: str, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        ttk.Label(
            self,
            text=header_text,
            font=("Segoe UI", 14, "bold"),
        ).pack(pady=15, anchor="w", padx=10)
