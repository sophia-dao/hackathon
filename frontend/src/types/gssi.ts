export type AlertLevel = "Low" | "Moderate" | "High" | "Critical";

export interface CurrentGssiResponse {
  week: string;
  gssi: number;
  alert: AlertLevel;
}

export interface GssiHistoryPoint {
  week: string;
  gssi: number;
}

export interface ForecastResponse {
  week: string;
  predicted_gssi: number;
  alert: AlertLevel;
}

export interface DriverContribution {
  name: string;
  contribution: number;
}

export interface SummaryResponse {
  summary: string;
}

export interface GssiComponentPoint {
  week: string;
  oil: number;
  volatility: number;
  freight: number;
  supplier: number;
  inventory: number;
}