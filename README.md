# 🌍 Global Supply Chain Stress Index (GSSI)

## 📌 Overview

The **Global Supply Chain Stress Index (GSSI)** is an early-warning system designed to monitor and forecast supply chain disruptions and their macro-financial impact.

This backend system:

* Aggregates global economic and logistics indicators
* Transforms them into a unified weekly stress index (GSSI)
* Forecasts future stress levels using LSTM
* Generates actionable alerts and summaries for decision-makers

---

## 🧠 System Architecture

### 🔄 Backend Flow

```text
API data ingestion
→ preprocessing (clean + align + resample weekly)
→ normalized feature table
→ GSSI computation
→ driver contribution analysis
→ LSTM sequence generation
→ forecasting (next-week GSSI)
→ alert labeling + summary generation
→ API endpoints
```

---

## 🧩 Project Structure

```text
hackathon/
    ├── app/
    │   ├── main.py
    │   ├── data_sources.py
    │   ├── preprocessing.py
    │   ├── index_builder.py
    │   ├── sequence_builder.py
    │   ├── forecasting.py
    │   ├── alerts.py
    │   ├── analytics.py
    │   └── routes/
    │       └── gssi.py
    │
    ├── data/
    ├── venv/
    ├── requirements.txt
    └── README.md
```

---

## 📊 Core Features

We use the following indicators to build GSSI:

* 🚢 Freight Cost
* 🏭 Supplier Delay
* 🛢 Oil Price
* 📉 Market Volatility (e.g., VIX)
* 📦 Inventory Stress

All features are:

* aligned by date
* resampled to **weekly frequency**
* normalized before index computation

---

## Expected Output(Sophia)
Main task: Data fetching + GSSI score

```
df.columns = [
    "week",
    "freight_cost",
    "supplier_delay",
    "oil_price",
    "market_volatility",
    "inventory_stress",
    "gssi",
    "alert"
]
```

---

## Expected Output (Andy)
Main task: AI + Forecast + Insights

```
{
  "forecast_week": "...",
  "predicted_gssi": 1.25,
  "predicted_alert": "High"
}
```

## 📈 GSSI Calculation

Initial version uses a weighted sum of normalized indicators:

```text
GSSI = w1 * freight_cost
     + w2 * supplier_delay
     + w3 * oil_price
     + w4 * market_volatility
     + w5 * inventory_stress
```

Default weights (MVP):

```text
w1 = w2 = w3 = w4 = w5 = 0.2
```

---

## 🤖 Forecasting (LSTM)

### Model Setup

* Input: past **8 weeks**
* Output: **next-week GSSI**
* Data frequency: weekly

### Versions

* ✅ V1: Univariate (GSSI only)
* 🔜 V2: Multivariate (all indicators)

---

## 🚨 Alert System

GSSI values are mapped to warning levels:

| GSSI Value | Alert Level |
| ---------- | ----------- |
| < -0.5     | Low         |
| -0.5 – 0.5 | Moderate    |
| 0.5 – 1.5  | High        |
| > 1.5      | Critical    |

---

## 📡 API Endpoints

| Endpoint         | Description                       |
| ---------------- | --------------------------------- |
| `/gssi/current`  | Latest GSSI + alert               |
| `/gssi/history`  | Historical GSSI                   |
| `/gssi/forecast` | Next-week forecast                |
| `/gssi/drivers`  | Top contributing indicators       |
| `/gssi/summary`  | Generated macro-financial summary |

---

## 📦 Example Response

### `/gssi/current`

```json
{
  "week": "2026-03-29",
  "gssi": 1.12,
  "alert": "High"
}
```

---

## ⚙️ Setup Instructions

### 1. Clone the repo

```bash
git clone <repo-url>
cd hackathon/backend
```

### 2. Create a virtual environment

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the FastAPI server

```bash
uvicorn app.main:app --reload
```

### 5. Open the API docs

```text
http://127.0.0.1:8000/docs
```

---

## ▶️ Quick Run Commands

### Start the backend

#### macOS / Linux

```bash
cd hackathon/backend
source venv/bin/activate
uvicorn app.main:app --reload
```

#### Windows

```bash
cd hackathon\backend
venv\Scripts\activate
uvicorn app.main:app --reload
```


---

## 🛠 Tech Stack

* FastAPI (backend API)
* Pandas / NumPy (data processing)
* scikit-learn (normalization)
* TensorFlow / Keras (LSTM)
* Uvicorn (server)

---

## 🚀 Development Roadmap

### Phase 1 (MVP)

* [x] API skeleton
* [ ] Data ingestion
* [ ] Weekly preprocessing
* [ ] GSSI computation
* [ ] Alert system

### Phase 2

* [ ] LSTM forecasting (univariate)
* [ ] Forecast endpoint
* [ ] Driver contribution analysis

### Phase 3

* [ ] Multivariate LSTM
* [ ] AI-generated summaries
* [ ] Scenario simulation

---

## 👥 Team Notes

* Backend focuses on **data pipeline + modeling**
* Frontend can already integrate with mock endpoints
* Keep modules independent to avoid merge conflicts

---

## 💡 Hackathon Angle

This project turns complex macro + logistics signals into:

* 📊 A single interpretable index (GSSI)
* 🔮 Predictive insights (LSTM forecast)
* 🚨 Actionable alerts
* 🧠 AI-generated explanations

---

## 📌 Future Improvements

* PCA-based weighting
* Real-time streaming data
* Anomaly detection
* Multi-step forecasting
* Interactive dashboards

---

## ✨ Summary

GSSI provides:

* visibility into supply chain stress
* early warnings for financial disruptions
* explainable, data-driven insights

---
