import { motion } from "framer-motion";
import AnimatedNumber from "../common/AnimatedNumber";
import type { ReactNode } from "react";

interface MetricCardProps {
  title: string;
  value: string;
  subtitle?: string;
  accent?: "blue" | "orange" | "green" | "purple";
  featured?: boolean;
  className?: string;
  children?: ReactNode;
}

const accentMap = {
  blue: {
    bar: "from-blue-500 via-cyan-400 to-sky-400",
    glow: "bg-blue-400/8",
    wash: "from-blue-50/70 via-white to-cyan-50/45",
    border: "group-hover:border-blue-200/70",
    text: "text-blue-600",
    softText: "text-blue-500/80",
    ring: "rgba(59,130,246,0.14)",
  },
  orange: {
    bar: "from-orange-500 via-amber-400 to-yellow-400",
    glow: "bg-orange-400/8",
    wash: "from-orange-50/70 via-white to-amber-50/45",
    border: "group-hover:border-orange-200/70",
    text: "text-orange-600",
    softText: "text-orange-500/80",
    ring: "rgba(249,115,22,0.14)",
  },
  green: {
    bar: "from-emerald-500 via-teal-400 to-green-400",
    glow: "bg-emerald-400/8",
    wash: "from-emerald-50/70 via-white to-teal-50/45",
    border: "group-hover:border-emerald-200/70",
    text: "text-emerald-600",
    softText: "text-emerald-500/80",
    ring: "rgba(16,185,129,0.14)",
  },
  purple: {
    bar: "from-violet-500 via-fuchsia-400 to-purple-400",
    glow: "bg-fuchsia-400/8",
    wash: "from-violet-50/70 via-white to-fuchsia-50/45",
    border: "group-hover:border-fuchsia-200/70",
    text: "text-violet-600",
    softText: "text-violet-500/80",
    ring: "rgba(168,85,247,0.14)",
  },
};

function parseNumericValue(value: string) {
  const cleaned = value.replace(/,/g, "").trim();

  if (/^(rising|falling|stable)$/i.test(cleaned)) {
    return null;
  }

  const numberPart = cleaned.replace(/[^\d.+-]/g, "");
  if (!numberPart || Number.isNaN(Number(numberPart))) {
    return null;
  }

  return {
    number: Number(numberPart),
    hasPlus: cleaned.startsWith("+"),
  };
}

function getTrendIcon(value: string, title: string) {
  const lowerValue = value.toLowerCase();
  const lowerTitle = title.toLowerCase();

  if (lowerValue.includes("rising")) return "↗";
  if (lowerValue.includes("falling")) return "↘";
  if (lowerValue.includes("stable")) return "→";

  if (lowerTitle.includes("delta")) {
    const num = parseNumericValue(value);
    if (!num) return null;
    if (num.number > 0) return "↗";
    if (num.number < 0) return "↘";
    return "→";
  }

  return null;
}

export default function MetricCard({
  title,
  value,
  subtitle,
  accent = "blue",
  featured = false,
  className = "",
  children,
}: MetricCardProps) {
  const theme = accentMap[accent];
  const numeric = parseNumericValue(value);
  const trendIcon = getTrendIcon(value, title);

  return (
    <motion.div
      whileHover={{
        y: -6,
        scale: 1.012,
        boxShadow: `0 24px 50px ${theme.ring}`,
      }}
      transition={{ type: "spring", stiffness: 240, damping: 20 }}
      className={[
        "group relative overflow-hidden rounded-[30px] border border-slate-200/90",
        "bg-gradient-to-br p-6 shadow-[0_12px_30px_rgba(15,23,42,0.06)]",
        "transition-colors",
        theme.wash,
        theme.border,
        featured ? "md:p-7 shadow-[0_18px_44px_rgba(15,23,42,0.08)]" : "",
        className,
      ].join(" ")}
    >
      <div className={`absolute inset-x-0 top-0 h-1 bg-gradient-to-r ${theme.bar}`} />

      <div
        className={`pointer-events-none absolute -right-8 -top-8 h-32 w-32 rounded-full blur-3xl ${theme.glow}`}
      />

      <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(180deg,rgba(255,255,255,0.58),rgba(255,255,255,0.18))]" />
      <div className="pointer-events-none absolute inset-[1px] rounded-[29px] border border-white/70" />

      <motion.div
        className={`pointer-events-none absolute top-0 h-1 w-16 bg-gradient-to-r ${theme.bar}`}
        animate={{ x: ["-20%", "360%"] }}
        transition={{ duration: 5.5, repeat: Infinity, ease: "linear" }}
      />

      <div className="relative flex h-full flex-col">
        <div className="flex items-start justify-between gap-4">
          <p className="text-[15px] font-semibold tracking-tight text-slate-500">
            {title}
          </p>

          <div
            className={[
              "hidden rounded-full border border-white/70 bg-white/65 px-2.5 py-1",
              "text-[11px] font-semibold md:block",
              theme.softText,
            ].join(" ")}
          >
            Live
          </div>
        </div>

        <div className="mt-6 flex-1">
          <div className="flex items-center gap-2.5">
            {trendIcon ? (
              <span
                className={[
                  "font-semibold leading-none",
                  featured ? "text-[34px]" : "text-2xl",
                  theme.text,
                ].join(" ")}
              >
                {trendIcon}
              </span>
            ) : null}

            <h3
              className={[
                "truncate font-bold tracking-tight text-slate-950",
                featured ? "text-6xl md:text-7xl" : "text-5xl",
              ].join(" ")}
            >
              {numeric ? (
                <span>
                  <AnimatedNumber
                    value={numeric.number}
                    duration={1200}
                    decimals={String(numeric.number).includes(".") ? 2 : 0}
                    prefix={numeric.hasPlus ? "+" : ""}
                  />
                </span>
              ) : (
                value
              )}
            </h3>
          </div>

          {subtitle ? (
            <p
              className={[
                "text-slate-600",
                featured ? "mt-5 text-lg leading-7" : "mt-3 text-[15px] leading-6",
              ].join(" ")}
            >
              {subtitle}
            </p>
          ) : null}
        </div>

        {children ? (
          <div className="mt-6 border-t border-slate-200/60 pt-4">
            {children}
          </div>
        ) : null}

        <div className="mt-6 h-[4px] w-full rounded-full bg-slate-200/60">
          <motion.div
            className={`h-[4px] rounded-full bg-gradient-to-r ${theme.bar}`}
            initial={{ width: "26%" }}
            animate={{ width: ["26%", "34%", "26%"] }}
            transition={{ duration: 3.2, repeat: Infinity, ease: "easeInOut" }}
          />
        </div>
      </div>
    </motion.div>
  );
}