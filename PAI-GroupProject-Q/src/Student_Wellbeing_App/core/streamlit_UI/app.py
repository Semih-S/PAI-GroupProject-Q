import streamlit as st
import pandas as pd
import sys
import time
from pathlib import Path
from datetime import date

# --- Path Setup ---
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parents[3]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# --- Imports ---
import data_loader 
from src.Student_Wellbeing_App.core.services.AuthenticationService import AuthenticationService
from src.Student_Wellbeing_App.core.services.StudentService import StudentService
from src.Student_Wellbeing_App.core.services.UserService import UserService
from src.Student_Wellbeing_App.core.services.DashboardService import DashboardService
from src.Student_Wellbeing_App.core.services.WellbeingService import WellbeingService
from src.Student_Wellbeing_App.core.services.AttendanceService import AttendanceService
from src.Student_Wellbeing_App.core.services.AlertService import AlertService
from src.Student_Wellbeing_App.core.services.RetentionService import RetentionService 
from src.Student_Wellbeing_App.core.services.AuditService import AuditService

from src.Student_Wellbeing_App.core.models.UserRole import UserRole
from src.Student_Wellbeing_App.core.models.AttendanceStatus import AttendanceStatus
from src.Student_Wellbeing_App.core.models.SubmissionStatus import SubmissionStatus

# --- Page Config ---
st.set_page_config(page_title="Student Wellbeing System", layout="wide", page_icon="🎓")

# [CACHE DISABLED] to prevent stale data issues during dev
# @st.cache_resource 
def get_services():
    return {
        "auth": AuthenticationService(),
        "student": StudentService(),
        "user": UserService(),
        "dashboard": DashboardService(),
        "wellbeing": WellbeingService(),
        "attendance": AttendanceService(),
        "alert": AlertService(),
        "retention": RetentionService(), 
        "audit": AuditService()
    }

services = get_services()

# --- Session State ---
if 'user_info' not in st.session_state:
    st.session_state.user_info = None

# --- Helper Functions ---
def login(user_id, password):
    result = services["auth"].authenticate_any(user_id, password)
    if result:
        st.session_state.user_info = result
        st.success("Login Successful!")
        st.rerun()
    else:
        st.error("Login Failed: Invalid ID or Password")

def logout():
    st.session_state.user_info = None
    st.rerun()

def handle_registration(fname, lname, email, pwd, year):
    try:
        new_id = services["student"].register_student(fname, lname, email, pwd, year)
        st.success(f"Registration Successful! Your ID: **{new_id}**. Please switch to Login tab.")
    except Exception as e:
        st.error(f"Registration Failed: {e}")

# =========================================================
#  LOGIN / REGISTER SCREEN
# =========================================================
if st.session_state.user_info is None:
    st.title("🎓 Student Wellbeing & Engagement Platform")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("# 🏫")
        st.caption("Data-driven student support system (Real DB Version)")
    
    with col2:
        tab_login, tab_reg = st.tabs(["🔑 Login", "📝 Student Register"])
        
        with tab_login:
            with st.form("login_form"):
                user_id = st.text_input("User ID (e.g. EMP0001, STU0052)")
                password = st.text_input("Password", type="password")
                if st.form_submit_button("Login"):
                    login(user_id, password)
        
        with tab_reg:
            st.info("New Student Registration")
            with st.form("reg_form"):
                f_name = st.text_input("First Name")
                l_name = st.text_input("Last Name")
                email = st.text_input("Email")
                year = st.number_input("Cohort Year", 2020, 2030, 2025)
                pwd = st.text_input("Set Password", type="password")
                if st.form_submit_button("Register"):
                    handle_registration(f_name, l_name, email, pwd, int(year))
    
    st.stop()

# =========================================================
#  MAIN APPLICATION
# =========================================================

current_user = st.session_state.user_info.principal
user_kind = st.session_state.user_info.kind
user_role = current_user.role if user_kind == 'user' else None
current_uid = current_user.user_id if user_kind == 'user' else current_user.student_id

