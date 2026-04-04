# StressWatch — Global Supply Chain Stress Index

An early-warning system that measures and forecasts global supply chain stress and its macro-financial implications for investors, policymakers, and corporations.

---

## System Architecture

```text
Data Ingestion (FRED, yfinance, GDELT, Google Trends)
→ Preprocessing (clean, align, resample to weekly)
→ GSSI Computation (signed weighted sum)
→ LSTM Forecasting (next-week GSSI)
→ Alert Labeling
→ Driver Correlation Analysis
→ AI Narrative + Recommendations (OpenAI)
→ REST API (FastAPI)
→ Dashboard (React + Recharts)
```

---

## Project Structure

```text
hackathon/
├── app/
│   ├── main.py               # FastAPI app entry point
│   ├── data_sources.py       # FRED, yfinance, GDELT, Google Trends ingestion
│   ├── preprocessing.py      # Cleaning, resampling, scaling
│   ├── index_builder.py      # GSSI computation + signed weights
│   ├── sequence_builder.py   # LSTM sequence preparation
│   ├── forecasting.py        # Next-week GSSI forecast
│   ├── alerts.py             # Alert level labeling
│   ├── analytics.py          # Driver analysis + OpenAI summaries
│   └── routes/
│       └── gssi.py           # API endpoints + in-memory cache
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   └── src/
│       ├── App.jsx            # Root layout, data fetching, tab routing
│       ├── api.js             # API client functions
│       ├── utils.js           # Shared formatters and constants
│       └── components/
│           ├── Sidebar.jsx        # Icon navigation sidebar
│           ├── MetricCard.jsx     # Top KPI cards
│           ├── HistoryChart.jsx   # Historical GSSI area chart
│           ├── ForecastCard.jsx   # Forecast panel
│           ├── DriversChart.jsx   # Horizontal bar chart (dashboard)
│           ├── DriversView.jsx    # Full drivers tab
│           ├── OverviewView.jsx   # Overview tab with AI cards
│           ├── ForecastView.jsx   # Forecast tab
│           ├── AlertsView.jsx     # Alerts tab
│           ├── RecentAlerts.jsx   # Alert history widget
│           ├── AlertBadge.jsx     # Colour-coded alert pill
│           └── SystemView.jsx     # API explorer tab
│
├── test/
├── venv/
├── .env
├── requirements.txt
└── README.md
```

---

## Data Sources

| Source | Series / Ticker | Feature | Role |
|---|---|---|---|
| FRED | `DCOILWTICO` | `oil` | Stress indicator |
| FRED | `FRGEXPUSM649NCIS` | `freight` | Stress indicator |
| FRED | `WPU0561` | `transport_ppi` | Stress indicator |
| FRED | `CSCICP03USM665S` | `consumer_confidence` | Health indicator |
| yfinance | `^GSPC`, `^DJI`, `^IXIC` | Close / Return / Vol | Mixed |
| GDELT | Supply chain articles | `news_count` | Stress indicator |
| Google Trends | Supply chain / shipping | `trend_*` | Stress indicator |

---

## GSSI Computation

Features are z-scored then combined via a signed weighted sum:

```text
GSSI = Σ (weight_i × z_score_i)   normalised to 0–100
```

Stress indicators carry **positive** weights; health indicators carry **negative** weights so that rising market confidence pulls GSSI down.

| Feature | Weight |
|---|---|
| oil, freight | +0.12 each |
| transport_ppi | +0.10 |
| dow/sp500/nasdaq volatility | +0.08 each |
| consumer_confidence | −0.10 |
| sp500/dow/nasdaq close | −0.06 each |

---

## Alert Levels

| GSSI (0–100) | Level |
|---|---|
| 0 – 25 | Low |
| 25 – 50 | Moderate |
| 50 – 75 | High |
| 75 – 100 | Critical |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/gssi/current` | Latest GSSI + alert |
| GET | `/gssi/history` | Full historical GSSI |
| GET | `/gssi/forecast` | Next-week forecast |
| GET | `/gssi/drivers` | Indicator correlations + latest values |
| GET | `/gssi/ai-summary` | AI narrative + recommendations |
| POST | `/gssi/refresh` | Force cache refresh |
| GET | `/gssi/cache-status` | Cache age and TTL |

Responses are cached in memory for **1 hour** to avoid re-running the full pipeline on every request.

---

## Dashboard Views

| Tab | Content |
|---|---|
| Dashboard | KPI cards, historical chart, forecast, top drivers, recent alerts |
| Overview | GSSI gauge, AI summary, investor / risk / policy recommendation cards |
| Forecast | Next-week prediction with trend analysis |
| Alerts | Full alert history |
| Drivers | Correlation rankings with latest real values on hover |
| System | Live API explorer |

---

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- FRED API key → [fred.stlouisfed.org/docs/api](https://fred.stlouisfed.org/docs/api/api_key.html)
- OpenAI API key → [platform.openai.com](https://platform.openai.com)

### 1. Clone the repo

```bash
git clone <repo-url>
cd hackathon
```

### 2. Configure environment variables

Create a `.env` file in `hackathon/`:

```env
FRED_API_KEY=your_fred_key
OPENAI_API_KEY=your_openai_key
```

### 3. Backend setup

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Start the backend

```bash
uvicorn app.main:app --reload
```

API runs at `http://localhost:8000` — interactive docs at `http://localhost:8000/docs`

### 5. Frontend setup

```bash
cd frontend
npm install
```

### 6. Start the frontend

```bash
npm run dev
```

Dashboard runs at `http://localhost:5173`

---

## Tech Stack

**Backend**
- FastAPI + Uvicorn
- Pandas / NumPy
- scikit-learn (scaling)
- TensorFlow / Keras (LSTM)
- OpenAI API (GPT-4o-mini)

**Frontend**
- React 19
- Recharts (charts)
- Lucide React (icons)
- Vite (build tool)

---

## AI Features

- **AI Summary** — macro-financial narrative covering GSSI level, inflation linkage, and forecast implications
- **Investor Strategy** — portfolio and asset allocation recommendations
- **Risk Management** — actions for corporations and financial institutions
- **Policy Response** — regulatory and government response suggestions

All AI outputs are generated via `gpt-4o-mini` and gracefully degrade if the OpenAI call fails.
