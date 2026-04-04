import { useEffect, useMemo, useRef, useState } from "react";
import { useInView, motion } from "framer-motion";

function AnimatedWords({
  text,
  delay = 0,
}: {
  text: string;
  delay?: number;
}) {
  const ref = useRef<HTMLParagraphElement | null>(null);
  const isInView = useInView(ref, {
    once: true,
    margin: "-10% 0px -10% 0px",
  });

  const words = useMemo(() => text.split(" "), [text]);
  const [visibleCount, setVisibleCount] = useState(0);

  useEffect(() => {
    if (!isInView) return;

    const startTimer = window.setTimeout(() => {
      let index = 0;

      const interval = window.setInterval(() => {
        index += 1;
        setVisibleCount(index);

        if (index >= words.length) {
          window.clearInterval(interval);
        }
      }, 50);

      return () => window.clearInterval(interval);
    }, delay);

    return () => window.clearTimeout(startTimer);
  }, [isInView, words.length, delay]);

  return (
    <p ref={ref} className="text-sm leading-7 text-slate-700">
      {words.map((word, index) => (
        <motion.span
          key={`${word}-${index}`}
          initial={{ opacity: 0, y: 8, filter: "blur(4px)" }}
          animate={
            index < visibleCount
              ? { opacity: 1, y: 0, filter: "blur(0px)" }
              : { opacity: 0, y: 8, filter: "blur(4px)" }
          }
          transition={{ duration: 0.28, ease: "easeOut" }}
          className="inline-block"
          style={{ marginRight: "0.35em" }}
        >
          {word}
        </motion.span>
      ))}
    </p>
  );
}

export default function MethodPanel() {
  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-lg">
      <h2 className="text-xl font-semibold text-slate-900">
        How the Prediction Works
      </h2>

      <div className="mt-4 space-y-3">
        <AnimatedWords
          text="The system aggregates freight cost, supplier delay, oil price, market volatility, and inventory stress into a normalized weekly GSSI score."
          delay={100}
        />

        <AnimatedWords
          text="A forecasting layer estimates next-week stress, while the dashboard highlights alert level, driver contribution, and recent trends."
          delay={450}
        />

        <AnimatedWords
          text="This gives users a simple macro-financial early-warning view instead of forcing them to interpret raw indicators one by one."
          delay={800}
        />
      </div>
    </div>
  );
}