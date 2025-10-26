from flask import Flask, request, jsonify, render_template, redirect, url_for, send_file
import smtplib
import random
import os
import pandas as pd
import mimetypes
from email.message import EmailMessage
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__, template_folder='templates')
CORS(app)

# Email configuration
EMAIL_ADDRESS = 'attendacnealert@gmail.com'
EMAIL_APP_PASSWORD = 'obdp erpc ymxz anqr'  # Gmail App Password
HOD_EMAIL = 'chanduchandra3458@gmail.com'  # HOD email address updated

# OTP store (temporary, per email)
otp_store = {}

# CSV paths
PRESENT_CSV = 'presenties list.csv'
ABSENT_CSV = 'absentees list.csv'
LATE_COMERS_XLSX = 'Late_comers_List.xlsx'

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
        otp_store.pop(email)  # OTP used, remove it
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Incorrect OTP'}), 401

@app.route('/home')
def home():
    return render_template('sample.html')

# Helper function to extract late comers from present list
def generate_late_comers():
    try:
        df = pd.read_csv(PRESENT_CSV)
        df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S').dt.time
        late_df = df[df['Time'] > datetime.strptime('09:45:00', '%H:%M:%S').time()]
        late_df.to_excel(LATE_COMERS_XLSX, index=False)
    except Exception as e:
        print(f"Error generating late comers: {e}")

# Helper to send email with attachments
def send_email_with_attachments(to_email):
    try:
        generate_late_comers()
        msg = EmailMessage()
        msg['Subject'] = 'Smart Attendance Data'
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg.set_content('Attached are the attendance and late comers reports.')

        for file_path in [PRESENT_CSV, LATE_COMERS_XLSX]:
            if os.path.exists(file_path):
                mime_type, _ = mimetypes.guess_type(file_path)
                mime_type = mime_type or 'application/octet-stream'
                main_type, sub_type = mime_type.split('/', 1)
                with open(file_path, 'rb') as f:
                    msg.add_attachment(f.read(), maintype=main_type, subtype=sub_type, filename=os.path.basename(file_path))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()

        return True
    except Exception as e:
        print(f"Email send error: {e}")
        return False

@app.route('/send-to-mail', methods=['POST'])
def send_attendance():
    try:
        # Get the email from request JSON
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'success': False, 'message': 'No email provided'}), 400

        # Send report to this email
        success = send_email_with_attachments(email)

        if success:
            return jsonify({'success': True, 'message': f"Report sent to {email}"})
        else:
            return jsonify({'success': False, 'message': f"Failed to send report to {email}"})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/send_alerts', methods=['GET'])
def send_absentees_alerts():
    try:
        # Paths to your CSV files
        base_dir = os.path.dirname(os.path.abspath(__file__))
        original_path = os.path.join(base_dir, "alert/class data.csv")
        absent_path = os.path.join(base_dir, "ai_attendance/absentees_list.csv")
        
        # Check if files exist
        if not os.path.exists(original_path) or not os.path.exists(absent_path):
            return jsonify({'success': False, 'message': "CSV files not found!"}), 404

        # Read data
        original_df = pd.read_csv(original_path)
        absentees_df = pd.read_csv(absent_path)

        # Clean columns
        original_df = original_df.loc[:, ~original_df.columns.str.contains('^Unnamed|^\\s*$', regex=True)]
        original_df.columns = original_df.columns.str.strip()
        absentees_df.columns = absentees_df.columns.str.strip()

        # Rename column for merge
        original_df.rename(columns={'E-mail ID': 'email'}, inplace=True)

        # Get absentees only and merge
        absentees_only = absentees_df[absentees_df['Status'].str.lower() == 'absent']
        merged_df = pd.merge(absentees_only, original_df, on='roll_number', how='inner')

        sent_count = 0
        failed_emails = []

        if merged_df.empty:
            return jsonify({'success': False, 'message': "📭 No absent students found."}), 200

        for _, row in merged_df.iterrows():
            student_email = row['email']
            roll = row['roll_number']
            date = row['Date']

            msg = EmailMessage()
            msg['Subject'] = f"Absentee Alert - {date}"
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = student_email
            msg.set_content(f"""Dear Student (Roll No: {roll}),

You were marked ABSENT on {date}. Please ensure regular attendance to avoid academic penalties.

Regards,
Smart Attendance System
""")

            try:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
                    smtp.send_message(msg)
                sent_count += 1
            except Exception as e:
                failed_emails.append(student_email)

        if failed_emails:
            return jsonify({'success': False, 'message': f"❌ Some emails failed: {failed_emails}. {sent_count} sent."}), 200
        return jsonify({'success': True, 'message': f"✅ {sent_count} absentee email(s) sent!"}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f"❌ Server error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
