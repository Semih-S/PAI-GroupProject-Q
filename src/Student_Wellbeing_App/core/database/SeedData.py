import sqlite3
import random
import hashlib
from datetime import date, timedelta, datetime, time
from pathlib import Path

# --- Configuration ---
DB_PATH = Path(__file__).resolve().parent / "student_wellbeing_db.sqlite3"
MODULES = [
    ("CS101", "Intro to Programming"), ("CS102", "Advanced Python"),
    ("DS201", "Data Science Fundamentals"), ("AI301", "Machine Learning Basics"),
    ("ET101", "Ethics in Technology"), ("UX201", "User Experience Design")
]
STAFF = [
    ("EMP0001", "Alice Admin", "ADMIN"), ("EMP0002", "Bob Wellbeing", "WELLBEING_OFFICER"),
    ("EMP0003", "Charlie Code", "COURSE_DIRECTOR"), ("EMP0004", "Diana Data", "COURSE_DIRECTOR"),
    ("EMP0005", "Evan Ethics", "COURSE_DIRECTOR")
]
TEACHER_MAP = {"EMP0003": ["CS101", "CS102"], "EMP0004": ["DS201", "AI301"], "EMP0005": ["ET101", "UX201"]}

def get_conn(): return sqlite3.connect(DB_PATH)
def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()
def rnd_time(day): return datetime.combine(day, time(random.randint(9, 17), random.randint(0, 59)))

def log_audit(cur, uid, action, detail, ts):
    cur.execute("INSERT INTO audit_log (user_id, action, details, timestamp) VALUES (?,?,?,?)", (uid, action, detail, ts))

