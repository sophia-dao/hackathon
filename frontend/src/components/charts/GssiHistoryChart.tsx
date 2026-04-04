import { useEffect, useRef, useState } from "react";
import { useInView } from "framer-motion";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  Line,
} from "recharts";
import type { GssiHistoryPoint } from "../../types/gssi";

export default function GssiHistoryChart({
  data,
  forecastValue,
}: {
  data: GssiHistoryPoint[];
  forecastValue?: number;
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const isInView = useInView(containerRef, {
    once: true,
    margin: "-10% 0px -10% 0px",
  });

  const [seriesReady, setSeriesReady] = useState(false);

  useEffect(() => {
    if (!isInView || seriesReady) return;

    const timer = window.setTimeout(() => {
      setSeriesReady(true);
    }, 180);

    return () => window.clearTimeout(timer);
  }, [isInView, seriesReady]);

  return (
    <div
      ref={containerRef}
      className="relative overflow-hidden rounded-3xl border border-slate-200 bg-white p-5 shadow-lg"
    >
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(37,99,235,0.05),transparent_28%),radial-gradient(circle_at_top_right,rgba(124,58,237,0.04),transparent_24%)]" />

      <div className="relative mb-4">
        <h2 className="text-xl font-semibold text-slate-900">GSSI Trend</h2>
        <p className="text-sm text-slate-500">
          Historical stress level over recent weeks
        </p>
      </div>

      <div className="relative h-80">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={data}
            margin={{ top: 8, right: 18, left: 2, bottom: 0 }}
          >
            <defs>
              <linearGradient id="gssiFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2563eb" stopOpacity={0.28} />
                <stop offset="95%" stopColor="#2563eb" stopOpacity={0.05} />
              </linearGradient>

              <linearGradient id="hoverGuideFade" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#94a3b8" stopOpacity={0.22} />
                <stop offset="100%" stopColor="#94a3b8" stopOpacity={0.06} />
              </linearGradient>
            </defs>

            <CartesianGrid
              strokeDasharray="4 4"
              stroke="#e2e8f0"
              vertical={true}
              horizontal={true}
            />

            <XAxis
              dataKey="week"
              tick={{ fontSize: 12, fill: "#64748b" }}
              tickLine={false}
              axisLine={{ stroke: "#94a3b8", strokeWidth: 1 }}
            />

            <YAxis
              tick={{ fontSize: 12, fill: "#64748b" }}
              tickLine={false}
              axisLine={{ stroke: "#94a3b8", strokeWidth: 1 }}
            />

            <Tooltip
              cursor={{
                stroke: "#94a3b8",
                strokeWidth: 1,
                strokeDasharray: "3 3",
              }}
              contentStyle={{
                borderRadius: 14,
                border: "1px solid rgba(226,232,240,0.95)",
                boxShadow: "0 12px 28px rgba(15,23,42,0.10)",
                background: "rgba(255,255,255,0.97)",
              }}
              labelStyle={{
                color: "#0f172a",
                fontWeight: 600,
                marginBottom: 6,
              }}
              formatter={(value) => {
                const numericValue =
                  typeof value === "number" ? value : Number(value ?? 0);
                return [numericValue.toFixed(2), "GSSI"];
              }}
            />

            <ReferenceLine
              y={0.5}
              stroke="#f59e0b"
              strokeDasharray="5 5"
              strokeOpacity={0.9}
            />

            <ReferenceLine
              y={1.5}
              stroke="#ef4444"
              strokeDasharray="5 5"
              strokeOpacity={0.9}
            />

            {forecastValue !== undefined && (
              <ReferenceLine
                y={forecastValue}
                stroke="#7c3aed"
                strokeDasharray="6 6"
                strokeWidth={1.5}
                label={{
                  value: "Forecast",
                  position: "right",
                  fill: "#7c3aed",
                  fontSize: 12,
                  fontWeight: 600,
                }}
              />
            )}

            {seriesReady ? (
              <>
                <Area
                  type="monotone"
                  dataKey="gssi"
                  stroke="none"
                  fill="url(#gssiFill)"
                  isAnimationActive
                  animationBegin={0}
                  animationDuration={1100}
                  animationEasing="ease-out"
                />

                <Line
                  type="monotone"
                  dataKey="gssi"
                  stroke="#2563eb"
                  strokeWidth={3.5}
                  dot={false}
                  activeDot={{
                    r: 6,
                    fill: "#2563eb",
                    stroke: "#ffffff",
                    strokeWidth: 2.5,
                  }}
                  isAnimationActive
                  animationBegin={80}
                  animationDuration={1200}
                  animationEasing="ease-out"
                />
              </>
            ) : null}
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}