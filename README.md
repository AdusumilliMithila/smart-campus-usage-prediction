Smart Campus Resource Forecasting System:
A data-driven system to predict campus activity patterns such as attendance, lab usage, library usage, and internet usage using time series forecasting (ARIMA) and event-based logic.

Overview:
This project simulates and predicts how campus resources are utilized over time.
It combines:
Synthetic dataset generation
Time series forecasting (ARIMA)
Event-based adjustments (exam, holiday, lab)
Interactive dashboard visualization

Problem Statement:
Traditional campus systems only display historical data and do not provide insights about future usage.
This project aims to:
Predict campus activity trends
Help in better planning of resources
Identify patterns like exam periods and holidays

---System Architecture---
Dataset Generation (Python)
        ↓
Historical Dataset + Event Dataset
        ↓
ARIMA Model (Prediction)
        ↓
Event-Based Adjustment
        ↓
Predictions CSV
        ↓
Frontend Dashboard (HTML + JS + Chart.js)

---Datasets Used:
created 3 datasets to ensure clear separation of logic:
1️)events_2024_25.csv
Contains past academic events
Columns:
Date
Event (Exam, LabExam, Holiday, PrepHoliday, Normal)
👉 Used to simulate academic calendar behavior

2️) historical_data.csv
Contains past usage data
Columns:
Attendance (%)
Lab Usage (%)
Library Usage (%)
Internet Usage (%)
👉 Generated based on event patterns

3) events_2026.csv
Contains future academic events
👉 Used to guide prediction adjustments
*We used Python scripts to generate realistic datasets.

--Key Concepts:
datetime → generate dates
timedelta → iterate days
random.uniform() → generate realistic percentage values

--Event Logic Example
if month == 5 and week in [2,3,4]:
    event = "Holiday"
elif event == "Exam":
    attendance = random.uniform(90, 100)

--Behavior Mapping
Event	Attendance	Lab	Library	Internet
Exam	High	Low	High	High
Lab Exam	High	High	Medium	Medium
Holiday	Low	Low	Low	Low
Normal	Medium	Medium	Medium	Medium

--Model Implementation (ARIMA)
We used the ARIMA model from statsmodels for forecasting.
from statsmodels.tsa.arima.model import ARIMA
model = ARIMA(data, order=(2,1,2))
model_fit = model.fit()
forecast = model_fit.forecast(steps=365)

--Why ARIMA?
Works well for time-series data
Captures trends and patterns
Simple and effective

--Event-Based Adjustment
After prediction:
if event == "Exam":
    attendance += 10
This improves realism by incorporating academic patterns

--Frontend Dashboard:
The dashboard is built using:
HTML → structure
CSS → styling
JavaScript → logic
Chart.js → graphs

--Features:
.Month-wise & Week-wise filtering
.Graphs for all resources
.Alerts:
Exam Phase
Lab Activity
Holiday Period

--Data Loading:
Papa.parse("predictions.csv", {...})

--Visualization:
new Chart(ctx, {
  type: "line"
});

--Results:
Successfully predicted usage trends
Generated realistic activity patterns
Implemented alert system
Provided interactive visualization

--Limitations:
Uses synthetic data
ARIMA cannot capture complex nonlinear patterns

--Future Scope:
Use real ERP data
Integrate machine learning models (LSTM, XGBoost)
Add real-time updates
Expand to energy & infrastructure prediction

--Technologies Used:
Python
Pandas
Statsmodels (ARIMA)
HTML
CSS
JavaScript
Chart.js

--Conclusion:
This project demonstrates how time series forecasting + event-based logic can be used to simulate and predict campus activity effectively.
