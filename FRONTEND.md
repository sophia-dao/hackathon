# 🌍 GSSI Backend API – Frontend Integration Guide

## 📌 Base URL

```
http://localhost:8000/gssi
```

---

# 🧠 Overview

This API powers the **Global Supply Chain Stress Index (GSSI)** dashboard.

The system:

* Aggregates macro + supply chain indicators
* Builds a weekly stress index (GSSI)
* Forecasts next-week stress using LSTM
* Generates AI-driven insights

---

# Endpoints

---

## 1. Health Check

### `GET /health`

Check if API is running.

### Response

```json
{
  "status": "ok",
  "message": "GSSI route is working"
}
```

---

## 2. Overview

### `GET /overview`

Basic system metadata.

### Response

```json
{
  "project": "Global Supply Chain Stress Index",
  "frequency": "weekly",
  "model": "LSTM",
  "status": "operational"
}
```

---

## 3. Current GSSI

### `GET /current`

Latest GSSI score.

### Response

```json
{
  "week": "2024-02-04",
  "gssi": 0.70,
  "alert": "high"
}
```

### Usage

* Dashboard headline
* Status badge (low / medium / high)

---

## 4. Historical Trend

### `GET /history`

Time series of GSSI.

### Response

```json
[
  { "week": "2024-01-07", "gssi": 0.10 },
  { "week": "2024-01-14", "gssi": 0.20 }
]
```

### Usage

* Line chart
* Trend visualization

---

## 5. Forecast

### `GET /forecast`

Next-week prediction.

### Response

```json
{
  "week": "2024-02-11",
  "predicted_gssi": 0.82,
  "alert": "high"
}
```

### Usage

* Forecast card
* Future projection chart

---

## 6. Component Breakdown

### `GET /components`

Underlying feature values over time.

### Response

```json
[
  {
    "week": "2024-02-04",
    "oil": 81.0,
    "volatility": 24.0,
    "freight": 2.0,
    "supplier": 3.0,
    "inventory": 0.9
  }
]
```

### Usage

* Multi-line chart
* Component comparison
* Feature drill-down

---

## 7. Drivers

### `GET /drivers`

Feature impact ranking.

### Response

```json
[
  {
    "name": "freight_cost",
    "correlation": 0.92,
    "impact": "positive",
    "source": "fred"
  }
]
```

### Fields

* `name`: feature name
* `correlation`: strength of relationship with GSSI
* `impact`: positive / negative
* `source`: data source category

### Usage

* Bar chart
* “Top drivers” list

---

## 8. AI Summary & Insights

### `GET /summary`

Structured macro interpretation.

### Response

```json
{
  "rule_based_summary": "The Global Supply Chain Stress Index is currently 0.70...",
  "ai_summary": "Supply chain stress remains elevated, posing inflation risks...",
  "ai_explanation": "Freight costs and supplier delays are driving stress...",
  "ai_recommendation": "Monitor logistics-sensitive sectors closely..."
}
```

### Fields

* `ai_summary`: inflation risk insight
* `ai_explanation`: why it’s happening
* `ai_recommendation`: action note

---

# Frontend Mapping

| UI Component   | Endpoint      | Field               |
| -------------- | ------------- | ------------------- |
| Current Score  | `/current`    | `gssi`, `alert`     |
| Trend Chart    | `/history`    | `gssi`              |
| Forecast       | `/forecast`   | `predicted_gssi`    |
| Components     | `/components` | oil, freight, etc.  |
| Drivers        | `/drivers`    | correlation         |
| AI Summary     | `/summary`    | `ai_summary`        |
| Explanation    | `/summary`    | `ai_explanation`    |
| Recommendation | `/summary`    | `ai_recommendation` |

---

# ⚠️ Notes

* All data is **weekly**
* GSSI is a **continuous numeric score**
* Alerts are:

  * `"low"`
  * `"medium"`
  * `"high"`
* AI fields are always strings (safe fallback included)

---

# Optional Optimization (Future)

Currently, each endpoint rebuilds the pipeline.

For performance, we may introduce:

```
GET /dashboard
```

to return all data in one call.

---

# Summary

Frontend should call:

* `/current`
* `/history`
* `/components`
* `/summary`
* `/forecast` (optional)
* `/drivers` (optional)

This will fully power the dashboard.