# --- Sidebar ---
with st.sidebar:
    st.markdown("## 👤 User Profile")
    lname = getattr(current_user, 'lastname', getattr(current_user, 'last_name', ''))
    st.write(f"**{current_user.first_name} {lname}**")
    
    role_label = user_role.value if user_role else "Student"
    st.caption(f"Role: {role_label}")
    
    uid = current_user.student_id if user_kind=='student' else current_user.user_id
    st.caption(f"ID: {uid}")
    
    st.divider()
    if st.button("🚪 Logout"):
        logout()

# ---------------------------------------------------------
#  VIEW 1: COURSE DIRECTOR (Teacher)
# ---------------------------------------------------------
if user_kind == 'user' and user_role == UserRole.COURSE_DIRECTOR:
    st.title("📚 Course Director Dashboard")
    
    # [REAL DB] Fetch modules assigned to this specific teacher
    my_courses = services["dashboard"].get_teacher_modules(current_user.user_id)
    
    if not my_courses:
        st.error("🚫 You are not assigned to any modules.")
        st.info("Please contact an Admin (e.g. EMP0010) to assign you to a module via the 'Course Management' tab.")
    else:
        selected_module = st.selectbox("Select Module", my_courses)
        
        # Tabs
        tab_overview, tab_attendance, tab_assessment = st.tabs(["📊 Overview", "📝 Attendance", "🎓 Assessments & Grades"])

        # --- Tab 1: Overview ---
        with tab_overview:
            stats = services["dashboard"].get_module_stats(selected_module)
            k1, k2, k3 = st.columns(3)
            k1.metric("Avg Attendance", f"{stats['avg_attendance']}%")
            k2.metric("Total Sessions", stats['total_sessions'])
            k3.metric("Absences", stats['absent_count'], delta_color="inverse")
            
            st.divider()
            st.subheader("📈 Correlation: Attendance vs Grades")
            
            # pass selected_module to data_loader
            df_academic = data_loader.load_academic_data(selected_module)
            if not df_academic.empty:
                st.scatter_chart(df_academic, x='present_count', y='avg_mark', color='#FF0000', size=50)
            else:
                st.warning("Not enough data to generate chart.")

        # --- Tab 2: Attendance (Interactive) ---
        with tab_attendance:
            st.subheader(f"Attendance Log: {selected_module}")
            
            if "att_editor_key" not in st.session_state:
                st.session_state.att_editor_key = 0

            # --- Upper Part: Quick Add Form ---
            enrolled_students_for_att = services["dashboard"].get_enrolled_students(selected_module)
            with st.expander("➕ Record New Attendance (Single Entry)"):
                if not enrolled_students_for_att:
                    st.warning("No students enrolled.")
                else:
                    with st.form("add_att_form"):
                        c1, c2 = st.columns(2)
                        s_id = c1.selectbox("Select Student", enrolled_students_for_att)
                        att_date = c2.date_input("Date", date.today())
                        att_status = st.selectbox("Status", [s.value for s in AttendanceStatus])
                        
                        if st.form_submit_button("Add Record"):
                            try:
                                services["attendance"].record_attendance(s_id, att_date, selected_module, AttendanceStatus(att_status), performed_by=current_user.user_id)
                                st.success(f"Added: {s_id} - {att_status}")
                                st.session_state.att_editor_key += 1
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
            
            st.divider()

            # --- Lower Part: Interactive Table ---
            st.markdown("#### 📋 Manage Records (Edit or Delete)")
            
            raw_records = services["dashboard"].get_module_attendance_records(selected_module)
            
            if raw_records:
                df = pd.DataFrame(raw_records)
                
                editor_key = f"att_editor_{st.session_state.att_editor_key}"
                
                edited_df = st.data_editor(
                    df,
                    column_config={
                        "id": None, # Hide ID
                        "student_id": st.column_config.TextColumn("Student ID", disabled=True),
                        "date": st.column_config.DateColumn("Date", disabled=True),
                        "status": st.column_config.SelectboxColumn(
                            "Status",
                            options=[s.value for s in AttendanceStatus],
                            required=True
                        )
                    },
                    num_rows="dynamic",
                    key=editor_key,
                    use_container_width=True
                )

                if st.button("💾 Save Changes", key="save_att_btn"):
                    try:
                        changes = st.session_state[editor_key]
                        updates_made = False

                        if changes["deleted_rows"]:
                            for idx in changes["deleted_rows"]:
                                record_id = int(df.iloc[idx]["id"])
                                services["attendance"].delete_attendance(record_id, performed_by=current_user.user_id)
                            updates_made = True
                            st.toast(f"Deleted {len(changes['deleted_rows'])} rows", icon="🗑️")

                        if changes["edited_rows"]:
                            for idx, row_changes in changes["edited_rows"].items():
                                if "status" in row_changes:
                                    record_id = int(df.iloc[int(idx)]["id"])
                                    new_status = row_changes["status"]
                                    services["attendance"].update_attendance_status(record_id, new_status, performed_by=current_user.user_id)
                            updates_made = True
                            st.toast("Status updated", icon="✏️")

                        if updates_made:
                            st.session_state.att_editor_key += 1
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.info("No changes detected.")

                    except Exception as e:
                        st.error(f"Save failed: {e}")
            else:
                st.info("No records found.")

        # --- Tab 3: Assessments & Grades (Interactive) ---
        with tab_assessment:
            st.subheader(f"Assessment Management: {selected_module}")
            
            if "grade_editor_key" not in st.session_state:
                st.session_state.grade_editor_key = 0

            # 1. Publish
            with st.expander("➕ Publish New Assessment / Exam"):
                with st.form("new_assess_form"):
                    c1, c2 = st.columns(2)
                    title = c1.text_input("Title (e.g. Midterm)")
                    weight = c2.number_input("Weight (%)", 0, 100, 20)
                    due = st.date_input("Due Date", date.today())
                    
                    if st.form_submit_button("Publish"):
                        services["dashboard"].create_assessment(selected_module, title, due, weight)
                        st.success("Assessment Published!")
                        st.rerun()

            st.divider()

            # 2. Select Assessment
            assessments = services["dashboard"].get_module_assessments(selected_module)
            
            if not assessments:
                st.info("No assessments created yet.")
            else:
                assess_options = {a.assessment_id: f"{a.title} (Due: {a.due_date})" for a in assessments}
                selected_assess_id = st.selectbox("Select Assessment to Grade", list(assess_options.keys()), format_func=lambda x: assess_options[x])
                
                st.markdown("---")

                # --- A. Quick Form ---
                enrolled_students = services["dashboard"].get_enrolled_students(selected_module)
                with st.expander("➕ Record Grade (Single Student)", expanded=True):
                    if not enrolled_students:
                        st.warning("No students enrolled.")
                    else:
                        with st.form("grade_upsert_form"):
                            c1, c2 = st.columns(2)
                            stu_id = c1.selectbox("Select Student", enrolled_students)
                            mark_in = c2.number_input("Mark (0-100)", 0.0, 100.0, step=1.0)
                            
                            if st.form_submit_button("Save Grade"):
                                services["dashboard"].submit_grade(stu_id, int(selected_assess_id), mark_in)
                                st.success(f"Saved: {stu_id} -> {mark_in}")
                                st.session_state.grade_editor_key += 1
                                st.rerun()

                # --- B. Grade Book ---
                st.markdown(f"#### 📋 Grade Book: {assess_options[selected_assess_id]}")
                
                grades_data = services["dashboard"].get_assessment_grades(int(selected_assess_id))
                
                if grades_data:
                    df_grades = pd.DataFrame(grades_data)
                    editor_key = f"grade_editor_{st.session_state.grade_editor_key}"

                    edited_df = st.data_editor(
                        df_grades,
                        column_config={
                            "id": None,
                            "student_id": st.column_config.TextColumn("Student", disabled=True),
                            "mark": st.column_config.NumberColumn("Mark", min_value=0, max_value=100),
                            "status": st.column_config.TextColumn("Status", disabled=True)
                        },
                        num_rows="dynamic",
                        key=editor_key,
                        use_container_width=True
                    )

                    if st.button("💾 Save Grade Changes"):
                        try:
                            changes = st.session_state[editor_key]
                            updates_made = False

                            if changes["deleted_rows"]:
                                for idx in changes["deleted_rows"]:
                                    sub_id = int(df_grades.iloc[idx]["id"])
                                    services["dashboard"].delete_grade_entry(sub_id)
                                updates_made = True
                                st.toast(f"Deleted {len(changes['deleted_rows'])} records", icon="🗑️")

                            if changes["edited_rows"]:
                                for idx, row_changes in changes["edited_rows"].items():
                                    if "mark" in row_changes:
                                        sub_id = int(df_grades.iloc[int(idx)]["id"])
                                        new_mark = float(row_changes["mark"])
                                        services["dashboard"].update_grade_direct(sub_id, new_mark)
                                updates_made = True
                                st.toast("Grades updated", icon="✏️")

                            if updates_made:
                                st.session_state.grade_editor_key += 1
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.info("No changes detected.")

                        except Exception as e:
                            st.error(f"Error: {e}")
                else:
                    st.info("No grades recorded yet.")

