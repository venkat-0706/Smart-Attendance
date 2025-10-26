import pandas as pd
import smtplib
from email.message import EmailMessage
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
original_path = os.path.join(base_dir, "../alert/class data.csv")
absent_path = os.path.join(base_dir, "../ai_attendance/absentees_list.csv")

original_df = pd.read_csv(original_path)
absentees_df = pd.read_csv(absent_path)

original_df = original_df.loc[:, ~original_df.columns.str.contains('^Unnamed|^\\s*$', regex=True)]
original_df.columns = original_df.columns.str.strip()
absentees_df.columns = absentees_df.columns.str.strip()

original_df.rename(columns={'E-mail ID': 'email'}, inplace=True)

absentees_only = absentees_df[absentees_df['Status'].str.lower() == 'absent']
merged_df = pd.merge(absentees_only, original_df, on='Roll Number', how='inner')

SENDER_EMAIL = "attendacnealert@gmail.com"
SENDER_PASSWORD = "obdp erpc ymxz anqr"

if merged_df.empty:
    print("📭 No absent students found.")
else:
    print("📨 Sending emails...")

    for _, row in merged_df.iterrows():
        student_email = row['email']
        roll = row['Roll Number']
        date = row['Date']

        msg = EmailMessage()
        msg['Subject'] = f"Absentee Alert - {date}"
        msg['From'] = SENDER_EMAIL
        msg['To'] = student_email
        msg.set_content(f"""Dear Student (Roll No: {roll}),

You were marked ABSENT on {date}. Please ensure regular attendance to avoid academic penalties.

Regards,
Smart Attendance System
""")

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
                smtp.send_message(msg)
            print(f"✅ Email sent to {student_email}")
        except Exception as e:
            print(f"❌ Failed to send email to {student_email}. Error: {e}")