def seed_data():
    print(f"🌱 Seeding Database: {DB_PATH}")
    conn = get_conn()
    cur = conn.cursor()

    # 1. Clean Slate (Delete data but keep schema)
    tables = ["audit_log", "submission", "attendance", "wellbeing_record", "alert", "enrollment", 
              "teaching_assignment", "assessment", "student", "module", "user", "retention_rule"]
    for t in tables: 
        try: cur.execute(f"DELETE FROM {t}"); cur.execute("DELETE FROM sqlite_sequence WHERE name=?", (t,))
        except: pass

    # 2. Init Core Data (Modules & Staff)
    print("✨ Initializing Modules and Staff...")
    for code, title in MODULES:
        cur.execute("INSERT INTO module VALUES (?, ?)", (code, title))
        log_audit(cur, "SYSTEM", "CREATE_MODULE", f"Created {code}", datetime.now())

    pw_hash = hash_pw("password123")
    for eid, name, role in STAFF:
        f, l = name.split()
        cur.execute("INSERT INTO user VALUES (?, ?, ?, ?, ?)", (eid, f, l, pw_hash, role))
        if eid in TEACHER_MAP:
            for m in TEACHER_MAP[eid]: cur.execute("INSERT INTO teaching_assignment (user_id, module_code) VALUES (?,?)", (eid, m))

    # 3. Create Students (Profiles: HIGH, AVG, RISK)
    print("🎓 Creating 50 Students with diverse profiles...")
    students = []
    codes = [m[0] for m in MODULES]
    for i in range(1, 51):
        sid, profile = f"STU{i:04d}", "HIGH" if i<=30 else "AVG" if i<=45 else "RISK"
        cur.execute("INSERT INTO student VALUES (?,?,?,?,?,?)", (sid, f"Student{i}", profile, f"stu{i}@uni.ac.uk", pw_hash, 2025))
        
        # Random enrollment (1-2 courses)
        my_courses = random.sample(codes, random.randint(1, 2))
        for c in my_courses: cur.execute("INSERT INTO enrollment (student_id, module_code) VALUES (?,?)", (sid, c))
        students.append({"id": sid, "prof": profile, "mods": my_courses})
        log_audit(cur, "EMP0001", "REGISTER_STUDENT", f"Enrolled {sid}", rnd_time(date.today()-timedelta(95)))

    # 4. Generate Ancient Data (Retention Test)
    old_dt = date.today() - timedelta(days=730)
    for i in range(90, 100): # Graduated students
        cur.execute("INSERT INTO student VALUES (?,?,?,?,?,?)", (f"STU{i:04d}", f"Grad{i}", "Old", f"old{i}@uni.ac.uk", pw_hash, 2018))
    for i in range(10): # Old alerts
        cur.execute("INSERT INTO alert (student_id, alert_type, reason, created_at, resolved) VALUES (?,?,?,?,?)", 
                    (students[i]["id"], "OLD_ISSUE", "Ancient alert", old_dt, 1))

    # 5. Timeline Generation (90 Days History)
    print("📅 Generating 3-month Timeline (Trends & Bell Curves)...")
    today = date.today()
    curr_date = today - timedelta(days=90)
    
    # Pre-create Assessments
    assess_map = {}
    for c in codes:
        # Midterm (45 days ago), Final (10 days ago)
        d_mid, d_fin = today-timedelta(45), today-timedelta(10)
        cur.execute("INSERT INTO assessment (module_code, title, due_date, weight) VALUES (?,?,?,?)", (c, f"{c} Midterm", d_mid, 40))
        mid_id = cur.lastrowid
        cur.execute("INSERT INTO assessment (module_code, title, due_date, weight) VALUES (?,?,?,?)", (c, f"{c} Final", d_fin, 60))
        fin_id = cur.lastrowid
        assess_map[c] = {'mid': (mid_id, d_mid), 'fin': (fin_id, d_fin)}

    while curr_date <= today:
        # Detect "Stress Weeks" (Exam weeks)
        is_stress_wk = any(abs((curr_date - d).days) < 5 for d in [today-timedelta(45), today-timedelta(10)])
        
        # A. Attendance (Weekdays)
        if curr_date.weekday() < 5:
            for s in students:
                for m in s["mods"]:
                    # Absences: Higher on Fridays, higher for RISK profiles, higher during stress weeks
                    fail_rate = 0.02 if s["prof"]=="HIGH" else 0.10 if s["prof"]=="AVG" else 0.30
                    if is_stress_wk and s["prof"]=="RISK": fail_rate = 0.60
                    if curr_date.weekday() == 4: fail_rate += 0.05 
                    
                    status = "ABSENT" if random.random() < fail_rate else "PRESENT"
                    if status == "ABSENT" and random.random() > 0.8: status = "EXCUSED"
                    cur.execute("INSERT INTO attendance (student_id, session_date, session_id, status) VALUES (?,?,?,?)", (s["id"], curr_date, m, status))

        # B. Wellbeing & Alerts (Mondays)
        if curr_date.weekday() == 0:
            for s in students:
                # Bell curve values
                mu_s, sigma_s = (2, 0.5) if s["prof"]=="HIGH" else (3, 0.8) if s["prof"]=="AVG" else (4, 1.0)
                mu_sl, sigma_sl = (8, 0.5) if s["prof"]=="HIGH" else (7, 1.0) if s["prof"]=="AVG" else (5.5, 1.5)
                
                stress = int(random.gauss(mu_s, sigma_s)) + (1 if is_stress_wk else 0)
                sleep = round(random.gauss(mu_sl, sigma_sl) - (1.0 if is_stress_wk else 0), 1)
                
                cur.execute("INSERT INTO wellbeing_record (student_id, week_start, stress_level, sleep_hours, source_type) VALUES (?,?,?,?,?)",
                            (s["id"], curr_date, max(1, min(5, stress)), max(0, min(12, sleep)), 'survey'))
                
                # Risk Logic
                if s["prof"] == "RISK" and (stress >= 5 or sleep < 4.5) and random.random() > 0.6:
                    cur.execute("INSERT INTO alert (student_id, alert_type, reason, created_at, resolved) VALUES (?,?,?,?,0)",
                                (s["id"], "HIGH_RISK", f"Stress:{stress}, Sleep:{sleep}", curr_date))
                    log_audit(cur, "SYSTEM", "RAISE_ALERT", f"Auto-alert for {s['id']}", rnd_time(curr_date))

        # C. Grading (If today matches grading deadline + 2 days)
        for m in codes:
            for atype in ['mid', 'fin']:
                aid, due = assess_map[m][atype]
                if curr_date == due + timedelta(days=2):
                    print(f"   -> Grading {m} {atype} on {curr_date}")
                    for s in students:
                        if m in s["mods"]:
                            # Bell Curve Grades
                            mu, sigma = (85, 5) if s["prof"]=="HIGH" else (65, 10) if s["prof"]=="AVG" else (45, 15)
                            mark = max(0, min(100, int(random.gauss(mu, sigma))))
                            status = "SUBMITTED"
                            
                            # Risk students might miss Finals
                            if s["prof"]=="RISK" and atype=='fin' and random.random()>0.7: 
                                status, mark = "MISSING", 0
                            
                            cur.execute("INSERT INTO submission (student_id, assessment_id, submitted_at, status, mark) VALUES (?,?,?,?,?)",
                                        (s["id"], aid, rnd_time(curr_date), status, mark))
                            
                            # Log sample audits (10%) to avoid bloat
                            if random.random() > 0.9:
                                log_audit(cur, "EMP0003", "SUBMIT_GRADE", f"Graded {s['id']} on {aid}: {mark}", rnd_time(curr_date))

        curr_date += timedelta(days=1)

    # 6. Retention Rules
    print("⚙️ Setting Retention Rules...")
    cur.execute("INSERT OR IGNORE INTO retention_rule (rule_id, data_type, retention_months, is_active) VALUES (1, 'RESOLVED_ALERTS', 12, 1)")
    cur.execute("INSERT OR IGNORE INTO retention_rule (rule_id, data_type, retention_months, is_active) VALUES (2, 'GRADUATED_STUDENTS', 48, 1)")

    conn.commit()
    conn.close()
    print("✅ Seed Complete!")

if __name__ == "__main__":
    seed_data()