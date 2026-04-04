import { useEffect, useRef, useState } from "react";
import { useInView } from "framer-motion";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from "recharts";
import type { GssiComponentPoint } from "../../types/gssi";

export default function ComponentLineChart({
  data,
}: {
  data: GssiComponentPoint[];
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
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(37,99,235,0.04),transparent_28%),radial-gradient(circle_at_top_right,rgba(124,58,237,0.04),transparent_24%)]" />

      <div className="relative mb-4">
        <h2 className="text-xl font-semibold text-slate-900">Indicator Trends</h2>
        <p className="text-sm text-slate-500">
          How each component evolved over time
        </p>
      </div>

      <div className="relative h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={data}
            margin={{ top: 8, right: 18, left: 2, bottom: 0 }}
          >
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
            />

            <Legend
              wrapperStyle={{
                paddingTop: 10,
                fontSize: 12,
                color: "#475569",
              }}
              iconType="circle"
            />

            {seriesReady ? (
              <>
                <Line
                  type="monotone"
                  dataKey="oil"
                  name="Oil"
                  stroke="#2563eb"
                  strokeWidth={3}
                  dot={false}
                  activeDot={{
                    r: 5,
                    fill: "#2563eb",
                    stroke: "#ffffff",
                    strokeWidth: 2,
                  }}
                  isAnimationActive
                  animationBegin={0}
                  animationDuration={1000}
                  animationEasing="ease-out"
                />

                <Line
                  type="monotone"
                  dataKey="volatility"
                  name="Volatility"
                  stroke="#7c3aed"
                  strokeWidth={3}
                  dot={false}
                  activeDot={{
                    r: 5,
                    fill: "#7c3aed",
                    stroke: "#ffffff",
                    strokeWidth: 2,
                  }}
                  isAnimationActive
                  animationBegin={80}
                  animationDuration={1000}
                  animationEasing="ease-out"
                />

                <Line
                  type="monotone"
                  dataKey="freight"
                  name="Freight"
                  stroke="#f97316"
                  strokeWidth={3}
                  dot={false}
                  activeDot={{
                    r: 5,
                    fill: "#f97316",
                    stroke: "#ffffff",
                    strokeWidth: 2,
                  }}
                  isAnimationActive
                  animationBegin={160}
                  animationDuration={1000}
                  animationEasing="ease-out"
                />

                <Line
                  type="monotone"
                  dataKey="supplier"
                  name="Supplier"
                  stroke="#14b8a6"
                  strokeWidth={3}
                  dot={false}
                  activeDot={{
                    r: 5,
                    fill: "#14b8a6",
                    stroke: "#ffffff",
                    strokeWidth: 2,
                  }}
                  isAnimationActive
                  animationBegin={240}
                  animationDuration={1000}
                  animationEasing="ease-out"
                />

                <Line
                  type="monotone"
                  dataKey="inventory"
                  name="Inventory"
                  stroke="#ef4444"
                  strokeWidth={3}
                  dot={false}
                  activeDot={{
                    r: 5,
                    fill: "#ef4444",
                    stroke: "#ffffff",
                    strokeWidth: 2,
                  }}
                  isAnimationActive
                  animationBegin={320}
                  animationDuration={1000}
                  animationEasing="ease-out"
                />
              </>
            ) : null}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}