# ---------------------------------------------------------
#  VIEW 2: WELLBEING OFFICER & ADMIN
# ---------------------------------------------------------
elif user_kind == 'user' and user_role in [UserRole.WELLBEING_OFFICER, UserRole.ADMIN]:
    title = "👮 Admin Console" if user_role == UserRole.ADMIN else "❤️ Wellbeing Center"
    st.title(title)
    
    tabs = st.tabs(["⚠️ Alert Monitor", "🔍 Student Search", "📝 Reports", "📚 Course Management", "⚙️ Data Retention", "🛡️ Audit Logs"])
    
    # --- Tab 1: Alert Monitor ---
    with tabs[0]:
        st.subheader("⚠️ Alert Monitor Dashboard")
        col_active, col_history = st.columns(2)
        
        with col_active:
            st.markdown("### 🔴 Pending Actions")
            active_alerts = services["alert"].get_active_alerts()
            if not active_alerts:
                st.success("No active alerts! All clear.")
            else:
                for a in active_alerts:
                    with st.container(border=True):
                        st.markdown(f"**{a.alert_type}**")
                        st.markdown(f"👤 `{a.student_id}`")
                        st.caption(f"📝 {a.reason}")
                        st.caption(f"📅 {a.created_at}")
                        if st.button("Mark Resolved ✅", key=f"res_{a.alert_id}"):
                            try:
                                services["alert"].resolve_alert(a.alert_id)
                                st.toast(f"Alert {a.alert_id} resolved!")
                                time.sleep(0.5)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")

        with col_history:
            st.markdown("### 🟢 Resolved History")
            resolved_alerts = services["alert"].get_resolved_alerts()
            if resolved_alerts:
                history_data = [{"Student": a.student_id, "Type": a.alert_type, "Reason": a.reason, "Date": a.created_at} for a in resolved_alerts]
                st.dataframe(pd.DataFrame(history_data), use_container_width=True, hide_index=True)
            else:
                st.info("No resolved history yet.")

    # --- Tab 2: Search ---
    with tabs[1]:
        st.subheader("Student Profile Search")
        all_students = services["student"].list_students()
        q = st.text_input("Search Name/ID").lower()
        filtered = [s for s in all_students if q in s.student_id.lower() or q in s.first_name.lower()] if q else all_students
        opts = {s.student_id: f"{s.first_name} {s.lastname} ({s.student_id})" for s in filtered}
        
        sel_sid = st.selectbox("Select Student", list(opts.keys()), format_func=lambda x: opts[x]) if opts else None
        
        if sel_sid:
            stu = services["student"].get_student_by_id(sel_sid)
            st.divider()
            st.markdown(f"### 👤 {stu.first_name} {stu.lastname} ({stu.student_id})")
            
            trend = services["dashboard"].get_student_wellbeing_trend(sel_sid)
            att_records = services["attendance"].get_attendance_for_student(sel_sid)
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### 🧠 Stress Trend")
                if trend['dates']:
                    st.line_chart(pd.DataFrame(trend), x='dates', y='stress', color='#FF4B4B')
                else:
                    st.warning("No wellbeing data found.")
            with c2:
                st.markdown("#### 💤 Sleep History (Hours)")
                if trend['dates']:
                    st.bar_chart(pd.DataFrame(trend), x='dates', y='sleep', color='#0068C9')
                else:
                    st.warning("No wellbeing data found.")

            st.divider()
            st.markdown("#### 📅 Attendance Overview")
            if att_records:
                att_data = [{"Date": r.session_date, "Status": r.status.value, "Session": r.session_id} for r in att_records]
                df_att = pd.DataFrame(att_data)
                
                ac1, ac2 = st.columns([2, 1])
                with ac1:
                    status_counts = df_att['Status'].value_counts()
                    st.bar_chart(status_counts, color='#00CC96')
                with ac2:
                    total = len(att_records)
                    absent = len([r for r in att_records if r.status.value == "ABSENT"])
                    rate = round(((total - absent) / total) * 100, 1)
                    st.metric("Attendance Rate", f"{rate}%", f"Total Entries: {total}")
                
                with st.expander("View Detailed Attendance Log"):
                    st.dataframe(df_att, use_container_width=True)
            else:
                st.info("No attendance records found for this student.")

    # --- Tab 3: Reports & Analytics ---
    with tabs[2]:
        st.subheader("📊 Global Analytics & Reporting")
        
        st.markdown("#### 1. Wellbeing Trends (Whole School)")
        df_trends = data_loader.load_aggregate_wellbeing_trend()
        if not df_trends.empty:
            c1, c2 = st.columns(2)
            with c1:
                st.caption("Average Stress Level")
                st.line_chart(df_trends, x='week_start', y='avg_stress', color='#FF4B4B')
            with c2:
                st.caption("Average Sleep Hours")
                st.bar_chart(df_trends, x='week_start', y='avg_sleep', color='#0068C9')
        else:
            st.info("Not enough data.")

        st.divider()
        st.markdown("#### 2. Module Performance")
        df_course = data_loader.load_course_performance_summary()
        if not df_course.empty:
            st.dataframe(
                df_course, 
                column_config={
                    "module_code": "Module",
                    "avg_mark": st.column_config.ProgressColumn("Avg Mark", min_value=0, max_value=100, format="%.1f"),
                    "attendance_rate": st.column_config.ProgressColumn("Attendance %", min_value=0, max_value=100, format="%.1f%%")
                },
                use_container_width=True
            )
        else:
            st.info("No academic data.")

        st.divider()
        # --- 3. Export Data ---
        st.markdown("#### 3. Export Comprehensive Student Report")
        st.caption("Download a CSV containing academic, attendance, and wellbeing metrics. **'Risk Status'** is automatically calculated based on thresholds.")
        
        df_export = data_loader.load_full_export_data()
        
        if not df_export.empty:
            # CSV Download Button
            csv = df_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Full Report (with Wellbeing Risks)",
                data=csv,
                file_name=f"student_wellbeing_report_{date.today()}.csv",
                mime="text/csv",
                type="primary"
            )
            
            # Enhanced Preview Table
            with st.expander("👁️ Preview Report Data"):
                st.dataframe(
                    df_export,
                    column_config={
                        "student_id": "ID",
                        "Risk_Status": st.column_config.TextColumn("Risk Flags", help="Auto-generated flags for Stress>4, Sleep<6h, or Low Attendance"),
                        "avg_stress": st.column_config.ProgressColumn("Avg Stress (1-5)", min_value=1, max_value=5, format="%.1f"),
                        "avg_sleep": st.column_config.NumberColumn("Avg Sleep (h)", format="%.1f h"),
                        "attendance_pct": st.column_config.NumberColumn("Attendance %", format="%.1f%%"),
                        "avg_grade": st.column_config.NumberColumn("Avg Grade", format="%.1f")
                    },
                    use_container_width=True
                )
        else:
            st.warning("No data available to export.")

    # --- Tab 4: Course Management ---
    with tabs[3]:
        st.subheader("⚙️ Curriculum & Enrollment Management")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("#### 1. Add Module")
            with st.form("add_mod_form"):
                m_code = st.text_input("Code (e.g. CS101)")
                m_title = st.text_input("Title")
                if st.form_submit_button("Create Module"):
                    services["dashboard"].create_new_module(m_code, m_title)
                    st.success(f"Created {m_code}")
        with c2:
            st.markdown("#### 2. Assign Teacher")
            with st.form("assign_teach_form"):
                t_id = st.text_input("Teacher ID") 
                m_code_t = st.text_input("Module Code")
                if st.form_submit_button("Assign"):
                    services["dashboard"].assign_teacher_to_module(t_id, m_code_t)
                    st.success(f"Assigned {t_id}")
        with c3:
            st.markdown("#### 3. Enroll Student")
            with st.form("enroll_stu_form"):
                s_id = st.text_input("Student ID")
                m_code_s = st.text_input("Module Code")
                if st.form_submit_button("Enroll"):
                    services["dashboard"].enroll_student_to_module(s_id, m_code_s)
                    st.success(f"Enrolled {s_id}")

    # --- Tab 5: Data Retention Policy ---
    with tabs[4]:
        st.subheader("⚙️ Data Retention & Privacy Policy")
        st.info("Manage data lifecycle rules.")
        
        rules = services["retention"].get_all_rules()
        
        st.markdown("#### 1. Manage Rules")
        # Rule Editor
        with st.expander("📝 Edit Existing Rules", expanded=True):
            rule_data = [{"ID": r.rule_id, "Type": r.data_type, "Months": r.retention_months, "Active": bool(r.is_active)} for r in rules]
            df_rules = pd.DataFrame(rule_data)
            edited_rules = st.data_editor(
                df_rules,
                column_config={
                    "ID": st.column_config.NumberColumn(disabled=True),
                    "Type": st.column_config.TextColumn(disabled=True),
                    "Months": st.column_config.NumberColumn(min_value=1, max_value=120),
                    "Active": st.column_config.CheckboxColumn(label="Active?")
                },
                use_container_width=True,
                key="retention_editor"
            )
            
            if st.button("💾 Save Rule Changes"):
                for index, row in edited_rules.iterrows():
                    services["retention"].update_rule_settings(int(row["ID"]), int(row["Months"]), bool(row["Active"]))
                st.success("Settings updated!")
                time.sleep(0.5)
                st.rerun()

        # Create/Delete
        c_add, c_del = st.columns(2)
        with c_add:
            with st.expander("➕ Add New Rule"):
                with st.form("add_rule_form"):
                    new_type = st.selectbox("Data Type", ["RESOLVED_ALERTS", "GRADUATED_STUDENTS"])
                    new_months = st.number_input("Months", 1, 120, 12)
                    if st.form_submit_button("Add Rule"):
                        services["retention"].create_rule(new_type, new_months, True)
                        st.success("Rule Added!")
                        st.rerun()
        with c_del:
            with st.expander("🗑️ Delete Rule"):
                with st.form("del_rule_form"):
                    rule_opts = {r.rule_id: f"{r.data_type} ({r.retention_months}m)" for r in rules}
                    sel_del_id = st.selectbox("Select Rule", list(rule_opts.keys()), format_func=lambda x: rule_opts[x])
                    if st.form_submit_button("Delete Selected Rule"):
                        services["retention"].delete_rule(sel_del_id)
                        st.warning(f"Rule {sel_del_id} Deleted.")
                        st.rerun()

        st.divider()
        st.markdown("#### 2. Safe Cleanup Execution")
        rule_map = {r.rule_id: f"ID {r.rule_id}: {r.data_type} (> {r.retention_months} months)" for r in rules if r.is_active}
        
        if not rule_map:
            st.warning("No active rules.")
        else:
            selected_rule_id = st.selectbox("Select Active Rule to Run", list(rule_map.keys()), format_func=lambda x: rule_map[x])
            
            if "preview_df" not in st.session_state: st.session_state.preview_df = None
            if st.button("🔍 Preview Data to be Deleted"):
                df_preview = services["retention"].get_preview_dataframe(selected_rule_id)
                st.session_state.preview_df = df_preview
                if df_preview.empty:
                    st.info("✅ No matching data found.")
                else:
                    st.error(f"⚠️ Found {len(df_preview)} records!")
            
            if st.session_state.preview_df is not None and not st.session_state.preview_df.empty:
                st.dataframe(st.session_state.preview_df, use_container_width=True)
                if st.button("🗑️ CONFIRM DELETE", type="primary"):
                    deleted_count = services["retention"].execute_specific_rule(selected_rule_id)
                    st.success(f"Deleted {deleted_count} records.")
                    st.session_state.preview_df = None
                    time.sleep(1.5)
                    st.rerun()

    # --- Tab 6: Audit Logs ---
    with tabs[5]:
        st.subheader("🛡️ System Audit Logs")
        st.info("Tracking critical actions (Seed data simulates history).")
        
        logs = services["audit"].get_logs()
        if logs:
            df_logs = pd.DataFrame(logs)
            st.dataframe(
                df_logs,
                column_config={
                    "log_id": st.column_config.NumberColumn("ID", width="small"),
                    "user_id": st.column_config.TextColumn("User", width="medium"),
                    "action": st.column_config.TextColumn("Action", width="medium"),
                    "details": st.column_config.TextColumn("Details", width="large"),
                    "timestamp": st.column_config.DatetimeColumn("Time", format="D MMM YYYY, h:mm a")
                },
                use_container_width=True,
                hide_index=True
            )
            if st.button("🔄 Refresh Logs"):
                st.rerun()
        else:
            st.info("Audit log is empty.")

