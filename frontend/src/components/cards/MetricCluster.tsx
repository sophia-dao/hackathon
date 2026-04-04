import MetricCard from "./MetricCard";
import DriverBarChart from "../charts/DriverBarChart";
import type { DriverContribution } from "../../types/gssi";

interface MetricClusterProps {
  currentGssi: string;
  currentWeek: string;
  forecastValue: string;
  forecastWeek: string;
  trend: string;
  trendSubtitle: string;
  delta: string;
  deltaSubtitle: string;
  drivers: DriverContribution[];
}

export default function MetricCluster({
  currentGssi,
  currentWeek,
  forecastValue,
  forecastWeek,
  trend,
  trendSubtitle,
  delta,
  deltaSubtitle,
  drivers,
}: MetricClusterProps) {
  return (
    <section className="rounded-[34px] border border-white/70 bg-[linear-gradient(180deg,#f8fbff_0%,#f4f7fb_100%)] p-4 shadow-[0_16px_50px_rgba(15,23,42,0.05)] md:p-6">
      <div className="grid gap-5 lg:grid-cols-[1.35fr_0.95fr]">
        <MetricCard
          title="Stress Trend Direction"
          value={trend}
          subtitle={trendSubtitle}
          accent="orange"
          featured
          className="min-h-[340px] lg:min-h-full"
        >
          <DriverBarChart data={drivers} compact />
        </MetricCard>

        <div className="grid gap-5">
          <MetricCard
            title="Current GSSI"
            value={currentGssi}
            subtitle={currentWeek}
            accent="blue"
            className="min-h-[148px]"
          />

          <MetricCard
            title="Next-week Forecast"
            value={forecastValue}
            subtitle={forecastWeek}
            accent="purple"
            className="min-h-[148px]"
          />

          <MetricCard
            title="Forecast Delta"
            value={delta}
            subtitle={deltaSubtitle}
            accent="green"
            className="min-h-[148px]"
          />
        </div>
      </div>
    </section>
  );
}