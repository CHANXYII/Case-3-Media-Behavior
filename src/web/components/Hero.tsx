"use client";
import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import { CountUp, Marquee, Reveal, WordReveal } from "./Motion";

const TICKER = [
  "181 ผู้ตอบจริง",
  "120 ฟีเจอร์ที่ใช้งานได้",
  "3 กลุ่มลูกค้า",
  "F1 macro 0.62",
  "Silhouette 0.30",
  "RTD launch · สงกรานต์ 2026",
  "พฤติกรรมสื่อ × ความชอบกาแฟ",
  "9 ตัวขับที่นัยสำคัญ p<0.05"
];

export default function Hero() {
  return (
    <section id="hero" className="relative pt-28 md:pt-32 pb-16 overflow-hidden">
      <div
        aria-hidden
        className="absolute -top-40 -right-32 w-[520px] h-[520px] rounded-full pointer-events-none"
        style={{
          background: "radial-gradient(circle, rgba(194,65,12,0.10), transparent 60%)"
        }}
      />

      <div className="max-w-6xl mx-auto px-6">
        <Reveal delay={0}>
          <div className="flex items-center gap-3 mb-6">
            <span className="inline-flex items-center gap-2 rounded-full bg-accent-gold/10 border border-accent-gold/30 px-3 py-1">
              <span className="w-1.5 h-1.5 rounded-full bg-accent-gold animate-pulse" />
              <span className="font-mono text-[11px] uppercase tracking-[0.14em] text-accent-copper">Case 03 · Live Brief</span>
            </span>
            <span className="h-px flex-1 bg-ink-3/60 max-w-[160px]" />
            <span className="text-xs font-mono text-ink-2 tabular">181 คน · 120 ฟีเจอร์</span>
          </div>
        </Reveal>

        <h1 className="font-display text-[44px] md:text-7xl lg:text-[88px] leading-[1.25] tracking-[-0.03em] font-bold text-ink-0 max-w-5xl">
          <span className="block py-3 md:py-4">
            <WordReveal text="จากร้านกาแฟ 4,000 สาขา" />
          </span>
          <motion.span
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.55, ease: [0.2, 0.8, 0.2, 1] }}
            className="shine-text font-display block py-3 md:py-4 mt-2 md:mt-3"
          >
            สู่ขวดบนชั้นในเซเว่น.
          </motion.span>
        </h1>

        <Reveal delay={0.55} className="mt-7">
          <p className="text-[16px] md:text-lg text-ink-2 max-w-2xl leading-relaxed">
            แบรนด์กาแฟที่มีร้านกว่า 4,000 สาขากำลังจะออกกาแฟพร้อมดื่มขายในเซเว่น
            คำถามคือ <strong className="text-ink-0 font-semibold">ควรคุยกับใคร</strong>
            ขายจุดไหน แล้ว <strong className="text-ink-0 font-semibold">เทงบไปช่องทางไหน</strong> ถึงจะคุ้ม
            เราเก็บแบบสอบถาม 181 คน แบ่งเป็น 3 กลุ่ม แล้วสร้างโมเดลแยกทีละกลุ่มเพื่อหาคำตอบ
          </p>
        </Reveal>

        <Reveal delay={0.7} className="mt-9">
          <div className="flex flex-wrap gap-3">
            <motion.a
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              href="#raw"
              className="btn-primary px-6 py-3 inline-flex items-center gap-2 text-sm"
            >
              Pipeline <ArrowRight size={16} />
            </motion.a>
            <motion.a
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              href="#predict"
              className="btn-secondary px-6 py-3 inline-flex items-center gap-2 text-sm"
            >
              ลองทำนาย
            </motion.a>
          </div>
        </Reveal>

        <Reveal delay={0.85} className="mt-16">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-px bg-ink-3/50 rounded-2xl overflow-hidden border border-ink-3/50 shadow-soft">
            {[
              { v: 181, l: "คนที่ตอบแบบสอบถาม", h: "หลังตัดแถวที่ข้อมูลว่างทิ้ง", suffix: "" },
              { v: 120, l: "ฟีเจอร์ที่ใช้งานได้", h: "จากคำถามไทย 76 ข้อ", suffix: "" },
              { v: 3, l: "กลุ่มลูกค้า · K-Means", h: "Silhouette = 0.30", suffix: "" },
              { v: 0.62, l: "F1 macro สูงสุด", h: "3-class stratified CV", decimals: 2, suffix: "" }
            ].map((kpi, i) => (
              <motion.div
                key={kpi.l}
                whileHover={{ backgroundColor: "#fff7ed" }}
                transition={{ duration: 0.2 }}
                className="bg-white p-5 md:p-6"
              >
                <div className="font-display text-3xl md:text-[40px] font-bold text-ink-0 tabular leading-none">
                  <CountUp
                    to={kpi.v}
                    duration={1.4 + i * 0.1}
                    decimals={kpi.decimals ?? 0}
                  />
                </div>
                <div className="text-sm text-ink-1 mt-3 font-medium">{kpi.l}</div>
                <div className="text-xs text-ink-2 mt-1">{kpi.h}</div>
              </motion.div>
            ))}
          </div>
        </Reveal>
      </div>

      <Reveal delay={1.05} className="mt-14 border-y border-ink-3/40 bg-white py-3">
        <Marquee items={TICKER} />
      </Reveal>
    </section>
  );
}
