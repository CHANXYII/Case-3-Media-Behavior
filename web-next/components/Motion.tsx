"use client";
import { useEffect, useRef, useState } from "react";
import { motion, useInView, useMotionValue, useScroll, useSpring, useTransform } from "framer-motion";

export function ScrollProgress() {
  const { scrollYProgress } = useScroll();
  const x = useSpring(scrollYProgress, { stiffness: 220, damping: 30, restDelta: 0.001 });
  return (
    <motion.div
      style={{ scaleX: x, transformOrigin: "0% 50%" }}
      className="fixed top-0 left-0 right-0 h-[2px] bg-accent-gold z-[60] pointer-events-none"
    />
  );
}

export function CountUp({
  to,
  from = 0,
  duration = 1.4,
  decimals = 0,
  suffix = "",
  prefix = "",
  className
}: {
  to: number;
  from?: number;
  duration?: number;
  decimals?: number;
  suffix?: string;
  prefix?: string;
  className?: string;
}) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: "-15% 0px" });
  const value = useMotionValue(from);
  const [display, setDisplay] = useState(from);

  useEffect(() => {
    if (!inView) return;
    const controls = value.on("change", (v) => setDisplay(v));
    const start = performance.now();
    let raf = 0;
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / (duration * 1000));
      const eased = 1 - Math.pow(1 - t, 3);
      value.set(from + (to - from) * eased);
      if (t < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => {
      cancelAnimationFrame(raf);
      controls();
    };
  }, [inView, to, from, duration, value]);

  const formatted =
    decimals > 0
      ? display.toFixed(decimals)
      : Math.round(display).toLocaleString("en-US");

  return (
    <span ref={ref} className={className}>
      {prefix}
      {formatted}
      {suffix}
    </span>
  );
}

export function Reveal({
  children,
  delay = 0,
  y = 18,
  className
}: {
  children: React.ReactNode;
  delay?: number;
  y?: number;
  className?: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-12% 0px" }}
      transition={{ duration: 0.55, delay, ease: [0.2, 0.8, 0.2, 1] }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

export function WordReveal({
  text,
  className,
  highlight,
  delay = 0
}: {
  text: string;
  className?: string;
  highlight?: string[];
  delay?: number;
}) {
  const words = text.split(" ");
  return (
    <span className={className}>
      {words.map((w, i) => {
        const isHighlight = highlight?.includes(w);
        return (
          <span key={i} className="headline-mask mr-[0.25em]">
            <motion.span
              initial={{ y: "110%" }}
              animate={{ y: "0%" }}
              transition={{ duration: 0.7, delay: delay + i * 0.06, ease: [0.2, 0.8, 0.2, 1] }}
              className={isHighlight ? "text-accent-gold" : ""}
            >
              {w}
            </motion.span>
          </span>
        );
      })}
    </span>
  );
}

export function Marquee({
  items,
  separator = "·"
}: {
  items: string[];
  separator?: string;
}) {
  const loop = [...items, ...items];
  return (
    <div className="marquee-track overflow-hidden">
      <div className="marquee">
        {loop.map((s, i) => (
          <span key={i} className="inline-flex items-center gap-6 whitespace-nowrap font-mono text-[12px] uppercase tracking-[0.18em] text-ink-2">
            {s}
            <span className="text-accent-gold">{separator}</span>
          </span>
        ))}
      </div>
    </div>
  );
}

export function ParallaxLayer({
  children,
  amount = 60,
  className
}: {
  children: React.ReactNode;
  amount?: number;
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start end", "end start"] });
  const y = useTransform(scrollYProgress, [0, 1], [amount, -amount]);
  return (
    <motion.div ref={ref as any} style={{ y }} className={className}>
      {children}
    </motion.div>
  );
}
