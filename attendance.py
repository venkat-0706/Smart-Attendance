from flask import Flask, render_template
import pandas as pd
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def dashboard():
    # File paths (use double backslashes or raw string to avoid escape issues)
    total_students_csv = r"D:\cvprojects\Smart Attendace\Source\alert\class data.csv"
    attendance_log_csv = r"D:\cvprojects\Smart Attendace\Source\ai_attendance\attendance_log.csv"
    absentees_csv = r"D:\cvprojects\Smart Attendace\Source\ai_attendance\absentees_list.csv"

    # --- 1. Total Students ---
    df_total = pd.read_csv(total_students_csv)
    total_students = len(df_total)

    # --- 2. Present Students (today only, no duplicates) ---
    df_present = pd.read_csv(attendance_log_csv)
    today = datetime.now().strftime('%Y-%m-%d')
    df_present_today = df_present[df_present['Date'] == today]

    # Remove duplicate roll numbers
    df_present_today = df_present_today.drop_duplicates(subset=['Roll Number'])

    present_count = len(df_present_today)
    present_records = df_present_today.to_dict(orient='records')

    # --- 3. Absent Students ---
    df_absent = pd.read_csv(absentees_csv)
    absent_count = len(df_absent)
    absent_records = df_absent.to_dict(orient='records')

    # --- 4. Attendance Percentage ---
    attendance_percent = round((present_count / total_students) * 100, 2) if total_students else 0

    # Pass values to sai.html
    return render_template(
        "sai.html",
        total_students=total_students,
        present_count=present_count,
        absent_count=absent_count,
        attendance_percent=attendance_percent,
        present_records=present_records,
        absent_records=absent_records
    )

if __name__ == "__main__":
    app.run(debug=True)
