from flask import Flask, request, jsonify, render_template
import smtplib
import random
import os
import pandas as pd
import mimetypes
from email.message import EmailMessage
from flask_cors import CORS
from datetime import datetime

# Use environment variables for sensitive data (set these in your prod environment!)
# Example: export EMAIL_ADDRESS='your_address@gmail.com'
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS', 'attendacnealert@gmail.com')
EMAIL_APP_PASSWORD = os.getenv('obdp erpc ymxz anqr', 'your_app_password_here')
HOD_EMAIL = 'chanduchandra3458@gmail.com'  # Change as needed

app = Flask(__name__, template_folder='templates')
CORS(app)

otp_store = {}  # email --> otp

# File paths
PRESENT_CSV = 'presenties list.csv'
LATE_COMERS_XLSX = 'Late_comers_List.xlsx'

@app.route('/')
def otp_login():
    return render_template('otp.html')

@app.route('/send-otp', methods=['POST'])
def send_otp():
    try:
        if not request.is_json:
            return jsonify({'success': False, 'error': 'Request must be JSON'}), 400

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
    if not request.is_json:
        return jsonify({'success': False, 'error': 'Request must be JSON'}), 400
    data = request.get_json()
    email = data.get("email")
    entered_otp = data.get("otp")

    if not email or not entered_otp:
        return jsonify({'success': False, 'error': 'Missing data'}), 400

    valid_otp = otp_store.get(email)
    if entered_otp == valid_otp:
        otp_store.pop(email, None)
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Incorrect OTP'}), 401

@app.route('/home')
def home():
    return render_template('sample.html')

def generate_late_comers():
    # This extracts late comers from PRESENT_CSV into an Excel file
    try:
        if not os.path.exists(PRESENT_CSV):
            print(f"File {PRESENT_CSV} does not exist!")
            return
        df = pd.read_csv(PRESENT_CSV)
        if 'Time' not in df.columns:
            print("No 'Time' column in presenties list.")
            return
        df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S', errors='coerce').dt.time
        # Pick times after 09:45:00
        late_df = df[df['Time'] > datetime.strptime('09:45:00', '%H:%M:%S').time()]
        late_df.to_excel(LATE_COMERS_XLSX, index=False)
    except Exception as e:
        print(f"Error generating late comers: {e}")

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

@app.route('/send-to-email', methods=['POST'])
def send_attendance():
    try:
        if not request.is_json:
            return jsonify({'success': False, 'error': 'Request must be JSON'}), 400

        data = request.get_json()
        recipient_type = data.get('recipientType')  # 'hod' or 'faculty'
        if recipient_type == 'hod':
            email = HOD_EMAIL
        else:
            email = data.get('email')

        if not email:
            return jsonify({'success': False, 'error': 'No email provided'}), 400

        success = send_email_with_attachments(email)
        return jsonify({'success': success})
    except Exception as e:
        print(f"Send attendance error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
