import pandas as pd
import matplotlib.pyplot as plt
import os

# Define base directory
base_dir = os.path.join("C:", os.sep, "Users", "HP", "OneDrive", "Documents",
                        "Desktop", "Smart Attendace", "Source", "ai_attendance")

# Define file paths using os.path
class_data_path = os.path.join(base_dir, "alert", "class data.csv")
attendance_log_path = os.path.join(base_dir, "attendance_log.csv")
absentees_list_path = os.path.join(base_dir, "absentees_list.csv")

# Load data
df_class = pd.read_csv(class_data_path)
df_attendance = pd.read_csv(attendance_log_path)
df_absentees = pd.read_csv(absentees_list_path)

# Clean and normalize data
df_class['Gender'] = df_class['Gender'].str.strip().str.lower()
df_attendance['Gender'] = df_attendance['Gender'].str.strip().str.lower()
df_absentees['Gender'] = df_absentees['Gender'].str.strip().str.lower()

# Drop duplicates
df_class = df_class.drop_duplicates()
df_attendance = df_attendance.drop_duplicates()
df_absentees = df_absentees.drop_duplicates()

# Function for label formatting in pie charts
def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        count = int(round(pct*total/100.0))
        return f'{pct:.1f}%\n({count})'
    return my_autopct

# Create a 1x3 subplot for pie charts
fig, axs = plt.subplots(1, 3, figsize=(18, 6))

# Pie 1: Class Strength by Gender
gender_counts_class = df_class['Gender'].value_counts()
axs[0].pie(gender_counts_class, labels=gender_counts_class.index,
           autopct=make_autopct(gender_counts_class), startangle=140,
           colors=["skyblue", "lightcoral"])
axs[0].set_title("Class Strength by Gender")
axs[0].axis('equal')

# Pie 2: Present Students by Gender
gender_counts_present = df_attendance['Gender'].value_counts()
axs[1].pie(gender_counts_present, labels=gender_counts_present.index,
           autopct=make_autopct(gender_counts_present), startangle=140,
           colors=["lightgreen", "salmon"])
axs[1].set_title("Present Students by Gender")
axs[1].axis('equal')

# Pie 3: Absent Students by Gender
gender_counts_absent = df_absentees['Gender'].value_counts()
axs[2].pie(gender_counts_absent, labels=gender_counts_absent.index,
           autopct=make_autopct(gender_counts_absent), startangle=140,
           colors=["orange", "lightblue"])
axs[2].set_title("Absent Students by Gender")
axs[2].axis('equal')

plt.tight_layout()
plt.show()
