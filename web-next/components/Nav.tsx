"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import clsx from "clsx";

const SECTIONS = [
  { id: "hero", label: "00 — โจทย์" },
  { id: "raw", label: "01 — ข้อมูลดิบ" },
  { id: "clean", label: "02 — เคลียร์ข้อมูล" },
  { id: "select", label: "03 — ฟีเจอร์" },
  { id: "personas", label: "04 — กลุ่มลูกค้า" },
  { id: "drivers", label: "05 — ตัวขับ" },
  { id: "predict", label: "06 — ลองทำนาย" },
  { id: "plan", label: "07 — แผนยิง" }
];

export default function Nav() {
  const [active, setActive] = useState("hero");
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) setActive(e.target.id);
        });
      },
      { rootMargin: "-30% 0px -55% 0px" }
    );
    SECTIONS.forEach((s) => {
      const el = document.getElementById(s.id);
      if (el) observer.observe(el);
    });
    return () => {
      window.removeEventListener("scroll", onScroll);
      observer.disconnect();
    };
  }, []);

  return (
    <motion.nav
      initial={{ y: -30, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
      className={clsx(
        "fixed top-0 inset-x-0 z-50 transition-all duration-300",
        scrolled ? "backdrop-blur-xl bg-bg-0/70 border-b border-white/5" : "bg-transparent"
      )}
    >
      <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 rounded-md bg-gradient-to-br from-accent-gold to-accent-copper flex items-center justify-center font-display font-bold text-bg-0">
            R
          </div>
          <div className="leading-tight">
            <div className="font-display text-base">RTD Coffee</div>
            <div className="text-[10px] text-ink-2 font-mono tracking-widest uppercase">
              เข้าใจลูกค้า · เจาะลึก
            </div>
          </div>
        </div>
        <div className="hidden lg:flex items-center gap-1 text-xs font-mono">
          {SECTIONS.map((s) => (
            <a
              key={s.id}
              href={`#${s.id}`}
              className={clsx(
                "px-3 py-1.5 rounded-full transition-colors",
                active === s.id
                  ? "text-accent-gold bg-accent-gold/10"
                  : "text-ink-2 hover:text-ink-1"
              )}
            >
              {s.label}
            </a>
          ))}
        </div>
        <a href="#predict" className="btn-primary rounded-full px-4 py-2 text-sm">
          ลองโมเดลเลย →
        </a>
      </div>
    </motion.nav>
  );
}
