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
    <div className="mb-10 md:mb-14">
      <div className="flex items-center gap-3 text-accent-gold/90">
        <span className="font-mono text-xs tracking-[0.25em]">{index}</span>
        <span className="h-px flex-1 max-w-[80px] bg-accent-gold/30" />
        <span className="tag">{kicker}</span>
      </div>
      <motion.h2
        initial={{ opacity: 0, y: 16 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-80px" }}
        transition={{ duration: 0.6 }}
        className="font-display text-4xl md:text-6xl tracking-tight mt-4 leading-[1.05]"
      >
        {title}
      </motion.h2>
      {subtitle && (
        <p className="mt-4 max-w-3xl text-ink-1/85 text-lg leading-relaxed">{subtitle}</p>
      )}
    </div>
  );
}

export function Card({
  children,
  className,
  glow = false
}: {
  children: React.ReactNode;
  className?: string;
  glow?: boolean;
}) {
  return (
    <div
      className={clsx(
        "glass rounded-2xl p-6 relative overflow-hidden",
        glow && "shadow-glow",
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
  color = "#E0A458"
}: {
  value: string | number;
  label: string;
  hint?: string;
  color?: string;
}) {
  return (
    <div className="flex flex-col gap-1">
      <div className="font-display text-4xl md:text-5xl font-semibold" style={{ color }}>
        {value}
      </div>
      <div className="text-ink-1/90 text-sm">{label}</div>
      {hint && <div className="text-ink-2 text-xs mt-1 leading-snug">{hint}</div>}
    </div>
  );
}

export function Pill({
  children,
  color = "#E0A458"
}: {
  children: React.ReactNode;
  color?: string;
}) {
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium"
      style={{ borderColor: `${color}55`, background: `${color}10`, color }}
    >
      {children}
    </span>
  );
}

export function Quote({ children, by }: { children: React.ReactNode; by?: string }) {
  return (
    <div className="border-l-2 border-accent-gold/60 pl-5 my-4 text-ink-1/90">
      <p className="font-display italic text-lg leading-relaxed">"{children}"</p>
      {by && <p className="mt-1 text-xs font-mono text-ink-2 tracking-wider">— {by}</p>}
    </div>
  );
}
