import pandas as pd
import random
from datetime import datetime

random.seed(42)

events = pd.read_csv("events_2024_25.csv")

rows = []

for _, r in events.iterrows():
    date_str = r["Date"]
    event = r["Event"]
    d = datetime.strptime(date_str, "%Y-%m-%d")
    weekday = d.weekday()  # Mon=0 ... Sat=5 Sun=6

    # Default normal day
    if weekday == 5:  # Saturday
        attendance = random.randint(45, 65)
        lab = random.randint(25, 45)
        library = random.randint(50, 70)
        internet = random.randint(50, 75)
    else:
        attendance = random.randint(65, 80)
        lab = random.randint(40, 60)
        library = random.randint(40, 60)
        internet = random.randint(45, 65)

    # Event-specific overrides
    if event == "Holiday":
        attendance = random.randint(5, 20)
        lab = random.randint(5, 15)
        library = random.randint(5, 20)
        internet = random.randint(10, 30)

    elif event == "Exam":
        attendance = random.randint(95, 100)
        lab = random.randint(10, 25)
        library = random.randint(80, 95)
        internet = random.randint(70, 90)

    elif event == "PrepHoliday":
        attendance = random.randint(30, 50)
        lab = random.randint(10, 20)
        library = random.randint(90, 100)
        internet = random.randint(80, 95)

    elif event == "LabExam":
        attendance = random.randint(88, 98)
        lab = random.randint(90, 100)
        library = random.randint(40, 60)
        internet = random.randint(60, 80)

    rows.append([date_str, attendance, lab, library, internet])

df = pd.DataFrame(
    rows,
    columns=["Date", "Attendance", "Lab", "Library", "Internet"]
)
df.to_csv("historical_data.csv", index=False)

print("historical_data.csv created")