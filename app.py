from flask import Flask, request, jsonify, render_template, send_file
import smtplib
import random
import pandas as pd
import os
import threading
import time
from flask_cors import CORS
from io import BytesIO

app = Flask(__name__, template_folder='templates')
CORS(app)

# Email configuration
EMAIL_ADDRESS = 'attendacnealert@gmail.com'
EMAIL_APP_PASSWORD = 'obdp erpc ymxz anqr'  # Gmail App Password

# OTP store (temporary, per email)
otp_store = {}

# CSV file paths
PRESENT_CSV = "C:\Users\HP\OneDrive\Documents\Desktop\Smart Attendace\Source\ai_attendance\attendance_log.csv"
ABSENT_CSV = "C:\Users\HP\OneDrive\Documents\Desktop\Smart Attendace\Source\ai_attendance\absentees_list.csv"

# Automatically delete CSV files after 12 hours
def delete_csv_files_after_12_hours():
    time.sleep(12 * 60 * 60)
    for file in [PRESENT_CSV, ABSENT_CSV]:
        if os.path.exists(file):
            os.remove(file)
            print(f"Deleted: {file}")

threading.Thread(target=delete_csv_files_after_12_hours, daemon=True).start()

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
        otp_store.pop(email)
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Incorrect OTP'}), 401

@app.route('/home')
def home():
    present_records = []
    absent_records = []
    try:
        if os.path.exists(PRESENT_CSV):
            present_df = pd.read_csv(PRESENT_CSV).drop_duplicates()
            present_records = present_df.to_dict(orient='records')
        if os.path.exists(ABSENT_CSV):
            absent_df = pd.read_csv(ABSENT_CSV).drop_duplicates()
            absent_records = absent_df.to_dict(orient='records')
    except Exception as e:
        print("CSV Load Error:", e)

    total_students = len(set([row['Roll Number'] for row in present_records + absent_records]))
    present_count = len(present_records)
    absent_count = len(absent_records)
    attendance_percent = round((present_count / total_students) * 100, 2) if total_students else 0

    return render_template(
        'index.html',
        present_records=present_records,
        absent_records=absent_records,
        total_students=total_students,
        present_count=present_count,
        absent_count=absent_count,
        attendance_percent=attendance_percent
    )

@app.route('/download/presenties-excel')
def download_presenties_excel():
    try:
        df = pd.read_csv(PRESENT_CSV).drop_duplicates()
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        return send_file(output, as_attachment=True, download_name='presenties.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception as e:
        return str(e), 500

@app.route('/download/absentees-excel')
def download_absentees_excel():
    try:
        df = pd.read_csv(ABSENT_CSV).drop_duplicates()
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        return send_file(output, as_attachment=True, download_name='absentees.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception as e:
        return str(e), 500

@app.route('/download/pdf')
def download_pdf():
    try:
        present_df = pd.read_csv(PRESENT_CSV).drop_duplicates()
        absent_df = pd.read_csv(ABSENT_CSV).drop_duplicates()
        combined_df = pd.concat([
            pd.DataFrame({'Status': ['Present'] * len(present_df)}).join(present_df),
            pd.DataFrame({'Status': ['Absent'] * len(absent_df)}).join(absent_df)
        ])
        output = BytesIO()
        combined_df.to_excel(output, index=False)
        output.seek(0)
        return send_file(output, as_attachment=True, download_name='attendance_combined.pdf', mimetype='application/pdf')
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
