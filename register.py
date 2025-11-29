import tkinter as tk
import sqlite3

# Function to register a user that takes username, email and password
def register_user():
    u = username.get().strip()
    p = password.get().strip()
    e = email.get().strip()

    if not u or not p or not e:
        status_label.config(text="All fields required!")
        return

    # Input sanitization to further protect from sql injection
    if '"' in u or ";" in u or "--" in u:
        status_label.config(text="Invalid characters in input!")
        return

    try:
        conn = sqlite3.connect("student_data.db")
        cur = conn.cursor()

        # Placeholders used for sql injection safe queries
        cur.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", (u, p, e))

        conn.commit()
        conn.close()
        status_label.config(text="Registration successful!")

    except sqlite3.IntegrityError:
        status_label.config(text="Username already exists!")
    except Exception as ex:
        status_label.config(text=f"Error: {ex}")

# Grahical user interface using tkinter
root = tk.Tk()
root.title("User Registration")

username = tk.StringVar()
password = tk.StringVar()
email = tk.StringVar()

tk.Label(root, text="Username:").pack()
tk.Entry(root, textvariable=username).pack()

tk.Label(root, text="Password:").pack()
tk.Entry(root, textvariable=password, show="*").pack()

tk.Label(root, text="Email:").pack()
tk.Entry(root, textvariable=email).pack()

tk.Button(root, text="Register", command=register_user).pack(pady=5)

status_label = tk.Label(root, text="")
status_label.pack()

root.mainloop()