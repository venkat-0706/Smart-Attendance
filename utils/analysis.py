from flask import Flask, render_template
from flask_socketio import SocketIO
import pandas as pd
import os

app = Flask(__name__, template_folder='templates')
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('sample.html')

@socketio.on('request_data')
def handle_request_data():
    # Load the two CSV files
    base_path = r"C:\Users\HP\OneDrive\Documents\Desktop\Smart Attendace\Source\ai_attendance"
    absentees_path = os.path.join(base_path, 'absentees_list.csv')
    attendance_path = os.path.join(base_path, 'attendance_log.csv')

    absentees_df = pd.read_csv(absentees_path)
    attendance_df = pd.read_csv(attendance_path)

    # Convert to dict to send over WebSocket
    absentees_data = absentees_df.to_dict(orient='records')
    attendance_data = attendance_df.to_dict(orient='records')

    # Send to client
    socketio.emit('csv_data', {
        'absentees': absentees_data,
        'attendance': attendance_data
    })

if __name__ == '__main__':
    socketio.run(app, debug=True)
