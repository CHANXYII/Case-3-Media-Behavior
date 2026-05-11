"use client";
import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";
import { WordReveal, CountUp } from "./Motion";

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
          className="font-display text-[40px] md:text-7xl lg:text-[92px] leading-[1.15] tracking-[-0.025em] font-bold text-white py-2"
        >
          <WordReveal text="เราไม่ได้ขายกาแฟ." />
        </motion.h2>
        <motion.h2
          style={{ x: xRight, opacity }}
          className="font-display text-[40px] md:text-7xl lg:text-[92px] leading-[1.15] tracking-[-0.025em] font-bold text-white mt-3 py-2"
        >
          <WordReveal text="เราขาย" delay={0.3} />{" "}
          <span className="text-accent-gold inline-block">
            <WordReveal text="การตัดสินใจ" delay={0.5} />
          </span>{" "}
          <WordReveal text="ที่ถูกคน." delay={0.75} />
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
              { v: 60, l: "งบลงสาย Mainstream" },
              { v: 30, l: "งบลงสายพรีเมียม" },
              { v: 10, l: "งบสำรอง · ชา/wellness" }
            ].map((s, i) => (
              <motion.div
                key={s.l}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-10% 0px" }}
                transition={{ duration: 0.5, delay: 0.4 + i * 0.1 }}
                className="bg-[#1c1917] p-4"
              >
                <div className="font-display text-2xl md:text-3xl font-bold text-accent-gold tabular leading-none">
                  <CountUp to={s.v} suffix="%" duration={1.6} />
                </div>
                <div className="text-[11px] text-white/60 mt-2 leading-snug">{s.l}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
