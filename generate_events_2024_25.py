import pandas as pd
from datetime import datetime, timedelta


def first_monday(year: int, month: int) -> datetime:
    d = datetime(year, month, 1)
    while d.weekday() != 0:  # Monday
        d += timedelta(days=1)
    return d


def second_monday(year: int, month: int) -> datetime:
    return first_monday(year, month) + timedelta(days=7)


def add_range_event(events: dict, start: datetime, end: datetime, label: str) -> None:
    d = start
    while d <= end:
        events[d.date()] = label
        d += timedelta(days=1)


def add_specific_event(events: dict, dates: list[datetime], label: str) -> None:
    for d in dates:
        events[d.date()] = label


def build_year_events(year: int) -> dict:
    events: dict = {}

    # Default Sundays as holiday
    start = datetime(year, 1, 1)
    end = datetime(year, 12, 31)
    d = start
    while d <= end:
        if d.weekday() == 6:  # Sunday
            events[d.date()] = "Holiday"
        d += timedelta(days=1)

    # May holidays: week 2, 3, 4
    add_range_event(events, datetime(year, 5, 8), datetime(year, 5, 28), "Holiday")

    # October holidays: week 1 and 2
    add_range_event(events, datetime(year, 10, 1), datetime(year, 10, 14), "Holiday")

    # Semester 1
    # Mid 1: March 2nd Monday to Friday (exactly 5 days)
    mid1_start = second_monday(year, 3)
    add_range_event(events, mid1_start, mid1_start + timedelta(days=4), "Exam")

    # Mid 2: June 1st Monday to Friday (exactly 5 days)
    mid2_start = first_monday(year, 6)
    add_range_event(events, mid2_start, mid2_start + timedelta(days=4), "Exam")

    # Sat after Mid 2 as prep-like day
    sat_after_mid2 = mid2_start + timedelta(days=5)
    if sat_after_mid2.year == year and sat_after_mid2.weekday() == 5:
        events[sat_after_mid2.date()] = "PrepHoliday"

    # Lab exams: 3 exams with prep holidays between
    # Monday, Wednesday, Friday = LabExam
    # Tuesday, Thursday = PrepHoliday
    lab_start = mid2_start + timedelta(days=14)  # 3rd Monday of June
    add_specific_event(
        events,
        [lab_start, lab_start + timedelta(days=2), lab_start + timedelta(days=4)],
        "LabExam",
    )
    add_specific_event(
        events,
        [lab_start + timedelta(days=1), lab_start + timedelta(days=3)],
        "PrepHoliday",
    )

    # End sem: 5 exams with one prep holiday between
    end_sem_start = lab_start + timedelta(days=7)  # next Monday
    end_exam_days = [
        end_sem_start,
        end_sem_start + timedelta(days=2),
        end_sem_start + timedelta(days=4),
        end_sem_start + timedelta(days=7),
        end_sem_start + timedelta(days=9),
    ]
    end_prep_days = [
        end_sem_start + timedelta(days=1),
        end_sem_start + timedelta(days=3),
        end_sem_start + timedelta(days=5),
        end_sem_start + timedelta(days=8),
    ]
    add_specific_event(events, end_exam_days, "Exam")
    add_specific_event(events, end_prep_days, "PrepHoliday")

    # Semester 2
    # Mid 1: September 1st Monday to Friday
    sem2_mid1_start = first_monday(year, 9)
    add_range_event(events, sem2_mid1_start, sem2_mid1_start + timedelta(days=4), "Exam")

    # Mid 2: December 1st Monday to Friday
    sem2_mid2_start = first_monday(year, 12)
    add_range_event(events, sem2_mid2_start, sem2_mid2_start + timedelta(days=4), "Exam")

    sat_after_mid2_dec = sem2_mid2_start + timedelta(days=5)
    if sat_after_mid2_dec.year == year and sat_after_mid2_dec.weekday() == 5:
        events[sat_after_mid2_dec.date()] = "PrepHoliday"

    # December lab exams: 3 exams with prep between
    dec_lab_start = sem2_mid2_start + timedelta(days=7)  # 2nd Monday
    add_specific_event(
        events,
        [dec_lab_start, dec_lab_start + timedelta(days=2), dec_lab_start + timedelta(days=4)],
        "LabExam",
    )
    add_specific_event(
        events,
        [dec_lab_start + timedelta(days=1), dec_lab_start + timedelta(days=3)],
        "PrepHoliday",
    )

    # December end sem: 5 exams with prep holidays between
    dec_end_start = dec_lab_start + timedelta(days=7)  # 3rd Monday
    dec_end_exam_days = [
        dec_end_start,
        dec_end_start + timedelta(days=2),
        dec_end_start + timedelta(days=4),
        dec_end_start + timedelta(days=7),
        dec_end_start + timedelta(days=9),
    ]
    dec_end_prep_days = [
        dec_end_start + timedelta(days=1),
        dec_end_start + timedelta(days=3),
        dec_end_start + timedelta(days=5),
        dec_end_start + timedelta(days=8),
    ]

    # Only include dates still inside the same year
    add_specific_event(events, [d for d in dec_end_exam_days if d.year == year], "Exam")
    add_specific_event(events, [d for d in dec_end_prep_days if d.year == year], "PrepHoliday")

    return events


all_rows = []
for yr in [2024, 2025]:
    year_events = build_year_events(yr)
    d = datetime(yr, 1, 1)
    while d <= datetime(yr, 12, 31):
        event = year_events.get(d.date(), "Normal")
        all_rows.append([d.strftime("%Y-%m-%d"), event])
        d += timedelta(days=1)

df = pd.DataFrame(all_rows, columns=["Date", "Event"])
df.to_csv("events_2024_25.csv", index=False)

print("events_2024_25.csv created")