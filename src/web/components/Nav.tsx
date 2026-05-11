"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import clsx from "clsx";

const SECTIONS = [
  { id: "hero", label: "โจทย์" },
  { id: "raw", label: "ข้อมูลดิบ" },
  { id: "clean", label: "เคลียร์ข้อมูล" },
  { id: "select", label: "ฟีเจอร์" },
  { id: "personas", label: "กลุ่มลูกค้า" },
  { id: "drivers", label: "ตัวขับ" },
  { id: "predict", label: "ลองทำนาย" },
  { id: "plan", label: "แผนยิง" }
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
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.35 }}
      className={clsx(
        "fixed top-0 inset-x-0 z-50 transition-all duration-200",
        scrolled
          ? "bg-white/80 backdrop-blur-md border-b border-ink-3/40 shadow-soft"
          : "bg-transparent"
      )}
    >
      <div className="max-w-6xl mx-auto flex items-center justify-between px-6 h-14">
        <a href="#hero" className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-md bg-accent-gold flex items-center justify-center text-white font-semibold text-sm">
            R
          </div>
          <span className="font-semibold text-sm text-ink-0">RTD Coffee Research</span>
        </a>

        <div className="hidden lg:flex items-center gap-0.5 text-[13px]">
          {SECTIONS.map((s) => (
            <a
              key={s.id}
              href={`#${s.id}`}
              className={clsx(
                "relative px-3 py-1.5 rounded-md transition-colors",
                active === s.id
                  ? "text-accent-gold font-medium"
                  : "text-ink-2 hover:text-ink-0"
              )}
            >
              {s.label}
              {active === s.id && (
                <motion.span
                  layoutId="nav-indicator"
                  className="absolute bottom-0 left-3 right-3 h-[2px] bg-accent-gold rounded-full"
                  transition={{ type: "spring", stiffness: 500, damping: 35 }}
                />
              )}
            </a>
          ))}
        </div>

        <a href="#predict" className="btn-primary px-4 py-1.5 text-sm">
          ลองโมเดล
        </a>
      </div>
    </motion.nav>
  );
}
