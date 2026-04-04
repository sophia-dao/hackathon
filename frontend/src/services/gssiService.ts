import { api } from "./api";
import type {
  CurrentGssiResponse,
  ForecastResponse,
  GssiHistoryPoint,
  DriverContribution,
  SummaryResponse,
} from "../types/gssi";

export const gssiService = {
  async getCurrent(): Promise<CurrentGssiResponse> {
    const res = await api.get("/gssi/current");
    return res.data;
  },

  async getHistory(): Promise<GssiHistoryPoint[]> {
    const res = await api.get("/gssi/history");
    return res.data;
  },

  async getForecast(): Promise<ForecastResponse> {
    const res = await api.get("/gssi/forecast");
    return res.data;
  },

  async getDrivers(): Promise<DriverContribution[]> {
    const res = await api.get("/gssi/drivers");
    return res.data;
  },

  async getSummary(): Promise<SummaryResponse> {
    const res = await api.get("/gssi/summary");
    return res.data;
  },
};