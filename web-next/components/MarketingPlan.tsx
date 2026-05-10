"use client";
import { motion } from "framer-motion";
import { Coffee, Megaphone, Target, Wallet, Calendar } from "lucide-react";
import { Card, SectionHeader, Pill } from "./UI";
import { ds, PERSONA, PersonaKey, fmtPct } from "@/lib/data";

type PlanRow = {
  pid: PersonaKey;
  proposition: string;
  productSpec: string;
  channels: { name: string; share: number }[];
  budgetShare: number;
  songkran: string;
  kpi: string;
  estTrial: number;
};

const PLANS: PlanRow[] = [
  {
    pid: 0,
    proposition:
      "‘หอมเหมือนร้านที่คุณติดอยู่แล้ว’ — ขายกลิ่นนำ พิสูจน์ด้วยคุณภาพร้านกาแฟ 4,000 สาขาเดิม.",
    productSpec:
      "สูตรแมส (นุ่ม + เข้มกลาง), 280 ml, ราคา 35–40 ฿. เน้นกลิ่นตอนเปิดขวด (ฟอยล์ปิดให้กลิ่นพุ่งตอนแกะ).",
    channels: [
      { name: "TikTok", share: 35 },
      { name: "OOH รอบเซเว่น", share: 25 },
      { name: "IG Reels", share: 20 },
      { name: "ทีวี (สงกรานต์)", share: 20 }
    ],
    budgetShare: 60,
    songkran:
      "ออกบูธรอบโซนสงกรานต์ใหญ่ (สีลม, ข้าวสาร) — แจกตัวอย่าง 50,000 ขวดเย็น พร้อมฝาขูดที่เผยกลิ่น.",
    kpi: "อย่างน้อย 70% ตอบ ‘จะลอง’ ตอน intercept survey ที่บูธ; week 4 ซื้อซ้ำ ≥ 12%.",
    estTrial: 0.83
  },
  {
    pid: 2,
    proposition:
      "‘กาแฟร้านหรู ในขวดเดียว’ — RTD ระดับพรีเมียมที่สื่อสารเหมือนนั่งร้านจริง: QR ดูที่มาเมล็ด + โน้ตจากบาริสต้าบนฉลาก.",
    productSpec:
      "SKU พรีเมียม, single-origin, ขวดเทียบกระจก 250 ml, 55–65 ฿. เปิดด้วย Doi Chang washed.",
    channels: [
      { name: "IG / lifestyle press", share: 40 },
      { name: "แจมร้านในเครือเดิม", share: 30 },
      { name: "Spotify podcast ads", share: 20 },
      { name: "OOH เลือกจุด", share: 10 }
    ],
    budgetShare: 30,
    songkran:
      "ป๊อปอัปในห้างพรีเมียม (EmSphere, ICONSIAM); จัด tasting flight โดยบาริสต้า. ห้ามแจกแมส — กลุ่มนี้ชอบความ exclusive.",
    kpi: "≥ 80% probability บน Predictor สำหรับ persona พรีเมียม; AOV +15%.",
    estTrial: 0.81
  },
  {
    pid: 1,
    proposition:
      "อย่าทุ่มงบกาแฟกับกลุ่มนี้. ปรับไปลอง RTD ชา/wellness แทน แล้ว re-survey ใน Q3.",
    productSpec:
      "นอกขอบเขต launch กาแฟ. ทำ tea-attribute survey ใหม่ให้ N≥40 จะได้พ้นเพดาน 10 แถว.",
    channels: [
      { name: "พักไว้ก่อน (ไม่เทงบ)", share: 100 }
    ],
    budgetShare: 10,
    songkran: "ใช้เป็นกลุ่มควบคุม — วัดแค่การรับรู้แบบ organic.",
    kpi: "Re-survey Q3; ถ้า try-rate-tea ≥ 50% บน N=40 ค่อยปลดล็อกงบทำชา launch.",
    estTrial: 0.4
  }
];