# ---------------------------------------------------------
#  VIEW 3: STUDENT VIEW
# ---------------------------------------------------------
elif user_kind == 'student':
    sid = current_user.student_id
    st.title(f"My Wellbeing Dashboard ({sid})")
    
    rate = services["dashboard"].calculate_attendance_rate(sid)
    c1, c2, c3 = st.columns(3)
    c1.metric("Attendance Rate", f"{rate}%")
    c2.metric("Cohort Year", current_user.year)
    c3.metric("Status", "Active")
    
    st.divider()
    
    today = date.today()
    current_week_start = today - pd.Timedelta(days=today.weekday())
    with st.expander("➕ Submit This Week's Survey", expanded=True):
        with st.form("survey_form"):
            st.caption(f"Recording for week of: {current_week_start}")
            s = st.slider("Stress Level (1-Low to 5-High)", 1, 5, 3)
            sl = st.number_input("Sleep Hours (avg per night)", 0.0, 12.0, 7.0, step=0.5)
            if st.form_submit_button("Submit"):
                try:
                    services["wellbeing"].add_or_update_record(sid, current_week_start, s, sl)
                    st.toast("✅ Recorded successfully!", icon="🎉")
                    time.sleep(0.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    st.divider()

    col_hist, col_viz = st.columns([1, 1])
    records = services["wellbeing"].get_records_for_student(sid)
    
    with col_hist:
        st.subheader("📋 My History")
        if records:
            df_hist = pd.DataFrame([vars(r) for r in records])
            df_hist["stress_level"] = pd.to_numeric(df_hist["stress_level"], errors='coerce').fillna(3).astype(int)
            df_hist["sleep_hours"] = pd.to_numeric(df_hist["sleep_hours"], errors='coerce').fillna(7.0).astype(float)
            
            df_display = df_hist[["record_id", "week_start", "stress_level", "sleep_hours"]]
            
            if "wb_editor_key" not in st.session_state: st.session_state.wb_editor_key = 0
            
            edited_wb = st.data_editor(
                df_display,
                column_config={
                    "record_id": None,
                    "week_start": st.column_config.DateColumn("Week Of", disabled=True, format="YYYY-MM-DD"),
                    "stress_level": st.column_config.NumberColumn("Stress (1-5)", min_value=1, max_value=5),
                    "sleep_hours": st.column_config.NumberColumn("Sleep (h)", min_value=0, max_value=12)
                },
                num_rows="dynamic",
                key=f"wb_editor_{st.session_state.wb_editor_key}",
                use_container_width=True
            )
            
            if st.button("💾 Save History Changes"):
                changes = st.session_state[f"wb_editor_{st.session_state.wb_editor_key}"]
                has_changes = False
                
                for idx in changes["deleted_rows"]:
                    rec_id = df_display.iloc[idx]["record_id"]
                    rec_date = df_display.iloc[idx]["week_start"]
                    if services["wellbeing"].is_editable(rec_date):
                        services["wellbeing"].delete_record(int(rec_id))
                        has_changes = True
                    else:
                        st.warning(f"Cannot delete past week record: {rec_date}")

                for idx, row_changes in changes["edited_rows"].items():
                    rec_id = df_display.iloc[int(idx)]["record_id"]
                    rec_date = df_display.iloc[int(idx)]["week_start"]
                    if services["wellbeing"].is_editable(rec_date):
                        curr_stress = df_display.iloc[int(idx)]["stress_level"]
                        curr_sleep = df_display.iloc[int(idx)]["sleep_hours"]
                        new_stress = row_changes.get("stress_level", curr_stress)
                        new_sleep = row_changes.get("sleep_hours", curr_sleep)
                        services["wellbeing"].update_record_direct(int(rec_id), new_stress, new_sleep)
                        has_changes = True
                    else:
                        st.warning(f"Cannot edit past week record: {rec_date}")

                if has_changes:
                    st.success("Changes saved!")
                    st.session_state.wb_editor_key += 1
                    time.sleep(0.5)
                    st.rerun()
        else:
            st.info("No records found.")

    with col_viz:
        st.subheader("📈 My Insights")
        trend = services["dashboard"].get_student_wellbeing_trend(sid)
        att_records = services["attendance"].get_attendance_for_student(sid)
        att_df = pd.DataFrame([vars(r) for r in att_records])
        
        t1, t2, t3 = st.tabs(["Stress", "Sleep", "Attendance"])
        with t1:
            if trend['dates']: st.line_chart(pd.DataFrame(trend), x='dates', y='stress', color='#FF4B4B')
            else: st.info("No stress data.")
        with t2:
            if trend['dates']: st.bar_chart(pd.DataFrame(trend), x='dates', y='sleep', color='#0068C9')
            else: st.info("No sleep data.")
        with t3:
            if not att_df.empty:
                status_counts = att_df['status'].value_counts()
                st.bar_chart(status_counts, color='#00CC96')
                st.caption(f"Total entries: {len(att_df)}")
            else: st.info("No attendance records.")