import cv2
import face_recognition
import numpy as np
import os
import torch
import torchvision.transforms as transforms
import datetime
import pyttsx3
from prettytable import PrettyTable
from collections import defaultdict
from Source.ai_attendance.models import model as liveness_model_module

# ================== Paths ===================
KNOWN_FACES_DIR = r"Source/ai_attendance/face_data/known_faces"
MINIFASNET_MODEL_PATH = r"Source/ai_attendance/models/4_0_0_80x80_MiniFASNetV1SE.pth"
SHAPE_PREDICTOR_PATH = r"Source/ai_attendance/models/shape_predictor_68_face_landmarks.dat"
CAPTURE_SAVE_DIR = r"Source/ai_attendance/static/captured_faces"

# ================== Load Known Faces ===================
known_face_encodings = []
known_face_names = []

for name in os.listdir(KNOWN_FACES_DIR):
    person_dir = os.path.join(KNOWN_FACES_DIR, name)
    for filename in os.listdir(person_dir):
        img_path = os.path.join(person_dir, filename)
        img = face_recognition.load_image_file(img_path)
        encodings = face_recognition.face_encodings(img)
        if encodings:
            known_face_encodings.append(encodings[0])
            known_face_names.append(name)

# ================== Load Liveness Detection Model ===================
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = liveness_model_module.MiniFASNetV1SE()
checkpoint = torch.load(MINIFASNET_MODEL_PATH, map_location=device)

# Remove 'module.' prefix if needed
new_state_dict = {k.replace('module.', ''): v for k, v in checkpoint.items()}
model.load_state_dict(new_state_dict)
model.to(device)
model.eval()

transform = transforms.Compose([
    transforms.Resize((80, 80)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5])
])

# ================== Initialize ===================
video_capture = cv2.VideoCapture(0)
attendance = defaultdict(lambda: None)
engine = pyttsx3.init()

# ================== Main Loop ===================
while True:
    ret, frame = video_capture.read()
    if not ret:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
        name = "Unknown"

        face_crop = frame[top:bottom, left:right]
        face_resized = cv2.resize(face_crop, (80, 80))
        face_resized = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
        input_tensor = transform(face_resized).unsqueeze(0).to(device)

        with torch.no_grad():
            output = model(input_tensor)
            prob = torch.softmax(output, dim=1)[0][1].item()

        is_live = prob > 0.8

        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]

            if is_live:
                if attendance[name] is None:
                    time_now = datetime.datetime.now().strftime("%H:%M:%S")
                    attendance[name] = time_now
                    engine.say(f"{name} attendance marked at {time_now}")
                    engine.runAndWait()
                color = (0, 255, 0)
                label = f"{name} (Real)"
            else:
                color = (0, 0, 255)
                label = f"{name} (Fake)"
        else:
            color = (0, 0, 255)
            label = "Unknown"

        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    cv2.imshow('Face Recognition with Liveness Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()

# ================== Print Attendance ===================
table = PrettyTable()
table.field_names = ["Name", "Time"]
for name, time in attendance.items():
    if time:
        table.add_row([name, time])

print("\nAttendance Record:\n", table)
