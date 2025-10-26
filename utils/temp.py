import pandas as pd
import matplotlib.pyplot as plt

# Load all three CSV files
original_path = r"D:\cvprojects\Smart Attendace\Source\alert\class data.csv"
present_path = r"D:\cvprojects\Smart Attendace\Source\ai_attendance\attendance_log.csv"
absent_path = r"D:\cvprojects\Smart Attendace\Source\ai_attendance\absentees_list.csv"

df_original = pd.read_csv(original_path)
df_present = pd.read_csv(present_path)
df_absent = pd.read_csv(absent_path)

# Clean and standardize
df_original['Gender'] = df_original['Gender'].str.strip().str.capitalize()
df_original['roll_number'] = df_original['roll_number'].astype(str).str.strip()
df_present['roll_number'] = df_present['roll_number'].astype(str).str.strip()
df_absent['roll_number'] = df_absent['roll_number'].astype(str).str.strip()

# Count gender in original data
original_gender_counts = df_original['Gender'].value_counts()

# Merge gender info into present and absent data
df_present_merged = pd.merge(df_present, df_original[['roll_number', 'Gender']], on='roll_number', how='left')
df_absent_merged = pd.merge(df_absent, df_original[['roll_number', 'Gender']], on='roll_number', how='left')

# Count gender distribution
present_gender_counts = df_present_merged['Gender'].value_counts()
absent_gender_counts = df_absent_merged['Gender'].value_counts()

# === PRINT GENDER COUNTS & PERCENTAGES ===

# Original
print("=== Original Student Gender Breakdown ===")
total_original = original_gender_counts.sum()
for gender, count in original_gender_counts.items():
    percent = (count / total_original) * 100
    print(f"{gender}: {count} students ({percent:.1f}%)")

# Present
print("\n=== Present Students Gender Breakdown ===")
total_present = present_gender_counts.sum()
for gender, count in present_gender_counts.items():
    percent = (count / total_present) * 100
    print(f"{gender}: {count} students ({percent:.1f}%)")

# Absent
print("\n=== Absent Students Gender Breakdown ===")
total_absent = absent_gender_counts.sum()
for gender, count in absent_gender_counts.items():
    percent = (count / total_absent) * 100
    print(f"{gender}: {count} students ({percent:.1f}%)")

# === PIE CHARTS ===
plt.figure(figsize=(18, 5))

# Original
plt.subplot(1, 3, 1)
plt.pie(
    original_gender_counts,
    labels=original_gender_counts.index,
    autopct=lambda p: f'{p:.1f}%\n({int(round(p * total_original / 100))})',
    startangle=140,
    colors=["gold", "lightskyblue"]
)
plt.title("Gender Distribution - Original")

# Present
plt.subplot(1, 3, 2)
plt.pie(
    present_gender_counts,
    labels=present_gender_counts.index,
    autopct=lambda p: f'{p:.1f}%\n({int(round(p * total_present / 100))})',
    startangle=140,
    colors=["lightgreen", "lightblue"]
)
plt.title("Gender Distribution - Present")

# Absent
plt.subplot(1, 3, 3)
plt.pie(
    absent_gender_counts,
    labels=absent_gender_counts.index,
    autopct=lambda p: f'{p:.1f}%\n({int(round(p * total_absent / 100))})',
    startangle=140,
    colors=["salmon", "lightgray"]
)
plt.title("Gender Distribution - Absent")

plt.tight_layout()
plt.show()
