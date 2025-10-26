
# 📸 AI-Powered Smart Attendance System

An intelligent, real-time attendance tracking system using face recognition and liveness detection. Built with Python, OpenCV, Flask, and anti-spoofing techniques, this system automates attendance marking, visualizes data, and enhances accuracy and security by preventing spoofing attacks.


---

## 🧠 Key Features

- 🎯 **Real-Time Face Recognition** – Automatically detects and identifies faces using `face_recognition` and OpenCV.
- 🔐 **Anti-Spoofing / Liveness Detection** – Detects fake attempts using printed photos or mobile screens.
- 📝 **Automated Attendance Logging** – Captures attendance with timestamps and logs into CSV files.
- 📊 **Dashboard Visualization** – Visual representation of attendance statistics.
- 📸 **Face Capture & Storage** – Stores images of users upon verification for audit purposes.
- 🔔 **Email Alerts for Absentees** – Automatically sends alerts to absent students.
- 🌐 **Web Integration** – Flask-powered responsive frontend for real-time display.

---

## 🧰 Tech Stack

| Category            | Tools / Technologies |
|---------------------|----------------------|
| 💻 Programming       | Python, JavaScript   |
| 🧠 AI & CV           | OpenCV, face_recognition, TensorFlow (Anti-Spoofing Models) |
| 🌐 Backend & Server | Flask                |
| 🗃️ Data Processing   | Pandas, NumPy        |
| 📊 Visualization     | Matplotlib / D3.js (optional) |
| 🧪 Testing/Debugging | Jupyter Notebook     |
| 🧾 Storage           | CSV for logs, image directory for captures |
| 📬 Email Services    | SMTP (for alerts)    |
| 🧑‍💻 Frontend         | HTML5, CSS3, JavaScript |
| 🔧 Tools             | Git, GitHub, VS Code |

---

## 📂 Project Structure

```

AI-Smart-Attendance/
│
├── ai\_attendance/
│   ├── face\_data/
│   │   ├── known\_faces/         # Directory with labeled face data
│   │   └── captured\_faces/      # Captured face images of attendees
│   ├── static/
│   │   ├── css/                 # Styling files
│   │   └── js/                  # Scripts
│   ├── templates/
│   │   └── index.html           # Web dashboard
│   ├── app.py                   # Main Flask app
│   ├── anti\_spoofing.py         # Liveness detection logic
│   ├── attendance\_log.csv       # Attendance records
│   └── utils.py                 # Supporting utility functions
│
├── requirements.txt             # All dependencies
├── README.md                    # You are here
└── LICENSE                      # License file

````

---

## 🖥️ How It Works

1. **Face Detection**: Uses OpenCV to detect faces from webcam/video stream.
2. **Face Recognition**: Matches face encodings with known dataset using `face_recognition`.
3. **Liveness Detection**: Runs anti-spoofing model to confirm real presence.
4. **Attendance Logging**: Logs date, time, and student name into a `.csv` file.
5. **Dashboard Display**: Attendance data shown on a Flask-powered webpage.
6. **Email Alert System**: Sends absentee notification via SMTP.

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/your-username/AI-Smart-Attendance.git
cd AI-Smart-Attendance

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
````

---

## ▶️ Usage

```bash
# Run the Flask app
python app.py

# Access the dashboard
Open your browser and go to http://127.0.0.1:5000/
```

---

## 📌 Dependencies

```
flask
opencv-python
face-recognition
numpy
pandas
tensorflow
prettytable
pyttsx3
```

Make sure to install all using:

```bash
pip install -r requirements.txt
```

---

## 📷 Sample Screenshots

| Live Face Recognition                          | Dashboard Overview                      |
| ---------------------------------------------- | --------------------------------------- |
| ![Face Recognition](static/images/sample1.jpg) | ![Dashboard](static/images/sample2.jpg) |

> *(Replace with actual images from your project)*

---

## 💡 Future Enhancements

* 🔒 Facial mask detection integration
* ☁️ Cloud deployment with Firebase or AWS
* 📱 Mobile version of the web interface
* 🧠 Enhanced deep learning-based spoof detection
* 🗂️ MongoDB/SQL database integration

---

## 👨‍💻 Author

**Venkata Chandu**
🎓 B.Tech CSE | Data Science & AI Enthusiast
🔗 [Portfolio](#) • [GitHub](https://github.com/venkat-0706) • [LinkedIn](#) • 📧 [chanduabbireddy247@gmail.com](mailto:chanduabbireddy247@gmail.com)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙌 Support

If you like this project, consider ⭐ starring the repository.
Feel free to open issues or contribute via pull requests!


