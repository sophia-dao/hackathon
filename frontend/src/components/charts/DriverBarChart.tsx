import { useEffect, useRef, useState } from "react";
import { useInView } from "framer-motion";
import {
  ResponsiveContainer,
  BarChart,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Bar,
  Cell,
} from "recharts";
import type { DriverContribution } from "../../types/gssi";

const colors = ["#2563eb", "#7c3aed", "#f97316", "#14b8a6", "#ef4444"];

export default function DriverBarChart({
  data,
  compact = false,
}: {
  data: DriverContribution[];
  compact?: boolean;
}) {
  const chartData = data.map((item) => ({
    ...item,
    contributionPct: Math.round(item.contribution * 100),
  }));

  const containerRef = useRef<HTMLDivElement | null>(null);
  const isInView = useInView(containerRef, {
    once: true,
    margin: "-10% 0px -10% 0px",
  });

  const [barsReady, setBarsReady] = useState(false);

  useEffect(() => {
    if (!isInView || barsReady) return;

    const timer = window.setTimeout(() => {
      setBarsReady(true);
    }, 180);

    return () => window.clearTimeout(timer);
  }, [isInView, barsReady]);

  return (
    <div
      ref={containerRef}
      className={
        compact
          ? "relative"
          : "relative rounded-3xl border border-slate-200 bg-white p-5 shadow-lg"
      }
    >
      {!compact && (
        <div className="mb-4">
          <h2 className="text-xl font-semibold text-slate-900">Top Drivers</h2>
          <p className="text-sm text-slate-500">
            Main contributors to current stress
          </p>
        </div>
      )}

      <div className={compact ? "relative mt-2 h-[360px]" : "relative h-[360px]"}>
        {!compact && (
          <div className="pointer-events-none absolute inset-0 rounded-2xl bg-[radial-gradient(circle_at_top_left,rgba(59,130,246,0.06),transparent_28%),radial-gradient(circle_at_top_right,rgba(168,85,247,0.05),transparent_30%)]" />
        )}

        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            margin={
              compact
                ? { top: 8, right: 8, left: -18, bottom: 6 }
                : { top: 10, right: 12, left: -12, bottom: 6 }
            }
            barCategoryGap={compact ? "20%" : "18%"}
          >
            <defs>
              <linearGradient id="driverBarGradient0" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#3b82f6" />
                <stop offset="100%" stopColor="#2563eb" />
              </linearGradient>
              <linearGradient id="driverBarGradient1" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#8b5cf6" />
                <stop offset="100%" stopColor="#7c3aed" />
              </linearGradient>
              <linearGradient id="driverBarGradient2" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#fb923c" />
                <stop offset="100%" stopColor="#f97316" />
              </linearGradient>
              <linearGradient id="driverBarGradient3" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#2dd4bf" />
                <stop offset="100%" stopColor="#14b8a6" />
              </linearGradient>
              <linearGradient id="driverBarGradient4" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#f87171" />
                <stop offset="100%" stopColor="#ef4444" />
              </linearGradient>
            </defs>

            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#e2e8f0"
              opacity={0.45}
              vertical={true}
              horizontal={true}
            />

            <XAxis
              dataKey="name"
              tick={{ fontSize: compact ? 11 : 12, fill: "#64748b" }}
              axisLine={false}
              tickLine={false}
            />

            <YAxis
              tick={{ fontSize: compact ? 11 : 12, fill: "#64748b" }}
              axisLine={false}
              tickLine={false}
            />

            <Tooltip
              cursor={{ fill: "rgba(148,163,184,0.08)" }}
              contentStyle={{
                borderRadius: 14,
                border: "1px solid rgba(226,232,240,0.9)",
                boxShadow: "0 12px 28px rgba(15,23,42,0.10)",
                background: "rgba(255,255,255,0.96)",
              }}
              labelStyle={{
                color: "#0f172a",
                fontWeight: 600,
                marginBottom: 6,
              }}
              formatter={(value) => {
                const numericValue =
                  typeof value === "number" ? value : Number(value ?? 0);
                return [`${numericValue}%`, "Contribution"];
              }}
            />

            {barsReady ? (
              <Bar
                dataKey="contributionPct"
                radius={[10, 10, 0, 0]}
                isAnimationActive
                animationBegin={0}
                animationDuration={1100}
                animationEasing="ease-out"
                activeBar={{
                  stroke: "#ffffff",
                  strokeWidth: 1.2,
                  fillOpacity: 1,
                }}
              >
                {chartData.map((_, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={`url(#driverBarGradient${index % colors.length})`}
                  />
                ))}
              </Bar>
            ) : null}
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}