import { motion } from "framer-motion";
import type { AlertLevel } from "../../types/gssi";

interface AlertStatusCardProps {
  alert: AlertLevel;
  week: string;
}

const styles: Record<
  AlertLevel,
  {
    frontShell: string;
    frontBorder: string;
    title: string;
    body: string;
    badgeBg: string;
    badgeText: string;
    dot: string;
    line: string;
    panelGlow: string;
    chipBg: string;
    chipText: string;
  }
> = {
  Low: {
    frontShell: "from-emerald-950/92 via-emerald-900/88 to-green-900/82",
    frontBorder: "border-emerald-200/14",
    title: "text-emerald-100/80",
    body: "text-emerald-50/88",
    badgeBg: "bg-emerald-50/95",
    badgeText: "text-emerald-700",
    dot: "bg-emerald-200",
    line: "bg-emerald-100/22",
    panelGlow: "shadow-[0_0_40px_rgba(74,222,128,0.14)]",
    chipBg: "from-emerald-100 to-white",
    chipText: "text-emerald-700",
  },
  Moderate: {
    frontShell: "from-yellow-950/92 via-amber-900/88 to-yellow-900/82",
    frontBorder: "border-yellow-200/14",
    title: "text-yellow-100/80",
    body: "text-yellow-50/88",
    badgeBg: "bg-yellow-50/95",
    badgeText: "text-yellow-700",
    dot: "bg-yellow-200",
    line: "bg-yellow-100/22",
    panelGlow: "shadow-[0_0_40px_rgba(250,204,21,0.14)]",
    chipBg: "from-yellow-100 to-white",
    chipText: "text-yellow-700",
  },
  High: {
    frontShell: "from-[#4d1236]/95 via-[#67163c]/92 to-[#812049]/88",
    frontBorder: "border-pink-200/14",
    title: "text-pink-100/80",
    body: "text-pink-50/90",
    badgeBg: "bg-[#fff6ea]",
    badgeText: "text-[#e27414]",
    dot: "bg-pink-200",
    line: "bg-pink-100/22",
    panelGlow: "shadow-[0_0_44px_rgba(236,72,153,0.18)]",
    chipBg: "from-cyan-100 via-white to-cyan-50",
    chipText: "text-[#3657a7]",
  },
  Critical: {
    frontShell: "from-red-950/94 via-rose-900/90 to-red-900/84",
    frontBorder: "border-red-200/14",
    title: "text-red-100/80",
    body: "text-red-50/90",
    badgeBg: "bg-red-50/95",
    badgeText: "text-red-700",
    dot: "bg-red-200",
    line: "bg-red-100/22",
    panelGlow: "shadow-[0_0_44px_rgba(248,113,113,0.18)]",
    chipBg: "from-red-100 to-white",
    chipText: "text-red-700",
  },
};

export default function AlertStatusCard({
  alert,
  week,
}: AlertStatusCardProps) {
  const s = styles[alert];

  return (
    <motion.div
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4, scale: 1.012 }}
      transition={{ type: "spring", stiffness: 180, damping: 18 }}
      className="relative h-[355px] w-[400px]"
    >

      {/* front main panel */}
      <div
        className={[
          "absolute right-[62px] top-[56px] h-[200px] w-[300px] overflow-hidden",
          "rounded-[26px] border bg-gradient-to-br px-8 py-6 backdrop-blur-xl",
          s.frontShell,
          s.frontBorder,
          s.panelGlow,
        ].join(" ")}
      >
        
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_100%_0%,rgba(255,255,255,0.12),transparent_28%),linear-gradient(180deg,rgba(255,255,255,0.06),transparent_38%)]" />
        <div className="pointer-events-none absolute inset-[1px] rounded-[24px] border border-white/6" />

        <div className="relative">
          <div className="flex items-center justify-between">
            <p className={`text-[11px] uppercase tracking-[0.34em] ${s.title}`}>
              Latest Alert
            </p>

            <motion.div
              animate={{
                opacity: [0.45, 1, 0.45],
                scale: [1, 1.18, 1],
              }}
              transition={{
                duration: 1.8,
                repeat: Infinity,
                ease: "easeInOut",
              }}
              className={`mt-0.5 h-3.5 w-3.5 rounded-full ${s.dot} shadow-[0_0_16px_rgba(255,255,255,0.16)]`}
            />
          </div>

          <div className="mt-8">
            <div
              className={[
                "inline-flex min-w-[110px] items-center justify-center rounded-full",
                "px-7 py-2.5 text-[20px] font-semibold",
                "shadow-[0_10px_28px_rgba(0,0,0,0.18)]",
                s.badgeBg,
                s.badgeText,
              ].join(" ")}
            >
              {alert}
            </div>
          </div>

          <p className={`mt-6 text-[14px] font-medium leading-6 ${s.body}`}>
            Updated for week of {week}
          </p>

          <div className="mt-8 h-[5px] w-full rounded-full bg-white/10">
            <motion.div
              className={`h-[5px] rounded-full ${s.line}`}
              style={{ width: "64%" }}
              animate={{
                opacity: [0.65, 1, 0.65],
                width: ["54%", "68%", "54%"],
              }}
              transition={{
                duration: 2.4,
                repeat: Infinity,
                ease: "easeInOut",
              }}
            />
          </div>
        </div>
      </div>

      {/* bottom chip */}
      <motion.div
        whileHover={{ y: -2 }}
        className={[
          "absolute bottom-[70px] right-[85px] z-20 h-[42px] w-[250px]",
          "rounded-full border border-cyan-100/28 bg-gradient-to-r",
          s.chipBg,
          "shadow-[0_10px_25px_rgba(114,219,255,0.18)]",
          "backdrop-blur-xl",
        ].join(" ")}
      >
        <div className="flex h-full items-center gap-2 px-5">
          <div className="flex h-6 w-6 items-center justify-center rounded-full bg-cyan-200/80 text-cyan-900 shadow-inner">
            <span className="text-xs">↓</span>
          </div>

          <span className={`text-[13px] font-semibold ${s.chipText}`}>
            Market pressure rising
          </span>
        </div>
      </motion.div>

      <div className="pointer-events-none absolute bottom-[32px] right-[34px] h-[110px] w-[260px] bg-[radial-gradient(circle_at_center,rgba(110,215,255,0.16),transparent_68%)] blur-2xl" />
    </motion.div>
  );
}