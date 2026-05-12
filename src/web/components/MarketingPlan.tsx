"use client";
import { motion } from "framer-motion";
import { Coffee, Megaphone, Target, Wallet, Calendar } from "lucide-react";
import { Card, SectionHeader, Pill } from "./UI";
import { CountUp } from "./Motion";
import { ds, PERSONA, PersonaKey, TARGET_CHOICES, fmtPct } from "@/lib/data";

type PlanRow = {
  pid: PersonaKey;
  proposition: string;
  productSpec: string;
  channels: { name: string; share: number }[];
  budgetShare: number;
  songkran: string;
  kpi: string;
};

const PLANS: PlanRow[] = [
  {
    pid: 0,
    proposition: "‘หอมเหมือนร้านที่คุณติดอยู่แล้ว’ — ขายกลิ่นนำ พิสูจน์ด้วยคุณภาพร้านกาแฟ 4,000 สาขา.",
    productSpec: "สูตรแมส (นุ่ม + เข้มกลาง), 280 ml, 35–40 ฿. เน้นกลิ่นตอนเปิดขวด (ฟอยล์ปิดให้กลิ่นพุ่งตอนแกะ).",
    channels: [
      { name: "TikTok", share: 35 },
      { name: "OOH รอบเซเว่น", share: 25 },
      { name: "IG Reels", share: 20 },
      { name: "ทีวี (สงกรานต์)", share: 20 }
    ],
    budgetShare: 60,
    songkran: "ออกบูธรอบโซนสงกรานต์ใหญ่ (สีลม, ข้าวสาร) — แจกตัวอย่าง 50,000 ขวดเย็น พร้อมฝาขูดที่เผยกลิ่น.",
    kpi: "อย่างน้อย 70% ตอบ ‘จะลอง’ ตอน intercept survey ที่บูธ; week 4 ซื้อซ้ำ ≥ 12%."
  },
  {
    pid: 2,
    proposition: "‘กาแฟร้านหรู ในขวดเดียว’ — RTD ระดับพรีเมียม สื่อสารเหมือนนั่งร้านจริง: QR ดูที่มาเมล็ด + โน้ตจากบาริสต้า.",
    productSpec: "SKU พรีเมียม, single-origin, ขวดเทียบกระจก 250 ml, 55–65 ฿. เปิดด้วย Doi Chang washed.",
    channels: [
      { name: "IG / lifestyle press", share: 40 },
      { name: "แจมร้านในเครือเดิม", share: 30 },
      { name: "Spotify podcast ads", share: 20 },
      { name: "OOH เลือกจุด", share: 10 }
    ],
    budgetShare: 30,
    songkran: "ป๊อปอัปในห้างพรีเมียม (EmSphere, ICONSIAM); จัด tasting flight โดยบาริสต้า. ห้ามแจกแมส.",
    kpi: "≥ 80% probability บน Predictor สำหรับ persona พรีเมียม; AOV +15%."
  },
  {
    pid: 1,
    proposition: "อย่าทุ่มงบกาแฟกับกลุ่มนี้. ปรับไปลอง RTD ชา/wellness แทน แล้ว re-survey ใน Q3.",
    productSpec: "นอกขอบเขต launch กาแฟ. ทำ tea-attribute survey ใหม่ให้ N≥40 จะได้พ้นเพดาน 10 แถว.",
    channels: [{ name: "พักไว้ก่อน (ไม่เทงบ)", share: 100 }],
    budgetShare: 10,
    songkran: "ใช้เป็นกลุ่มควบคุม — วัดแค่การรับรู้แบบ organic.",
    kpi: "Re-survey Q3; ถ้าอัตรา ‘ลองแน่นอน’ ของชา ≥ 50% บน N=40 ค่อยปลดล็อกงบทำชา launch."
  }
];

