import tkinter as tk
import sqlite3

logged_in_user = None  # Track login session

def login_user():
    global logged_in_user
    user_input = username_or_email.get().strip()
    p = password.get().strip()

    if not user_input or not p:
        status_label.config(text="Enter Username or Email along with your Password")
        return

    conn = sqlite3.connect("student_data.db")
    cur = conn.cursor()

    # Injection-safe using placeholders
    cur.execute("""
        SELECT id, username, email FROM users
        WHERE (username = ? AND password = ?)
           OR (email = ? AND password = ?)
    """, (user_input, p, user_input, p))

    user = cur.fetchone()
    conn.close()

    if user:
        logged_in_user = user  # Save session
        status_label.config(text="Login successful")
        open_dashboard()       # Open dashboard after login
    else:
        status_label.config(text="Invalid credentials")

def open_dashboard():
    if not logged_in_user:
        return

    dashboard = tk.Toplevel(root)
    dashboard.title("Student Dashboard")

    tk.Label(
        dashboard,
        text="Welcome to the Student Analytics Dashboard",
        font=("Arial", 14, "bold")
    ).pack(pady=10)

    tk.Button(
        dashboard, text="Show Student Records",
        command=lambda: show_student_records(dashboard),
        width=30
    ).pack(pady=5)

    tk.Button(
        dashboard, text="Show Analytics",
        command=lambda: show_analytics(dashboard),
        width=30
    ).pack(pady=5)

def show_student_records(parent_window):
    viewer = tk.Toplevel(parent_window)
    viewer.title("All Student Records")

    conn = sqlite3.connect("student_data.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM student")
    rows = cur.fetchall()
    conn.close()

    for i, row in enumerate(rows):
        tk.Label(viewer, text=str(row)).grid(row=i, column=0, padx=5, pady=2)

def show_analytics(parent_window):
    analytics = tk.Toplevel(parent_window)
    analytics.title("Student Analytics")

    conn = sqlite3.connect("student_data.db")
    cur = conn.cursor()

    cur.execute("SELECT student_id, student_name, AVG(attended) FROM student GROUP BY student_id")
    avg_attendance = cur.fetchall()

    cur.execute("SELECT student_id, AVG(stress_level) FROM student GROUP BY student_id")
    avg_stress = cur.fetchall()

    cur.execute("SELECT student_id, AVG(hours_slept) FROM student GROUP BY student_id")
    avg_sleep = cur.fetchall()

    cur.execute("SELECT week, AVG(stress_level) FROM student GROUP BY week ORDER BY AVG(stress_level) DESC LIMIT 1")
    highest_stress_week = cur.fetchone()

    conn.close()

    row = 0
    tk.Label(analytics, text="Average Attendance Per Student", font=("Arial", 11, "bold")).grid(row=row, column=0, pady=4)
    row += 1
    for student in avg_attendance:
        tk.Label(analytics, text=f"{student[1]}: {round(student[2], 2)}").grid(row=row, column=0)
        row += 1

    row += 1
    tk.Label(analytics, text="Average Stress Level Per Student", font=("Arial", 11, "bold")).grid(row=row, column=0, pady=4)
    row += 1
    for student in avg_stress:
        tk.Label(analytics, text=f"{student[0]}: {round(student[1], 2)}").grid(row=row, column=0)
        row += 1

    row += 1
    tk.Label(analytics, text="Average Hours Slept Per Student", font=("Arial", 11, "bold")).grid(row=row, column=0, pady=4)
    row += 1
    for student in avg_sleep:
        tk.Label(analytics, text=f"{student[0]}: {round(student[1], 2)} hours").grid(row=row, column=0)
        row += 1

    row += 1
    tk.Label(analytics, text="Week With Highest Stress", font=("Arial", 11, "bold"), fg="red").grid(row=row, column=0, pady=4)
    row += 1
    if highest_stress_week:
        tk.Label(analytics, text=f"Week {highest_stress_week[0]} (Avg Stress: {round(highest_stress_week[1], 2)})").grid(row=row, column=0)

# ===== LOGIN GUI =====
root = tk.Tk()
root.title("Login")

username_or_email = tk.StringVar()
password = tk.StringVar()

tk.Label(root, text="Username or Email:").pack()
tk.Entry(root, textvariable=username_or_email).pack(pady=2)

tk.Label(root, text="Password:").pack()
tk.Entry(root, textvariable=password, show="*").pack(pady=2)

tk.Button(root, text="Login", command=login_user).pack(pady=5)

status_label = tk.Label(root, text="")
status_label.pack()

root.mainloop()
