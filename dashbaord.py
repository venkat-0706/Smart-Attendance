from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import smtplib
import random
from flask_cors import CORS
import pandas as pd
from datetime import datetime, timedelta
import os

# --- Flask App ---
app = Flask(__name__, template_folder='templates')
CORS(app)

# Secret key (keep constant, don’t regenerate!)
app.secret_key = "supersecretkey123"

# Session timeout (15 minutes)
app.permanent_session_lifetime = timedelta(minutes=15)

# Email credentials
EMAIL_ADDRESS = 'attendacnealert@gmail.com'
EMAIL_APP_PASSWORD = 'obdp erpc ymxz anqr'   # Gmail App Password

# Store OTPs temporarily
otp_store = {}

# ---------------- LOGIN ROUTES ---------------- #
@app.route('/')
def otp_login():
    return render_template('otp.html')

@app.route('/send-otp', methods=['POST'])
def send_otp():
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'success': False, 'error': 'No email provided'}), 400

        otp = str(random.randint(100000, 999999))
        otp_store[email] = otp

        subject = 'Your Smart Attendance OTP'
        body = f'Your OTP is: {otp}'
        message = f'Subject: {subject}\n\n{body}'

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, email, message)
        server.quit()

        return jsonify({'success': True})
    except Exception as e:
        print("Error:", e)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get("email")
    entered_otp = data.get("otp")

    if not email or not entered_otp:
        return jsonify({'success': False, 'error': 'Missing data'}), 400

    valid_otp = otp_store.get(email)
    if entered_otp == valid_otp:
        otp_store.pop(email, None)  # OTP used, remove it
        session.permanent = True
        session['user'] = email
        return jsonify({'success': True, 'redirect': '/dashboard'})
    else:
        return jsonify({'success': False, 'error': 'Incorrect OTP'}), 401

# ---------------- DASHBOARD ROUTES ---------------- #
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('sai.html'))

    try:
        # File paths (make sure these files exist!)
        total_students_csv = r"D:\cvprojects\Smart Attendace\Source\alert\class data.csv"
        attendance_log_csv = r"D:\cvprojects\Smart Attendace\Source\ai_attendance\attendance_log.csv"
        absentees_csv = r"D:\cvprojects\Smart Attendace\Source\ai_attendance\absentees_list.csv"

        # --- 1. Total Students ---
        df_total = pd.read_csv(total_students_csv)
        total_students = len(df_total)

        # --- 2. Present Students ---
        df_present = pd.read_csv(attendance_log_csv)
        today = datetime.now().strftime('%Y-%m-%d')
        df_present_today = df_present[df_present['Date'] == today]
        df_present_today = df_present_today.drop_duplicates(subset=['Roll Number'])

        present_count = len(df_present_today)
        present_records = df_present_today.to_dict(orient='records')

        # --- 3. Absent Students ---
        df_absent = pd.read_csv(absentees_csv)
        absent_count = len(df_absent)
        absent_records = df_absent.to_dict(orient='records')

        # --- 4. Attendance Percentage ---
        attendance_percent = round((present_count / total_students) * 100, 2) if total_students else 0

        return render_template(
            "sai.html",
            user=session['user'],
            total_students=total_students,
            present_count=present_count,
            absent_count=absent_count,
            attendance_percent=attendance_percent,
            present_records=present_records,
            absent_records=absent_records
        )

    except Exception as e:
        return f"Error loading dashboard: {e}"

@app.route('/home')
def home_redirect():
    return redirect(url_for('dashboard'))

# ---------------- LOGOUT ROUTE ---------------- #
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('otp_login'))

# ---------------- MAIN ---------------- #
if __name__ == '__main__':
    app.run(debug=True)
