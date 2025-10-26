from flask import Flask, request, jsonify, render_template, redirect, url_for
import smtplib
import random
from flask_cors import CORS
import pandas as pd
from email.message import EmailMessage
import os

app = Flask(__name__, template_folder='templates')
CORS(app)

EMAIL_ADDRESS = 'attendacnealert@gmail.com'
EMAIL_APP_PASSWORD = 'obdp erpc ymxz anqr'

otp_store = {}


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



if __name__ == '__main__':
    app.run(debug=True)
