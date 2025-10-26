import face_recognition
import cv2
import os
import numpy as np
import datetime
import pyttsx3
import csv
from prettytable import PrettyTable
from PIL import Image
from pathlib import Path

# === Paths ===
# Define base project directory using an absolute path
BASE_DIR = Path("Smart Attendace/Source/ai_attendance")

KNOWN_FACES_DIR = BASE_DIR / "face_data" / "known_faces"
CAPTURE_SAVE_DIR = BASE_DIR / "static" / "captured_faces"
CSV_LOG_PATH = BASE_DIR / "attendance_log.csv"
ABSENTEES_PATH = BASE_DIR / "absentees_list.csv"

os.makedirs(CAPTURE_SAVE_DIR, exist_ok=True)

# === Text-to-Speech ===
engine = pyttsx3.init()
engine.setProperty('rate', 170)

def speak(text):
    engine.say(text)
    engine.runAndWait()

# === Load Known Faces ===
known_encodings = []
known_names = []
print("[INFO] Loading known faces...")

for filename in os.listdir(KNOWN_FACES_DIR):
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):
        path = os.path.join(KNOWN_FACES_DIR, filename)

        try:
            # Force every image into 8-bit RGB
            img = Image.open(path).convert("RGB")
            image = np.array(img, dtype=np.uint8)

            # Get encodings
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_encodings.append(encodings[0])
                known_names.append(os.path.splitext(filename)[0])
            else:
                print(f"[WARNING] No face detected in {filename}")

        except Exception as e:
            print(f"[ERROR] Could not process {filename}: {e}")

# === Attendance Setup ===
attendance_records = []
attendance_marked = set()
attendance_count = {}
today_date = datetime.datetime.now().strftime("%Y-%m-%d")
detection_start_time = {}

# === CSV Init ===
if not os.path.exists(CSV_LOG_PATH):
    with open(CSV_LOG_PATH, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Roll Number", "Date", "Time", "Status"])

# === Anti-Spoof Detection (LBP) ===
def extract_lbp_features(gray_face):
    lbp = np.zeros_like(gray_face)
    for i in range(1, gray_face.shape[0] - 1):
        for j in range(1, gray_face.shape[1] - 1):
            center = gray_face[i, j]
            binary = ''
            binary += '1' if gray_face[i - 1, j - 1] >= center else '0'
            binary += '1' if gray_face[i - 1, j] >= center else '0'
            binary += '1' if gray_face[i - 1, j + 1] >= center else '0'
            binary += '1' if gray_face[i, j + 1] >= center else '0'
            binary += '1' if gray_face[i + 1, j + 1] >= center else '0'
            binary += '1' if gray_face[i + 1, j] >= center else '0'
            binary += '1' if gray_face[i + 1, j - 1] >= center else '0'
            binary += '1' if gray_face[i, j - 1] >= center else '0'
            lbp[i, j] = int(binary, 2)
    hist, _ = np.histogram(lbp.ravel(), bins=np.arange(257), density=True)
    return hist

def is_real_face(lbp_features):
    return lbp_features[0] > 0.01  # simple heuristic

# === Start Webcam ===
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("[ERROR] Webcam not accessible.")
    exit()

print("[INFO] Starting face recognition... Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        top_exp, right_exp, bottom_exp, left_exp = [v * 4 for v in (top, right, bottom, left)]
        face_img = frame[top_exp:bottom_exp, left_exp:right_exp]

        # === Anti-Spoof Check ===
        try:
            face_gray = cv2.cvtColor(cv2.resize(face_img, (64, 64)), cv2.COLOR_BGR2GRAY)
            lbp_features = extract_lbp_features(face_gray)
            if not is_real_face(lbp_features):
                label = "Spoof Detected"
                cv2.putText(frame, label, (left_exp, top_exp - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.rectangle(frame, (left_exp, top_exp), (right_exp, bottom_exp), (0, 0, 255), 2)
                speak("Spoof attempt detected. Face ignored.")
                continue
        except Exception as e:
            print("[ERROR] Anti-spoofing failed:", e)
            continue

        # === Face Recognition ===
        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        distances = face_recognition.face_distance(known_encodings, face_encoding)
        name = "Unknown"

        if distances.size > 0:
            best_index = np.argmin(distances)
            if matches[best_index] and distances[best_index] < 0.45:
                name = known_names[best_index]

                # === 2-Second Detection Timer ===
                current_time = datetime.datetime.now()
                if name not in detection_start_time:
                    detection_start_time[name] = current_time
                else:
                    duration = (current_time - detection_start_time[name]).total_seconds()
                    if duration >= 2 and name not in attendance_marked:
                        time_str = current_time.strftime("%H:%M:%S")
                        timestamp = current_time.strftime("%Y%m%d_%H%M%S")

                        img_path = os.path.join(CAPTURE_SAVE_DIR, f"{name}_{timestamp}.jpg")
                        cv2.imwrite(img_path, face_img)

                        attendance_marked.add(name)
                        attendance_count[name] = attendance_count.get(name, 0) + 1
                        attendance_records.append([name, today_date, "Attended", time_str])
                        speak(f"Attendance captured for {name}")

                        with open(CSV_LOG_PATH, 'a', newline='') as f:
                            csv.writer(f).writerow([name, today_date, time_str, "Attended"])
                    elif name in attendance_marked:
                        speak(f"{name}, your attendance has already been captured.")
            else:
                detection_start_time.pop(name, None)

        # Draw rectangle and label
        cv2.rectangle(frame, (left_exp, top_exp), (right_exp, bottom_exp), (0, 255, 0), 2)
        cv2.putText(frame, name, (left_exp, bottom_exp + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow("Smart Attendance System", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# === Save Absentees List ===
absentees = [name for name in known_names if name not in attendance_marked]
if absentees:
    with open(ABSENTEES_PATH, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Roll Number", "Date", "Status"])
        for name in absentees:
            writer.writerow([name, today_date, "Absent"])

# === Display Attendance Summary ===
print("\n✅ Final Attendance Record:")
table = PrettyTable(["Roll Number", "Date", "Status", "Time", "Count"])
for row in attendance_records:
    name = row[0]
    count = attendance_count.get(name, 1)
    table.add_row(row + [count])
print(table)

if absentees:
    print("\n❌ Absentees List:")
    absent_table = PrettyTable(["Roll Number", "Date", "Status"])
    for name in absentees:
        absent_table.add_row([name, today_date, "Absent"])
    print(absent_table)

cap.release()
cv2.destroyAllWindows()
engine.stop()