export default function MarketingPlan() {
  const total = ds.dashboard.demographics.total;
  const blocks = ds.clusterSupervised.blocks;

  const ranked = PLANS.map((p) => {
    const block = blocks.find((b) => b.cluster_id === p.pid)!;
    const size = block.size;
    const tryRate = block.try_rate;
    const expected = size * tryRate;
    return { ...p, block, size, tryRate, expected };
  });

  const totalExpected = ranked.reduce((s, r) => s + r.expected, 0);

  return (
    <section id="plan" className="py-20 md:py-28">
      <div className="max-w-6xl mx-auto px-6">
        <SectionHeader
          index="07"
          kicker="ข้อเสนอ"
          title="จาก coefficient → แผน media พร้อมงบที่บวกได้ 100%"
          subtitle="ทุกบรรทัดด้านล่างยึดจากตัวเลขในหน้าเดียวกัน. ขนาดกลุ่มมาจาก K-Means. target supervised แยกเป็น 3 คำตอบ. ตัวขับอันดับ 1 ของแต่ละกลุ่มมาจาก logistic regression แยกคลัสเตอร์. สัดส่วนงบ = จำนวนคน × definite-try rate."
        />

        <div className="grid grid-cols-12 gap-5 mb-6">
          <Card className="col-span-12 md:col-span-4">
            <div className="tag mb-2">คาดการณ์จากกลุ่มตัวอย่าง</div>
            <div className="text-4xl font-bold text-ink-0 tabular">
              <CountUp to={Math.round(totalExpected)} duration={1.6} />
              <span className="text-xl text-ink-3">/{total}</span>
            </div>
            <p className="text-sm text-ink-2 mt-3 leading-relaxed">
              จำนวนคนที่น่าจะ <span className="text-accent-gold font-medium">ลองแน่นอน</span> จากกลุ่มสำรวจ <span className="font-mono text-ink-1">{total}</span> คน. คูณด้วย <span className="font-mono text-ink-1">store_traffic / sample_size</span> เพื่อ scale ตลาด.
            </p>
          </Card>
          <Card className="col-span-12 md:col-span-4">
            <div className="tag mb-2">สัดส่วนงบที่แนะนำ</div>
            <div className="flex h-10 rounded-md overflow-hidden mt-3 border border-ink-3/40">
              {ranked.map((r, i) => {
                const p = PERSONA[r.pid];
                return (
                  <motion.div
                    key={r.pid}
                    initial={{ width: 0 }}
                    whileInView={{ width: `${r.budgetShare}%` }}
                    viewport={{ once: true, margin: "-10% 0px" }}
                    transition={{ duration: 0.9, delay: 0.2 + i * 0.12, ease: [0.2, 0.8, 0.2, 1] }}
                    className="flex items-center justify-center text-xs font-mono font-medium text-white"
                    style={{ background: p.color }}
                    title={`${p.code} · ${r.budgetShare}%`}
                  >
                    {r.budgetShare}%
                  </motion.div>
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
            <div className="tag mb-2">จุดยึดบนปฏิทิน</div>
            <div className="flex items-center gap-3 mt-2">
              <Calendar className="text-accent-gold" size={22} />
              <div>
                <div className="text-xl font-bold text-ink-0">สงกรานต์ 2026</div>
                <div className="text-xs text-ink-2 font-mono">13–15 เม.ย. · พีค OOH</div>
              </div>
            </div>
            <p className="text-sm text-ink-2 mt-3 leading-relaxed">
              ช่วงเทศกาล <span className="font-mono text-ink-1">freq_ooh</span> + <span className="font-mono text-ink-1">streaming</span> พุ่ง 1.5–2× ของวันปกติ. เทงบ trade marketing 65% เข้า 2 สัปดาห์ก่อนเทศกาล.
            </p>
          </Card>
        </div>

        <div className="space-y-5">
          {ranked.map((r, i) => {
            const p = PERSONA[r.pid];
            return (
              <motion.div
                key={r.pid}
                initial={{ opacity: 0, y: 14 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-80px" }}
                transition={{ duration: 0.4, delay: i * 0.06 }}
              >
                <Card className="hover-lift overflow-hidden">
                  <div
                    className="absolute top-0 left-0 right-0 h-[3px] rounded-t-xl"
                    style={{ background: p.color }}
                  />
                  <div className="grid grid-cols-12 gap-6">
                    <div className="col-span-12 lg:col-span-3 lg:border-r border-ink-3/40 lg:pr-6">
                      <div className="flex items-center gap-3 mb-4">
                        <div
                          className="w-10 h-10 rounded-md text-lg font-bold flex items-center justify-center"
                          style={{ background: `${p.color}14`, color: p.color, border: `1px solid ${p.color}40` }}
                        >
                          {p.iconLetter}
                        </div>
                        <div>
                          <div className="text-[11px] font-mono text-ink-2">{p.code}</div>
                          <div className="text-base font-semibold leading-snug text-ink-0">{p.name}</div>
                        </div>
                      </div>

                      <div className="grid grid-cols-3 gap-2 text-center">
                        <div className="surface-muted p-2">
                          <div className="text-base font-semibold tabular" style={{ color: p.color }}>{r.size}</div>
                          <div className="text-[9px] text-ink-2 font-mono uppercase mt-0.5">คน</div>
                        </div>
                        <div className="surface-muted p-2">
                          <div className="text-base font-semibold tabular" style={{ color: TARGET_CHOICES[2].color }}>{fmtPct(r.tryRate)}</div>
                          <div className="text-[9px] text-ink-2 font-mono uppercase mt-0.5">ลองแน่</div>
                        </div>
                        <div className="surface-muted p-2">
                          <div className="text-base font-semibold tabular" style={{ color: p.color }}>{r.budgetShare}%</div>
                          <div className="text-[9px] text-ink-2 font-mono uppercase mt-0.5">งบ</div>
                        </div>
                      </div>

                      <div className="mt-4 surface-muted p-3">
                        <div className="text-[10px] font-mono uppercase tracking-widest text-ink-2 mb-1">คาดว่าจะลองแน่นอน</div>
                        <div className="text-xl font-bold tabular" style={{ color: p.color }}>
                          {r.expected.toFixed(0)}
                          <span className="text-sm text-ink-3"> /{r.size}</span>
                        </div>
                        <div className="text-[10px] text-ink-2 mt-1 font-mono">= {r.size} × {fmtPct(r.tryRate, 0)}</div>
                        <div className="mt-3 grid grid-cols-3 gap-1 text-center">
                          {TARGET_CHOICES.map((ch) => (
                            <div key={ch.key}>
                              <div className="text-sm font-semibold tabular" style={{ color: ch.color }}>{fmtPct(r.block.choice_rates[ch.key])}</div>
                              <div className="text-[9px] text-ink-2 font-mono uppercase">{ch.shortLabel}</div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>

                    <div className="col-span-12 lg:col-span-9 grid grid-cols-12 gap-5">
                      <div className="col-span-12 md:col-span-7">
                        <div className="flex items-center gap-2 text-ink-2 mb-2">
                          <Target size={13} />
                          <span className="tag">ข้อเสนอ</span>
                        </div>
                        <p className="text-[15px] text-ink-0 leading-relaxed font-medium">{r.proposition}</p>

                        <div className="flex items-center gap-2 text-ink-2 mt-5 mb-2">
                          <Coffee size={13} />
                          <span className="tag">สเปกสินค้า</span>
                        </div>
                        <p className="text-[13px] text-ink-2 leading-relaxed">{r.productSpec}</p>

                        <div className="flex items-center gap-2 text-ink-2 mt-5 mb-2">
                          <Calendar size={13} />
                          <span className="tag">แอ็กชันสงกรานต์</span>
                        </div>
                        <p className="text-[13px] text-ink-2 leading-relaxed">{r.songkran}</p>
                      </div>

                      <div className="col-span-12 md:col-span-5">
                        <div className="flex items-center gap-2 text-ink-2 mb-3">
                          <Megaphone size={13} />
                          <span className="tag">ช่องทางสื่อ</span>
                        </div>
                        <div className="space-y-2.5">
                          {r.channels.map((c) => (
                            <div key={c.name}>
                              <div className="flex justify-between text-xs mb-1">
                                <span className="text-ink-1">{c.name}</span>
                                <span className="font-mono tabular" style={{ color: p.color }}>{c.share}%</span>
                              </div>
                              <div className="h-1.5 rounded-full bg-bg-2 overflow-hidden">
                                <motion.div
                                  initial={{ width: 0 }}
                                  whileInView={{ width: `${c.share}%` }}
                                  viewport={{ once: true }}
                                  transition={{ duration: 0.6, ease: "easeOut" }}
                                  className="h-full rounded-full"
                                  style={{ background: p.color }}
                                />
                              </div>
                            </div>
                          ))}
                        </div>

                        <div className="flex items-center gap-2 text-ink-2 mt-5 mb-2">
                          <Wallet size={13} />
                          <span className="tag">เป้าวัดความสำเร็จ</span>
                        </div>
                        <p className="text-xs text-ink-2 leading-relaxed">{r.kpi}</p>
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
