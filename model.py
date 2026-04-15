import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

# Load data
hist = pd.read_csv("historical_data.csv")
events = pd.read_csv("events_2026.csv")

# Prepare historical data
hist["Date"] = pd.to_datetime(hist["Date"])
hist = hist.sort_values("Date")
hist.set_index("Date", inplace=True)
hist = hist.asfreq("D")

# Train one ARIMA model
models = {}
for col in ["Attendance", "Lab", "Library", "Internet"]:
    models[col] = ARIMA(hist[col], order=(2, 1, 2)).fit()

# Predict 2026
future_dates = pd.date_range(start="2026-01-01", end="2026-12-31")
pred = pd.DataFrame(index=future_dates)

for col in models:
    pred[col] = models[col].forecast(steps=len(future_dates)).values

pred.reset_index(inplace=True)
pred.rename(columns={"index": "Date"}, inplace=True)

# Merge with future events
events["Date"] = pd.to_datetime(events["Date"])
final = pd.merge(pred, events, on="Date", how="left")

# Event-based adjustments
for i, row in final.iterrows():
    event = row["Event"]

    if event == "Holiday":
        final.loc[i, "Attendance"] *= 0.25
        final.loc[i, "Lab"] *= 0.25
        final.loc[i, "Library"] *= 0.30
        final.loc[i, "Internet"] *= 0.40

    elif event == "Exam":
        final.loc[i, "Attendance"] = max(final.loc[i, "Attendance"] * 1.15, 95)
        final.loc[i, "Lab"] = min(final.loc[i, "Lab"] * 0.50, 25)
        final.loc[i, "Library"] = max(final.loc[i, "Library"] * 1.25, 85)
        final.loc[i, "Internet"] = max(final.loc[i, "Internet"] * 1.15, 75)

    elif event == "PrepHoliday":
        final.loc[i, "Attendance"] = min(max(final.loc[i, "Attendance"] * 0.60, 30), 55)
        final.loc[i, "Lab"] = min(final.loc[i, "Lab"] * 0.50, 20)
        final.loc[i, "Library"] = max(final.loc[i, "Library"] * 1.35, 90)
        final.loc[i, "Internet"] = max(final.loc[i, "Internet"] * 1.20, 80)

    elif event == "LabExam":
        final.loc[i, "Attendance"] = max(final.loc[i, "Attendance"] * 1.10, 88)
        final.loc[i, "Lab"] = max(final.loc[i, "Lab"] * 1.40, 90)
        final.loc[i, "Library"] = min(max(final.loc[i, "Library"] * 0.85, 40), 60)
        final.loc[i, "Internet"] = min(max(final.loc[i, "Internet"] * 1.05, 60), 85)

# Clamp all percentages to 0–100
for col in ["Attendance", "Lab", "Library", "Internet"]:
    final[col] = final[col].clip(lower=0, upper=100).round().astype(int)

# Save final dataset
final.to_csv("predictions.csv", index=False)

print("predictions.csv created successfully")