"use client";
import { motion } from "framer-motion";
import { ArrowRight, Coffee } from "lucide-react";

export default function Hero() {
  return (
    <section id="hero" className="relative pt-32 md:pt-40 pb-24 overflow-hidden">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid grid-cols-12 gap-8 items-end">
          <div className="col-span-12 lg:col-span-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="flex items-center gap-3 mb-6"
            >
              <span className="tag">เคส 03 · พฤติกรรมสื่อ</span>
              <span className="h-px flex-1 bg-accent-gold/30 max-w-[180px]" />
              <span className="text-xs font-mono text-ink-2">181 คน · 120 ฟีเจอร์</span>
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.05 }}
              className="font-display text-3xl md:text-5xl lg:text-6xl leading-[1.1] tracking-tight font-bold"
            >
              จากร้านกาแฟ 4,000 สาขา{" "}
              <br />
              <span className="shimmer-text">สู่ขวดบนชั้นในเซเว่น</span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.18 }}
              className="mt-8 text-lg md:text-xl text-ink-1/85 max-w-2xl leading-relaxed"
            >
              แบรนด์กำลังจะขยายจากร้านกาแฟ 4,000+ สาขา ออกมาเป็นกาแฟพร้อมดื่ม (RTD)
              ในร้านสะดวกซื้อ คำถามคือ <span className="text-accent-gold">ควรคุยกับใคร</span> ·
              พูดเรื่องอะไร · แล้ว <span className="text-accent-gold">เทงบไปทางไหน</span> ถึงจะคุ้ม.
              งั้นเราเก็บแบบสอบถาม 181 คน เคลียร์ให้เหลือ 120 คอลัมน์ใช้งานได้จริง
              แบ่งเป็น 3 กลุ่มลูกค้า แล้วเทรนโมเดลทำนายแยกทีละกลุ่ม — ที่เหลืออ่านด้านล่างได้เลย.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="mt-10 flex flex-wrap gap-3"
            >
              <a href="#raw" className="btn-primary rounded-full px-6 py-3 inline-flex items-center gap-2">
                อ่านจากต้น <ArrowRight size={16} />
              </a>
              <a
                href="#predict"
                className="rounded-full px-6 py-3 inline-flex items-center gap-2 border border-white/15 text-ink-1 hover:border-accent-gold/60 hover:text-accent-gold transition"
              >
                ลองทำนายเอง
              </a>
            </motion.div>
          </div>

          <div className="col-span-12 lg:col-span-4 hidden lg:block">
            <div className="relative h-[420px]">
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 1.2 }}
                className="absolute inset-0 rounded-full bg-gradient-radial from-accent-gold/30 via-accent-copper/10 to-transparent blur-2xl"
                style={{
                  background:
                    "radial-gradient(circle at 50% 50%, rgba(224,164,88,0.35), rgba(199,123,60,0.08) 40%, transparent 70%)"
                }}
              />
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 60, repeat: Infinity, ease: "linear" }}
                className="absolute inset-6 rounded-full border border-accent-gold/30"
                style={{ borderStyle: "dashed" }}
              />
              <motion.div
                animate={{ rotate: -360 }}
                transition={{ duration: 90, repeat: Infinity, ease: "linear" }}
                className="absolute inset-16 rounded-full border border-accent-gold/15"
              />
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <Coffee size={56} className="text-accent-gold mx-auto mb-3" strokeWidth={1.4} />
                  <div className="font-display text-3xl font-bold">79%</div>
                  <div className="text-xs font-mono tracking-widest text-ink-2 uppercase mt-1">
                    อยากลอง RTD ตัวใหม่
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.5 }}
          className="mt-20 grid grid-cols-2 md:grid-cols-4 gap-6"
        >
          {[
            { v: "181", l: "คนที่ตอบแบบสอบถาม", h: "หลังตัดแถวที่ข้อมูลว่างทิ้งแล้ว" },
            { v: "120", l: "ฟีเจอร์ที่ใช้งานได้", h: "จากคำถามภาษาไทย 76 ข้อ" },
            { v: "3", l: "กลุ่มลูกค้า (K-Means)", h: "Silhouette = 0.30" },
            { v: "0.89", l: "F1 สูงสุด (Random Forest)", h: "5-fold stratified CV" }
          ].map((kpi) => (
            <div key={kpi.l} className="border-l border-accent-gold/30 pl-4">
              <div className="font-display text-3xl md:text-4xl text-accent-gold">{kpi.v}</div>
              <div className="text-sm text-ink-1 mt-1">{kpi.l}</div>
              <div className="text-xs text-ink-2 mt-1">{kpi.h}</div>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
