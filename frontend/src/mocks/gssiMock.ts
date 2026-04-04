import type {
  CurrentGssiResponse,
  ForecastResponse,
  GssiHistoryPoint,
  DriverContribution,
  SummaryResponse,
} from "../types/gssi";

export const mockCurrent: CurrentGssiResponse = {
  week: "2026-03-29",
  gssi: 1.12,
  alert: "Low",
};

export const mockHistory: GssiHistoryPoint[] = [
  { week: "2026-01-26", gssi: 0.18 },
  { week: "2026-02-02", gssi: 0.24 },
  { week: "2026-02-09", gssi: 0.31 },
  { week: "2026-02-16", gssi: 0.48 },
  { week: "2026-02-23", gssi: 0.56 },
  { week: "2026-03-02", gssi: 0.71 },
  { week: "2026-03-09", gssi: 0.83 },
  { week: "2026-03-16", gssi: 0.97 },
  { week: "2026-03-23", gssi: 1.05 },
  { week: "2026-03-29", gssi: 1.12 },
];

export const mockForecast: ForecastResponse = {
  week: "2026-04-05",
  predicted_gssi: 1.26,
  alert: "High",
};

export const mockDrivers: DriverContribution[] = [
  { name: "Oil Price", contribution: 0.34 },
  { name: "Market Volatility", contribution: 0.27 },
  { name: "Freight Cost", contribution: 0.19 },
  { name: "Supplier Delay", contribution: 0.12 },
  { name: "Inventory Stress", contribution: 0.08 },
];

export const mockSummary: SummaryResponse = {
  summary:
    "Current GSSI indicates elevated supply chain stress driven mainly by rising oil prices and volatility. If current conditions persist, short-term inflation pressure and sector-level risk may continue to rise.",
};

export const mockComponents = [
  { week: "2026-01-26", oil: 0.10, volatility: 0.06, freight: 0.04, supplier: 0.03, inventory: 0.02 },
  { week: "2026-02-02", oil: 0.11, volatility: 0.07, freight: 0.05, supplier: 0.03, inventory: 0.02 },
  { week: "2026-02-09", oil: 0.13, volatility: 0.08, freight: 0.05, supplier: 0.03, inventory: 0.02 },
  { week: "2026-02-16", oil: 0.18, volatility: 0.11, freight: 0.08, supplier: 0.06, inventory: 0.05 },
  { week: "2026-02-23", oil: 0.20, volatility: 0.12, freight: 0.10, supplier: 0.08, inventory: 0.06 },
  { week: "2026-03-02", oil: 0.25, volatility: 0.14, freight: 0.12, supplier: 0.10, inventory: 0.10 },
  { week: "2026-03-09", oil: 0.28, volatility: 0.18, freight: 0.14, supplier: 0.11, inventory: 0.12 },
  { week: "2026-03-16", oil: 0.30, volatility: 0.21, freight: 0.16, supplier: 0.14, inventory: 0.16 },
  { week: "2026-03-23", oil: 0.32, volatility: 0.23, freight: 0.18, supplier: 0.15, inventory: 0.17 },
  { week: "2026-03-29", oil: 0.34, volatility: 0.27, freight: 0.19, supplier: 0.12, inventory: 0.08 },
];