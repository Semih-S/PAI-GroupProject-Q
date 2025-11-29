import pandas as pd
import sqlite3
import tkinter as tk

# Loading CSV
df = pd.read_csv("data.csv")

# Create sqlite database
conn = sqlite3.connect("student_data.db")
cur = conn.cursor()

# Export dataframe to sqlite table
df.to_sql("student", conn, if_exists="replace", index=False)

# Add a new table for users
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT NOT NULL
);
""")

conn.commit()
conn.close()

print("CSV converted to sqlite and users table added for registeration and login")