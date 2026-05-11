"use client";
import { motion } from "framer-motion";
import clsx from "clsx";

export function SectionHeader({
  index,
  kicker,
  title,
  subtitle
}: {
  index: string;
  kicker: string;
  title: string;
  subtitle?: string;
}) {
  return (
    <div className="mb-10 md:mb-14 max-w-3xl">
      <div className="flex items-center gap-3">
        <span className="font-display text-2xl font-bold text-accent-gold tabular leading-none">{index}</span>
        <span className="h-px w-10 bg-ink-3" />
        <span className="tag text-accent-copper">{kicker}</span>
      </div>
      <motion.h2
        initial={{ opacity: 0, y: 14 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-80px" }}
        transition={{ duration: 0.55, ease: [0.2, 0.8, 0.2, 1] }}
        className="font-display text-3xl md:text-[44px] tracking-[-0.025em] mt-4 leading-[1.28] font-bold text-ink-0 py-1"
      >
        {title}
      </motion.h2>
      {subtitle && (
        <motion.p
          initial={{ opacity: 0, y: 8 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="mt-4 text-ink-2 text-[15px] md:text-base leading-relaxed"
        >
          {subtitle}
        </motion.p>
      )}
    </div>
  );
}

export function Card({
  children,
  className
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={clsx(
        "surface p-6 relative",
        className
      )}
    >
      {children}
    </div>
  );
}

export function StatBlock({
  value,
  label,
  hint,
  color
}: {
  value: string | number;
  label: string;
  hint?: string;
  color?: string;
}) {
  return (
    <div className="flex flex-col gap-1">
      <div className="text-3xl md:text-4xl font-semibold tabular" style={color ? { color } : { color: "#0c0a09" }}>
        {value}
      </div>
      <div className="text-ink-1 text-sm font-medium">{label}</div>
      {hint && <div className="text-ink-2 text-xs mt-0.5 leading-snug">{hint}</div>}
    </div>
  );
}

export function Pill({
  children,
  color = "#57534E"
}: {
  children: React.ReactNode;
  color?: string;
}) {
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-[11px] font-medium tabular"
      style={{ borderColor: `${color}40`, background: `${color}0d`, color }}
    >
      {children}
    </span>
  );
}

export function Quote({ children, by }: { children: React.ReactNode; by?: string }) {
  return (
    <div className="border-l-2 border-accent-gold pl-4 my-4">
      <p className="italic text-ink-1 text-[15px] leading-relaxed">"{children}"</p>
      {by && <p className="mt-1 text-xs font-mono text-ink-2">— {by}</p>}
    </div>
  );
}

export function Callout({
  label = "สรุป",
  children
}: {
  label?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="border-l-2 border-accent-gold bg-accent-cream/40 rounded-r-md px-4 py-3 text-[13px] text-ink-1 leading-relaxed">
      <span className="tag mr-2 text-accent-copper">{label}</span>
      {children}
    </div>
  );
}
