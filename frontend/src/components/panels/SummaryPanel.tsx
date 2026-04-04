import { useEffect, useMemo, useRef, useState } from "react";
import { useInView, motion } from "framer-motion";

function AnimatedWords({
  text,
  delay = 0,
}: {
  text: string;
  delay?: number;
}) {
  const ref = useRef<HTMLDivElement | null>(null);
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
      }, 55);

      return () => window.clearInterval(interval);
    }, delay);

    return () => window.clearTimeout(startTimer);
  }, [isInView, words.length, delay]);

  return (
    <div ref={ref} className="text-sm leading-8 text-slate-700">
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
    </div>
  );
}

export default function SummaryPanel({ summary }: { summary: string }) {
  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-lg">
      <div className="mb-4 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-blue-100 font-bold text-blue-700">
          AI
        </div>
        <div>
          <h2 className="text-xl font-semibold text-slate-900">
            AI / Macro Summary
          </h2>
          <p className="text-sm text-slate-500">
            Interpretable decision-support note
          </p>
        </div>
      </div>

      <AnimatedWords text={summary} delay={120} />
    </div>
  );
}