import pandas as pd
import sqlite3
import sys
from pathlib import Path

# --- Path Setup ---
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parents[3]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.Student_Wellbeing_App.core.database.connection import DB_PATH

def get_db():
    return sqlite3.connect(DB_PATH)

# --- 1. Overall Wellbeing Trends ---
def load_aggregate_wellbeing_trend():
    conn = get_db()
    query = """
    SELECT week_start, 
           AVG(stress_level) as avg_stress, 
           AVG(sleep_hours) as avg_sleep
    FROM wellbeing_record
    GROUP BY week_start
    ORDER BY week_start
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# --- 2. carriculum Performance Summary ---
def load_course_performance_summary():
    conn = get_db()
    # A. average grades per module
    q_grades = """
    SELECT a.module_code, AVG(s.mark) as avg_mark
    FROM submission s
    JOIN assessment a ON s.assessment_id = a.assessment_id
    WHERE s.mark IS NOT NULL
    GROUP BY a.module_code
    """
    df_grades = pd.read_sql_query(q_grades, conn)
    
    # B. attendance rate per module
    q_att = """
    SELECT session_id as module_code, 
           CAST(SUM(CASE WHEN status='PRESENT' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 as attendance_rate
    FROM attendance
    GROUP BY session_id
    """
    df_att = pd.read_sql_query(q_att, conn)
    conn.close()
    
    if not df_grades.empty and not df_att.empty:
        return pd.merge(df_grades, df_att, on='module_code', how='outer').fillna(0)
    return df_grades if not df_grades.empty else df_att

# --- 3. Export Full Student Data with Risk Status ---
def load_full_export_data():
    """generate a full export dataframe with risk status for each student"""
    conn = get_db()
    
    # 1. base student info
    df_stu = pd.read_sql_query("SELECT student_id, first_name, lastname, email, year FROM student", conn)
    
    # 2. grade (avg)
    df_grade = pd.read_sql_query("SELECT student_id, AVG(mark) as avg_grade FROM submission WHERE mark > 0 GROUP BY student_id", conn)
    
    # 3. attendance (%)
    df_att = pd.read_sql_query("""
        SELECT student_id, 
               CAST(SUM(CASE WHEN status='PRESENT' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 as attendance_pct
        FROM attendance 
        GROUP BY student_id
    """, conn)
    
    # 4. Wellbeing (avg stress & sleep)
    df_well = pd.read_sql_query("""
        SELECT student_id,
               AVG(stress_level) as avg_stress,
               AVG(sleep_hours) as avg_sleep
        FROM wellbeing_record
        GROUP BY student_id
    """, conn)
    
    conn.close()
    
    # --- Merge Data ---
    df = pd.merge(df_stu, df_grade, on='student_id', how='left')
    df = pd.merge(df, df_att, on='student_id', how='left')
    df = pd.merge(df, df_well, on='student_id', how='left') # merge wellbeing data
    
    # --- Data cleaning---
    df['avg_grade'] = df['avg_grade'].fillna(0).round(1)
    df['attendance_pct'] = df['attendance_pct'].fillna(100.0).round(1) # no attendance means full attendance
    df['avg_stress'] = df['avg_stress'].fillna(0).round(1)
    df['avg_sleep'] = df['avg_sleep'].fillna(0).round(1)
    
    # risk logic identification
    def identify_risk(row):
        flags = []
        # risk criteria
        if row['avg_stress'] >= 4.0: flags.append("High Stress")
        if row['avg_sleep'] < 6.0 and row['avg_sleep'] > 0: flags.append("Low Sleep") # > 0 to avoid new students
        if row['attendance_pct'] < 80.0: flags.append("Low Attendance")
        if row['avg_grade'] < 50.0 and row['avg_grade'] > 0: flags.append("Low Grades")
        
        if flags:
            return f"⚠️ AT RISK: {', '.join(flags)}"
        return "Normal"

    df['Risk_Status'] = df.apply(identify_risk, axis=1)
    
    # return specific columns in order
    cols = ['student_id', 'first_name', 'lastname', 'Risk_Status', 'avg_stress', 'avg_sleep', 'attendance_pct', 'avg_grade', 'email']
    # make sure all cols exist
    final_cols = [c for c in cols if c in df.columns]
    
    return df[final_cols]

# academic performance and attendance data for students
def load_academic_data(module_code=None):
    conn = get_db()
    if module_code:
        grades_query = """
        SELECT s.student_id, AVG(s.mark) as avg_mark 
        FROM submission s
        JOIN assessment a ON s.assessment_id = a.assessment_id
        WHERE s.mark IS NOT NULL AND a.module_code = ?
        GROUP BY s.student_id
        """
        params = (module_code,)
        attendance_query = """
        SELECT student_id, COUNT(*) as present_count
        FROM attendance
        WHERE status = 'PRESENT' AND session_id LIKE ?
        GROUP BY student_id
        """
        att_params = (f"{module_code}%",)
    else:
        grades_query = "SELECT student_id, AVG(mark) as avg_mark FROM submission WHERE mark IS NOT NULL GROUP BY student_id"
        params = ()
        attendance_query = "SELECT student_id, COUNT(*) as present_count FROM attendance WHERE status = 'PRESENT' GROUP BY student_id"
        att_params = ()

    df_grades = pd.read_sql_query(grades_query, conn, params=params)
    df_attendance = pd.read_sql_query(attendance_query, conn, params=att_params)
    
    if module_code:
        q_stu = "SELECT s.student_id, s.first_name, s.lastname FROM student s JOIN enrollment e ON s.student_id=e.student_id WHERE e.module_code=?"
        p_stu = (module_code,)
    else:
        q_stu = "SELECT student_id, first_name, lastname FROM student"
        p_stu = ()
        
    df_students = pd.read_sql_query(q_stu, conn, params=p_stu)
    conn.close()
    
    if df_students.empty: return pd.DataFrame()

    df_analysis = pd.merge(df_students, df_grades, on='student_id', how='left')
    df_analysis = pd.merge(df_analysis, df_attendance, on='student_id', how='left')
    df_analysis['avg_mark'] = df_analysis['avg_mark'].fillna(0)
    df_analysis['present_count'] = df_analysis['present_count'].fillna(0)
    return df_analysis