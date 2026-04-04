import axios from "axios";
import type {
  CurrentGssiResponse,
  ForecastResponse,
  GssiHistoryPoint,
  DriverContribution,
  SummaryResponse,
  GssiComponentPoint,
} from "../types/gssi";

export const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export interface DashboardResponse {
  current: CurrentGssiResponse;
  history: GssiHistoryPoint[];
  forecast: ForecastResponse;
  drivers: DriverContribution[];
  summary: SummaryResponse;
  components: GssiComponentPoint[];
}

export async function getDashboard(): Promise<DashboardResponse> {
  const res = await api.get("/gssi/dashboard");
  return res.data;
}

export async function getCurrentGssi(): Promise<CurrentGssiResponse> {
  const res = await api.get("/gssi/current");
  return res.data;
}

export async function getGssiHistory(): Promise<GssiHistoryPoint[]> {
  const res = await api.get("/gssi/history");
  return res.data;
}

export async function getForecast(): Promise<ForecastResponse> {
  const res = await api.get("/gssi/forecast");
  return res.data;
}

export async function getDrivers(): Promise<DriverContribution[]> {
  const res = await api.get("/gssi/drivers");
  return res.data;
}

export async function getSummary(): Promise<SummaryResponse> {
  const res = await api.get("/gssi/summary");
  return res.data;
}

export async function getComponents(): Promise<GssiComponentPoint[]> {
  const res = await api.get("/gssi/components");
  return res.data;
}