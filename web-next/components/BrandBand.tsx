"use client";
import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";

export default function BrandBand() {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"]
  });
  const xLeft = useTransform(scrollYProgress, [0, 1], ["-8%", "8%"]);
  const xRight = useTransform(scrollYProgress, [0, 1], ["8%", "-8%"]);
  const opacity = useTransform(scrollYProgress, [0, 0.25, 0.75, 1], [0.4, 1, 1, 0.4]);

  return (
    <section ref={ref} className="brand-band py-24 md:py-32">
      <div className="max-w-6xl mx-auto px-6 relative">
        <div className="flex items-center gap-3 mb-8">
          <span className="w-8 h-px bg-accent-gold" />
          <span className="font-mono text-[11px] uppercase tracking-[0.18em] text-accent-gold">
            Manifesto · จุดยืนของแคมเปญ
          </span>
        </div>

        <motion.h2
          style={{ x: xLeft, opacity }}
          className="font-display text-[40px] md:text-7xl lg:text-[92px] leading-[0.95] tracking-[-0.025em] font-bold text-white"
        >
          เราไม่ได้ขายกาแฟ.
        </motion.h2>
        <motion.h2
          style={{ x: xRight, opacity }}
          className="font-display text-[40px] md:text-7xl lg:text-[92px] leading-[0.95] tracking-[-0.025em] font-bold text-white mt-2"
        >
          เราขาย <span className="text-accent-gold">การตัดสินใจ</span> ที่ถูกคน.
        </motion.h2>

        <div className="mt-12 grid grid-cols-12 gap-6 items-end">
          <div className="col-span-12 md:col-span-7">
            <p className="text-white/70 text-base md:text-lg leading-relaxed max-w-xl">
              ทุกบาทของงบสื่อ ควรมีตัวเลขมาหนุน. หน้านี้คือสิ่งที่ data จริง 181 คนบอกเรา —
              ใครจะลอง, ทำไม, และควรคุยด้วยช่องไหน. <span className="text-white">ไม่ใช่ความรู้สึก. คือสมการ.</span>
            </p>
          </div>
          <div className="col-span-12 md:col-span-5 grid grid-cols-3 gap-px bg-white/10 rounded-xl overflow-hidden">
            {[
              { v: "60%", l: "งบลงสาย Mainstream" },
              { v: "30%", l: "งบลงสายพรีเมียม" },
              { v: "10%", l: "งบสำรอง · ชา/wellness" }
            ].map((s) => (
              <div key={s.l} className="bg-[#1c1917] p-4">
                <div className="font-display text-2xl md:text-3xl font-bold text-accent-gold tabular leading-none">
                  {s.v}
                </div>
                <div className="text-[11px] text-white/60 mt-2 leading-snug">{s.l}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
