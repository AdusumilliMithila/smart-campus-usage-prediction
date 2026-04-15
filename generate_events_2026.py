import pandas as pd
from datetime import datetime, timedelta


def first_monday(year: int, month: int) -> datetime:
    d = datetime(year, month, 1)
    while d.weekday() != 0:
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

    # Sundays
    d = datetime(year, 1, 1)
    while d <= datetime(year, 12, 31):
        if d.weekday() == 6:
            events[d.date()] = "Holiday"
        d += timedelta(days=1)

    # May holidays
    add_range_event(events, datetime(year, 5, 8), datetime(year, 5, 28), "Holiday")

    # October holidays
    add_range_event(events, datetime(year, 10, 1), datetime(year, 10, 14), "Holiday")

    # March Mid 1
    mid1_start = second_monday(year, 3)
    add_range_event(events, mid1_start, mid1_start + timedelta(days=4), "Exam")

    # June Mid 2
    mid2_start = first_monday(year, 6)
    add_range_event(events, mid2_start, mid2_start + timedelta(days=4), "Exam")

    # Saturday after June mid2
    sat_after_mid2 = mid2_start + timedelta(days=5)
    if sat_after_mid2.weekday() == 5:
        events[sat_after_mid2.date()] = "PrepHoliday"

    # June lab exams
    lab_start = mid2_start + timedelta(days=14)
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

    # June/July end sem
    end_sem_start = lab_start + timedelta(days=7)
    exam_days = [
        end_sem_start,
        end_sem_start + timedelta(days=2),
        end_sem_start + timedelta(days=4),
        end_sem_start + timedelta(days=7),
        end_sem_start + timedelta(days=9),
    ]
    prep_days = [
        end_sem_start + timedelta(days=1),
        end_sem_start + timedelta(days=3),
        end_sem_start + timedelta(days=5),
        end_sem_start + timedelta(days=8),
    ]
    add_specific_event(events, exam_days, "Exam")
    add_specific_event(events, prep_days, "PrepHoliday")

    # September Mid 1
    sem2_mid1_start = first_monday(year, 9)
    add_range_event(events, sem2_mid1_start, sem2_mid1_start + timedelta(days=4), "Exam")

    # December Mid 2
    sem2_mid2_start = first_monday(year, 12)
    add_range_event(events, sem2_mid2_start, sem2_mid2_start + timedelta(days=4), "Exam")

    sat_after_mid2_dec = sem2_mid2_start + timedelta(days=5)
    if sat_after_mid2_dec.weekday() == 5:
        events[sat_after_mid2_dec.date()] = "PrepHoliday"

    # December lab exams
    dec_lab_start = sem2_mid2_start + timedelta(days=7)
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

    # December end sem
    dec_end_start = dec_lab_start + timedelta(days=7)
    dec_exam_days = [
        dec_end_start,
        dec_end_start + timedelta(days=2),
        dec_end_start + timedelta(days=4),
        dec_end_start + timedelta(days=7),
        dec_end_start + timedelta(days=9),
    ]
    dec_prep_days = [
        dec_end_start + timedelta(days=1),
        dec_end_start + timedelta(days=3),
        dec_end_start + timedelta(days=5),
        dec_end_start + timedelta(days=8),
    ]

    add_specific_event(events, [d for d in dec_exam_days if d.year == year], "Exam")
    add_specific_event(events, [d for d in dec_prep_days if d.year == year], "PrepHoliday")

    return events


year = 2026
year_events = build_year_events(year)

rows = []
d = datetime(year, 1, 1)
while d <= datetime(year, 12, 31):
    event = year_events.get(d.date(), "Normal")
    rows.append([d.strftime("%Y-%m-%d"), event])
    d += timedelta(days=1)

df = pd.DataFrame(rows, columns=["Date", "Event"])
df.to_csv("events_2026.csv", index=False)

print("events_2026.csv created")