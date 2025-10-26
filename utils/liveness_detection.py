import cv2
import dlib
import numpy as np
import torch
import torch.nn.functional as F
from torchvision import transforms

# Import load_model from your model.py
from Source.ai_attendance.models.model import load_model
 # ✅ Correct relative import

# ===== Load Dlib Face Detector & Shape Predictor =====
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(r'C:\Users\HP\OneDrive\Documents\Desktop\Smart Attendace\Source\ai_attendance\models\shape_predictor_68_face_landmarks.dat')

# ===== Load Anti-Spoofing Model =====
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_path = r'C:\Users\HP\OneDrive\Documents\Desktop\Smart Attendace\Source\ai_attendance\models\4_0_0_80x80_MiniFASNetV1SE.pth'
model = load_model(model_path, device)

# ===== Image Preprocessing =====
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((80, 80)),
    transforms.ToTensor(),
])

# ===== Liveness Detection Function =====
def is_real_face(frame, face_rect):
    h, w, _ = frame.shape
    x1, y1 = max(0, face_rect.left()), max(0, face_rect.top())
    x2, y2 = min(w, face_rect.right()), min(h, face_rect.bottom())
    face_img = frame[y1:y2, x1:x2]

    if face_img.size == 0:
        return False

    face_img = cv2.resize(face_img, (80, 80))
    face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
    input_tensor = transform(face_img).unsqueeze(0).to(device)

    with torch.no_grad():
        output = model(input_tensor)
        prob = F.softmax(output, dim=1)[0][1].cpu().item()
        print(f"Liveness Confidence: {prob:.2f}")

    return prob > 0.8

# ===== Start Webcam =====
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face in faces:
        landmarks = predictor(gray, face)

        for n in range(0, 68):
            x, y = landmarks.part(n).x, landmarks.part(n).y
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

        real = is_real_face(frame, face)
        label = "Real" if real else "Spoof"

        cv2.rectangle(frame, (face.left(), face.top()), (face.right(), face.bottom()), (0, 255, 0) if real else (0, 0, 255), 2)
        cv2.putText(frame, label, (face.left(), face.top() - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0) if real else (0, 0, 255), 2)

    cv2.imshow("Liveness Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
