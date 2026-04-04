import { motion, type Variants } from "framer-motion";
import AlertStatusCard from "../components/cards/AlertStatusCard";
import GssiHistoryChart from "../components/charts/GssiHistoryChart";
import ComponentLineChart from "../components/charts/ComponentLineChart";
import SummaryPanel from "../components/panels/SummaryPanel";
import MethodPanel from "../components/panels/MethodPanel";
import MetricCluster from "../components/cards/MetricCluster";

import { useGssiData } from "../hooks/useGssiData";
import { formatNumber, trendLabel } from "../utils/format";

export default function Dashboard() {
  const {
    current,
    history,
    forecast,
    drivers,
    summary,
    components,
    loading,
    error,
  } = useGssiData();

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-100">
        <div className="rounded-3xl border border-slate-200 bg-white px-8 py-5 shadow-lg">
          <p className="font-medium text-slate-700">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error || !current || !forecast || !summary) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-100 p-6">
        <div className="max-w-md rounded-3xl border border-red-200 bg-white p-6 shadow-lg">
          <h2 className="text-xl font-semibold text-red-700">Error</h2>
          <p className="mt-2 text-sm text-slate-700">
            {error ?? "Something went wrong while loading the dashboard."}
          </p>
        </div>
      </div>
    );
  }

  const trend = trendLabel(current.gssi, forecast.predicted_gssi);
  const delta = forecast.predicted_gssi - current.gssi;

  const containerVariants: Variants = {
    hidden: {},
    show: {
      transition: {
        staggerChildren: 0.12,
      },
    },
  };

  const itemVariants: Variants = {
    hidden: {
      opacity: 0,
      y: 24,
      scale: 0.985,
    },
    show: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: {
        duration: 0.55,
      },
    },
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.45 }}
      className="min-h-screen bg-slate-100 px-4 py-6 md:px-8"
    >
      <motion.div
        className="mx-auto max-w-7xl space-y-6"
        variants={containerVariants}
        initial="hidden"
        animate="show"
      >
        <motion.header
          variants={itemVariants}
          whileHover={{
            y: -4,
            scale: 1.003,
            boxShadow: "0 30px 80px rgba(15, 23, 42, 0.30)",
          }}
          transition={{ type: "spring", stiffness: 180, damping: 20 }}
          className="group relative overflow-hidden rounded-[38px] border border-white/10 bg-gradient-to-br from-[#071224] via-[#0a1633] to-[#1d2d68] px-8 py-8 text-white shadow-[0_25px_70px_rgba(15,23,42,0.22)] md:px-10 md:py-10"
        >
          {/* background glows */}
          <div className="pointer-events-none absolute inset-0">
            <div className="absolute left-[-5%] top-[55%] h-[300px] w-[300px] rounded-full bg-cyan-400/15 blur-3xl" />
            <div className="absolute right-[-6%] top-[8%] h-[340px] w-[340px] rounded-full bg-violet-400/25 blur-3xl" />
            <div className="absolute right-[8%] top-[28%] h-[220px] w-[220px] rounded-full bg-cyan-400/15 blur-3xl" />
            <div className="absolute left-[32%] top-[0%] h-[180px] w-[180px] rounded-full bg-blue-400/10 blur-3xl" />
          </div>

          {/* stronger finance curves */}
          <svg
            className="pointer-events-none absolute inset-0 h-full w-full opacity-90"
            viewBox="0 0 1200 420"
            fill="none"
            preserveAspectRatio="none"
          >
            <defs>
              <linearGradient id="heroCurveBright" x1="0" y1="0" x2="1200" y2="420">
                <stop offset="0%" stopColor="#22d3ee" />
                <stop offset="30%" stopColor="#38bdf8" />
                <stop offset="65%" stopColor="#818cf8" />
                <stop offset="100%" stopColor="#c084fc" />
              </linearGradient>

              <linearGradient id="heroCurveSoft" x1="0" y1="0" x2="1200" y2="420">
                <stop offset="0%" stopColor="#0ea5e9" />
                <stop offset="100%" stopColor="#38bdf8" />
              </linearGradient>

              <filter id="curveGlow">
                <feGaussianBlur stdDeviation="8" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>

            <path
              d="M -40 350 C 220 240, 480 420, 760 230 C 930 130, 1080 110, 1240 20"
              stroke="url(#heroCurveBright)"
              strokeWidth="5"
              fill="none"
              filter="url(#curveGlow)"
              strokeLinecap="round"
            />

            <path
              d="M 520 410 C 760 340, 940 260, 1220 60"
              stroke="url(#heroCurveSoft)"
              strokeOpacity="0.4"
              strokeWidth="2.5"
              fill="none"
              strokeLinecap="round"
            />
          </svg>

          {/* glossy light beam */}
          <div className="pointer-events-none absolute -right-[8%] top-[28%] h-[220px] w-[42%] rotate-[-12deg] bg-gradient-to-r from-transparent via-white/10 to-transparent blur-xl" />

          <div className="relative grid grid-cols-1 gap-10 lg:grid-cols-[1.25fr_0.85fr] lg:items-center">
            {/* LEFT SIDE */}
            <div className="max-w-4xl">
              <motion.div
                whileHover={{ scale: 1.04 }}
                transition={{ type: "spring", stiffness: 260, damping: 18 }}
                className="relative inline-flex overflow-hidden rounded-full bg-white/10 px-5 py-2 text-sm font-medium text-blue-100 ring-1 ring-white/15 backdrop-blur-sm"
              >
                <motion.span
                  className="absolute inset-0"
                  style={{
                    background:
                      "linear-gradient(120deg, transparent, rgba(255,255,255,0.35), transparent)",
                  }}
                  animate={{ x: ["-120%", "120%"] }}
                  transition={{ duration: 2.8, repeat: Infinity, ease: "linear" }}
                />
                <span className="relative z-10">
                  Macro-Financial Early Warning System
                </span>
              </motion.div>

              <motion.h1
                initial={false}
                whileHover={{ x: 2 }}
                transition={{ type: "spring", stiffness: 220, damping: 18 }}
                className="mt-7 max-w-4xl text-5xl font-bold leading-[0.95] tracking-tight md:text-6xl xl:text-7xl"
              >
                Global Supply
                <br />
                Chain Stress Index
              </motion.h1>

              <motion.p
                initial={false}
                whileHover={{ x: 2 }}
                transition={{
                  type: "spring",
                  stiffness: 220,
                  damping: 18,
                  delay: 0.03,
                }}
                className="mt-8 max-w-3xl text-lg leading-9 text-slate-200"
              >
                Monitor supply chain disruption, stress drivers, and short-term
                risk outlook through a single interpretable dashboard.
              </motion.p>

              <div className="mt-8 flex flex-wrap gap-3">
                <motion.div
                  whileHover={{ y: -2, scale: 1.02 }}
                  className="rounded-2xl bg-white/10 px-4 py-2.5 text-sm font-medium text-slate-100 ring-1 ring-white/10 backdrop-blur-sm"
                >
                  📊 5 core indicators
                </motion.div>
                <motion.div
                  whileHover={{ y: -2, scale: 1.02 }}
                  className="rounded-2xl bg-white/10 px-4 py-2.5 text-sm font-medium text-slate-100 ring-1 ring-white/10 backdrop-blur-sm"
                >
                  📈 Weekly forecast
                </motion.div>
                <motion.div
                  whileHover={{ y: -2, scale: 1.02 }}
                  className="rounded-2xl bg-white/10 px-4 py-2.5 text-sm font-medium text-slate-100 ring-1 ring-white/10 backdrop-blur-sm"
                >
                  ⚡ Real-time risk view
                </motion.div>
              </div>
            </div>

            {/* RIGHT SIDE */}
            <div className="relative flex min-h-[380px] items-center justify-center lg:justify-end">
              <motion.div
                whileHover={{ y: -6, scale: 1.02 }}
                transition={{ type: "spring", stiffness: 220, damping: 18 }}
                className="relative z-10"
              >
                <AlertStatusCard alert={current.alert} week={current.week} />
              </motion.div>
            </div>
          </div>
        </motion.header>

        <motion.section variants={itemVariants}>
          <MetricCluster
            currentGssi={formatNumber(current.gssi)}
            currentWeek={`Week of ${current.week}`}
            forecastValue={formatNumber(forecast.predicted_gssi)}
            forecastWeek={`Forecast for ${forecast.week}`}
            trend={trend}
            trendSubtitle="Top Drivers"
            delta={`${delta >= 0 ? "+" : ""}${formatNumber(delta)}`}
            deltaSubtitle="Expected weekly change"
            drivers={drivers}
          />
        </motion.section>

        <motion.section variants={itemVariants}>
          <GssiHistoryChart
            data={history}
            forecastValue={forecast.predicted_gssi}
          />
        </motion.section>

        <motion.section variants={itemVariants}>
          <ComponentLineChart data={components} />
        </motion.section>

        <motion.section
          variants={itemVariants}
          className="grid gap-6 xl:grid-cols-2"
        >
          <SummaryPanel summary={summary.summary} />
          <MethodPanel />
        </motion.section>
      </motion.div>
    </motion.div>
  );
}