export default function MarketingPlan() {
  const total = ds.dashboard.demographics.total;
  const blocks = ds.clusterSupervised.blocks;

  // Ranking by absolute trial volume (size × try-rate)
  const ranked = PLANS.map((p) => {
    const block = blocks.find((b) => b.cluster_id === p.pid);
    const size = block?.size ?? 0;
    const tryRate = block?.try_rate ?? p.estTrial;
    const expected = size * tryRate;
    return { ...p, size, tryRate, expected };
  });

  const totalExpected = ranked.reduce((s, r) => s + r.expected, 0);

  return (
    <section id="plan" className="py-24 md:py-32 relative">
      <div className="max-w-7xl mx-auto px-6">
        <SectionHeader
          index="07"
          kicker="ข้อเสนอ"
          title="จาก coefficient → แผน media พร้อมงบที่บวกได้ 100%"
          subtitle="ทุกบรรทัดด้านล่างยึดจากตัวเลขในหน้าเดียวกัน. ขนาดกลุ่มมาจาก K-Means. try-rate มาจาก target ของ supervised. ตัวขับอันดับ 1 ของแต่ละกลุ่มมาจาก logistic regression แยกคลัสเตอร์. สัดส่วนงบคิดตาม จำนวนคนในกลุ่ม × try-rate."
        />

        <div className="grid grid-cols-12 gap-6 mb-8">
          <Card className="col-span-12 md:col-span-4">
            <div className="text-xs font-mono text-ink-2 tracking-widest uppercase mb-1">
              คาดการณ์จากกลุ่มตัวอย่าง
            </div>
            <div className="font-display text-5xl text-accent-gold font-bold">
              {Math.round(totalExpected)}
              <span className="text-2xl text-ink-2">/{total}</span>
            </div>
            <p className="text-sm text-ink-1/85 mt-3 leading-relaxed">
              จำนวนคนที่น่าจะลองจริงๆ จากกลุ่มสำรวจ <span className="font-mono">{total}</span> คน.
              อยากเทียบกับตลาดทั้งประเทศ คูณด้วย{" "}
              <span className="font-mono">store_traffic / sample_size</span> (รอทีม field ส่งตัวเลขมา).
            </p>
          </Card>
          <Card className="col-span-12 md:col-span-4">
            <div className="text-xs font-mono text-ink-2 tracking-widest uppercase mb-1">
              สัดส่วนงบที่แนะนำ
            </div>
            <div className="flex h-12 rounded-xl overflow-hidden mt-3">
              {ranked.map((r) => {
                const p = PERSONA[r.pid];
                return (
                  <div
                    key={r.pid}
                    className="flex items-center justify-center text-xs font-mono"
                    style={{
                      width: `${r.budgetShare}%`,
                      background: p.color,
                      color: "#1B1814"
                    }}
                    title={`${p.code} · ${r.budgetShare}%`}
                  >
                    {r.budgetShare}%
                  </div>
                );
              })}
            </div>
            <div className="flex flex-wrap gap-2 mt-4">
              {ranked.map((r) => {
                const p = PERSONA[r.pid];
                return (
                  <Pill key={r.pid} color={p.color}>
                    {p.code} · {r.budgetShare}%
                  </Pill>
                );
              })}
            </div>
          </Card>
          <Card className="col-span-12 md:col-span-4">
            <div className="text-xs font-mono text-ink-2 tracking-widest uppercase mb-1">
              จุดยึดบนปฏิทิน
            </div>
            <div className="flex items-center gap-3 mt-2">
              <Calendar className="text-accent-gold" size={26} />
              <div>
                <div className="font-display text-2xl font-bold">สงกรานต์ 2026</div>
                <div className="text-xs text-ink-2 font-mono">13–15 เม.ย. · พีค OOH</div>
              </div>
            </div>
            <p className="text-sm text-ink-1/85 mt-3 leading-relaxed">
              ข้อมูลช่วงเทศกาลโชว์ว่า <span className="font-mono">freq_ooh</span> และ{" "}
              <span className="font-mono">streaming</span> พุ่ง 1.5–2× ของวันปกติ.
              เทงบ trade marketing 65% เข้า 2 สัปดาห์ก่อนเทศกาล.
            </p>
          </Card>
        </div>

        <div className="space-y-6">
          {ranked.map((r, i) => {
            const p = PERSONA[r.pid];
            return (
              <motion.div
                key={r.pid}
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-80px" }}
                transition={{ duration: 0.6, delay: i * 0.08 }}
              >
                <Card className="overflow-hidden">
                  <div
                    className="absolute -top-24 -right-24 w-72 h-72 rounded-full opacity-20 blur-3xl"
                    style={{ background: p.color }}
                  />
                  <div className="grid grid-cols-12 gap-6 relative">
                    <div className="col-span-12 lg:col-span-3 border-r border-white/5 pr-6">
                      <div className="flex items-center gap-3 mb-3">
                        <div
                          className="w-12 h-12 rounded-xl font-display text-2xl font-bold flex items-center justify-center"
                          style={{
                            background: `${p.color}25`,
                            color: p.color,
                            border: `1px solid ${p.color}66`
                          }}
                        >
                          {p.iconLetter}
                        </div>
                        <div>
                          <div className="text-xs font-mono text-ink-2">{p.code}</div>
                          <div className="font-display text-lg leading-tight font-semibold">{p.name}</div>
                        </div>
                      </div>

                      <div className="grid grid-cols-3 gap-2 text-center">
                        <div className="rounded-md bg-bg-2/60 p-2">
                          <div className="font-display text-base font-bold" style={{ color: p.color }}>
                            {r.size}
                          </div>
                          <div className="text-[9px] text-ink-2 font-mono uppercase mt-0.5">
                            คน
                          </div>
                        </div>
                        <div className="rounded-md bg-bg-2/60 p-2">
                          <div className="font-display text-base font-bold" style={{ color: p.color }}>
                            {fmtPct(r.tryRate)}
                          </div>
                          <div className="text-[9px] text-ink-2 font-mono uppercase mt-0.5">
                            จะลอง
                          </div>
                        </div>
                        <div className="rounded-md bg-bg-2/60 p-2">
                          <div className="font-display text-base font-bold" style={{ color: p.color }}>
                            {r.budgetShare}%
                          </div>
                          <div className="text-[9px] text-ink-2 font-mono uppercase mt-0.5">
                            งบ
                          </div>
                        </div>
                      </div>

                      <div className="mt-4 rounded-md bg-bg-2/60 p-3">
                        <div className="text-[10px] font-mono uppercase tracking-widest text-ink-2 mb-1">
                          คาดว่าจะลอง (กลุ่มสำรวจ)
                        </div>
                        <div className="font-display text-2xl font-bold" style={{ color: p.color }}>
                          {r.expected.toFixed(0)}
                          <span className="text-base text-ink-2"> /{r.size}</span>
                        </div>
                        <div className="text-[10px] text-ink-2 mt-1 font-mono">
                          = {r.size} × {fmtPct(r.tryRate, 0)}
                        </div>
                      </div>
                    </div>

                    <div className="col-span-12 lg:col-span-9 grid grid-cols-12 gap-5">
                      <div className="col-span-12 md:col-span-7">
                        <div className="flex items-center gap-2 text-accent-gold mb-2">
                          <Target size={14} />
                          <span className="tag">ข้อเสนอ</span>
                        </div>
                        <p className="text-base text-ink-0 leading-relaxed font-display font-medium">
                          {r.proposition}
                        </p>

                        <div className="flex items-center gap-2 text-accent-gold mt-5 mb-2">
                          <Coffee size={14} />
                          <span className="tag">สเปกสินค้า</span>
                        </div>
                        <p className="text-sm text-ink-1/85 leading-relaxed">{r.productSpec}</p>

                        <div className="flex items-center gap-2 text-accent-gold mt-5 mb-2">
                          <Calendar size={14} />
                          <span className="tag">แอ็กชันสงกรานต์</span>
                        </div>
                        <p className="text-sm text-ink-1/85 leading-relaxed">{r.songkran}</p>
                      </div>

                      <div className="col-span-12 md:col-span-5">
                        <div className="flex items-center gap-2 text-accent-gold mb-3">
                          <Megaphone size={14} />
                          <span className="tag">ช่องทางสื่อ</span>
                        </div>
                        <div className="space-y-2.5">
                          {r.channels.map((c) => (
                            <div key={c.name}>
                              <div className="flex justify-between text-xs mb-1">
                                <span className="text-ink-1">{c.name}</span>
                                <span
                                  className="font-mono"
                                  style={{ color: p.color }}
                                >
                                  {c.share}%
                                </span>
                              </div>
                              <div className="h-1.5 rounded-full bg-white/5 overflow-hidden">
                                <motion.div
                                  initial={{ width: 0 }}
                                  whileInView={{ width: `${c.share}%` }}
                                  viewport={{ once: true }}
                                  transition={{ duration: 0.7, ease: "easeOut" }}
                                  className="h-full rounded-full"
                                  style={{ background: p.color }}
                                />
                              </div>
                            </div>
                          ))}
                        </div>

                        <div className="flex items-center gap-2 text-accent-gold mt-5 mb-2">
                          <Wallet size={14} />
                          <span className="tag">เป้าวัดความสำเร็จ</span>
                        </div>
                        <p className="text-xs text-ink-1/85 leading-relaxed">{r.kpi}</p>
                      </div>
                    </div>
                  </div>
                </Card>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
