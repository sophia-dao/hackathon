import { useEffect, useState } from "react";
import type {
  CurrentGssiResponse,
  ForecastResponse,
  GssiHistoryPoint,
  DriverContribution,
  SummaryResponse,
  GssiComponentPoint,
} from "../types/gssi";
import { getDashboard } from "../services/api";

type UseGssiDataResult = {
  current: CurrentGssiResponse | null;
  history: GssiHistoryPoint[];
  forecast: ForecastResponse | null;
  drivers: DriverContribution[];
  summary: SummaryResponse | null;
  components: GssiComponentPoint[];
  loading: boolean;
  error: string | null;
};

export function useGssiData(): UseGssiDataResult {
  const [current, setCurrent] = useState<CurrentGssiResponse | null>(null);
  const [history, setHistory] = useState<GssiHistoryPoint[]>([]);
  const [forecast, setForecast] = useState<ForecastResponse | null>(null);
  const [drivers, setDrivers] = useState<DriverContribution[]>([]);
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [components, setComponents] = useState<GssiComponentPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    async function loadGssiData() {
      try {
        setLoading(true);
        setError(null);

        const data = await getDashboard();

        if (!mounted) return;

        setCurrent(data.current);
        setHistory(data.history);
        setForecast(data.forecast);
        setDrivers(data.drivers);
        setSummary(data.summary);
        setComponents(data.components);
      } catch (err) {
        console.error("Failed to load GSSI data:", err);
        if (!mounted) return;
        setError("Failed to load dashboard data from backend.");
      } finally {
        if (mounted) setLoading(false);
      }
    }

    loadGssiData();

    return () => {
      mounted = false;
    };
  }, []);

  return {
    current,
    history,
    forecast,
    drivers,
    summary,
    components,
    loading,
    error,
  };
}