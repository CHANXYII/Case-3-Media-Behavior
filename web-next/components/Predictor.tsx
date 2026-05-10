"use client";
import { useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles } from "lucide-react";
import {
  RadialBarChart,
  RadialBar,
  PolarAngleAxis,
  ResponsiveContainer
} from "recharts";
import { Card, SectionHeader, Pill } from "./UI";
import { ds, PERSONA, PersonaKey } from "@/lib/data";

function sigmoid(x: number) {
  return 1 / (1 + Math.exp(-x));
}

const FEATURE_HELP: Record<string, string> = {
  coffee_value:
    "‘ราคาเทียบกับคุณภาพ ต้องคุ้ม’ มีผลตอนเลือกแค่ไหน. 1 = ไม่สน, 5 = ตัดสินใจจากข้อนี้เลย.",
  coffee_aroma: "‘กลิ่นต้องโดน — ต้องดมตอนเปิดขวด’.",
  coffee_convenience: "‘ขอแบบหยิบเดินดื่ม ไม่ต้องชง’.",
  coffee_nutrition: "‘น้ำตาลน้อย/มีฟังก์ชันเสริม สำคัญ’.",
  coffee_smooth: "‘นุ่ม ไม่ขม ดื่มเย็นได้สบาย’.",
  coffee_brand_trust: "‘ขอแบรนด์ที่รู้จักและไว้ใจอยู่แล้ว’.",
  coffee_packaging: "‘ดีไซน์ขวด/กระป๋อง มีผลตอนเดินผ่านชั้น’.",
  coffee_fresh_taste: "‘ต้องเหมือนกาแฟสดเพิ่งชง’.",
  coffee_intensity: "‘ขอเข้มจัด คั่วเข้ม’.",
  coffee_premium: "‘รู้สึกพรีเมียม จ่ายเพิ่มได้’."
};

export default function Predictor() {
  const data = ds.clusterSupervised;
  const featureOrder = data.features.map((f) => f.name);
  const blocks = data.blocks.filter((b) => b.cluster_id !== null && b.model.fitted);

  const [activeId, setActiveId] = useState<PersonaKey>(0);
  const [values, setValues] = useState<Record<string, number>>(() => {
    const obj: Record<string, number> = {};
    featureOrder.forEach((f) => (obj[f] = 4));
    return obj;
  });

  const block = blocks.find((b) => b.cluster_id === activeId) || blocks[0];
  const persona = PERSONA[block.cluster_id as PersonaKey];

  const { prob, logit, contributions } = useMemo(() => {
    const m = block.model;
    if (!m.fitted) return { prob: 0, logit: 0, contributions: [] };
    let logit = m.intercept ?? 0;
    const contribs: { feature: string; label: string; z: number; coef: number; contrib: number }[] = [];
    featureOrder.forEach((f, i) => {
      const x = values[f];
      const mean = (m.scaler_mean ?? [])[i] ?? 0;
      const scale = (m.scaler_scale ?? [])[i] || 1;
      const z = (x - mean) / scale;
      const coefRow = (m.coefficients ?? []).find((c: any) => c.feature === f);
      const coef = coefRow ? coefRow.coefficient : 0;
      const contrib = z * coef;
      logit += contrib;
      contribs.push({
        feature: f,
        label: coefRow ? coefRow.label : f,
        z,
        coef,
        contrib
      });
    });
    contribs.sort((a, b) => Math.abs(b.contrib) - Math.abs(a.contrib));
    return { prob: sigmoid(logit), logit, contributions: contribs };
  }, [block, values, featureOrder]);

  const probPct = prob * 100;
  const probColor =
    prob > 0.7 ? "#5BB89A" : prob > 0.45 ? persona.color : "#D85A5A";
  const radial = [{ name: "p", value: probPct, fill: probColor }];

  return (
    <section id="predict" className="py-24 md:py-32 relative">
      <div className="max-w-7xl mx-auto px-6">
        <SectionHeader
          index="06"
          kicker="โมเดลใช้งานจริง"
          title="ลองให้คะแนนผู้ตอบสด ๆ ดูเลย"
          subtitle="เลือก persona ที่อยากลอง แล้วลากสไลเดอร์ข้างล่าง. เราจะคำนวณ z-score เทียบกับการกระจายตัวที่เทรนของกลุ่มนั้น คูณด้วย log-odds เฉพาะคลัสเตอร์ บวกกับ intercept แล้วยัดเข้า sigmoid — ออกมาเป็นเปอร์เซ็นต์ ‘คนคนนี้จะลอง RTD ใหม่ไหม’ พร้อมบอกว่าฟีเจอร์ไหนดันคะแนนขึ้น/ลง."
        />

        <div className="grid grid-cols-12 gap-3 mb-8">
          {blocks.map((b) => {
            const p = PERSONA[b.cluster_id as PersonaKey];
            const isActive = b.cluster_id === activeId;
            return (
              <button
                key={b.cluster_id}
                onClick={() => setActiveId(b.cluster_id as PersonaKey)}
                className={`col-span-12 md:col-span-4 text-left rounded-2xl p-4 border transition-all ${
                  isActive ? "border-accent-gold/60" : "border-white/8 hover:border-white/20"
                }`}
                style={
                  isActive
                    ? {
                        background: `linear-gradient(135deg, ${p.color}18, ${p.color}05)`
                      }
                    : { background: "rgba(255,255,255,0.02)" }
                }
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-xs font-mono text-ink-2">{p.code}</div>
                    <div className="font-display text-base leading-tight font-semibold">{p.name}</div>
                  </div>
                  <div className="font-mono text-xs text-ink-2 text-right">
                    n={b.labelled_size}
                    <br />
                    base ≈ {(b.try_rate! * 100).toFixed(0)}%
                  </div>
                </div>
              </button>
            );
          })}
        </div>

        <div className="grid grid-cols-12 gap-6">
          <Card className="col-span-12 lg:col-span-7">
            <div className="text-xs font-mono text-ink-2 tracking-widest uppercase mb-3">
              ลากสไลเดอร์ทั้ง 10 ข้อ
            </div>
            <div className="space-y-4">
              {featureOrder.map((f) => {
                const label = data.features.find((x) => x.name === f)?.label ?? f;
                const v = values[f];
                return (
                  <div key={f} className="grid grid-cols-12 gap-3 items-center">
                    <div className="col-span-12 md:col-span-4">
                      <div className="text-sm text-ink-1 font-medium">{label}</div>
                      <div className="text-[11px] text-ink-2 leading-snug">{FEATURE_HELP[f]}</div>
                    </div>
                    <div className="col-span-9 md:col-span-7">
                      <input
                        type="range"
                        min={1}
                        max={5}
                        step={1}
                        value={v}
                        onChange={(e) =>
                          setValues((prev) => ({ ...prev, [f]: Number(e.target.value) }))
                        }
                      />
                      <div className="flex justify-between text-[10px] text-ink-2 font-mono mt-1">
                        <span>1 · ไม่สำคัญ</span>
                        <span>2</span>
                        <span>3</span>
                        <span>4</span>
                        <span>5 · สำคัญสุด</span>
                      </div>
                    </div>
                    <div
                      className="col-span-3 md:col-span-1 font-mono text-base text-right"
                      style={{ color: persona.color }}
                    >
                      {v}/5
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>

          <Card className="col-span-12 lg:col-span-5" glow>
            <div className="flex items-center justify-between mb-2">
              <Pill color={persona.color}>
                <Sparkles size={11} /> สด · {persona.code}
              </Pill>
              <div className="font-mono text-xs text-ink-2">
                base = {(block.try_rate! * 100).toFixed(0)}%
              </div>
            </div>

            <div className="relative h-[260px]">
              <ResponsiveContainer>
                <RadialBarChart
                  innerRadius="72%"
                  outerRadius="100%"
                  data={radial}
                  startAngle={210}
                  endAngle={-30}
                >
                  <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
                  <RadialBar background={{ fill: "#252019" }} dataKey="value" cornerRadius={20} />
                </RadialBarChart>
              </ResponsiveContainer>
              <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                <AnimatePresence mode="wait">
                  <motion.div
                    key={Math.round(probPct)}
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -6 }}
                    transition={{ duration: 0.18 }}
                    className="font-display text-6xl font-semibold"
                    style={{ color: probColor }}
                  >
                    {probPct.toFixed(0)}%
                  </motion.div>
                </AnimatePresence>
                <div className="text-xs font-mono text-ink-2 tracking-widest uppercase mt-1">
                  โอกาสจะลอง RTD ใหม่
                </div>
              </div>
            </div>

            <div className="mt-4 text-xs font-mono text-ink-2 grid grid-cols-2 gap-2">
              <div>
                <div className="uppercase tracking-widest">logit</div>
                <div className="text-ink-1 text-base">{logit.toFixed(2)}</div>
              </div>
              <div>
                <div className="uppercase tracking-widest">intercept</div>
                <div className="text-ink-1 text-base">
                  {block.model.intercept!.toFixed(2)}
                </div>
              </div>
            </div>

            <div className="mt-5">
              <div className="text-xs font-mono text-ink-2 tracking-widest uppercase mb-2">
                ทำไมได้คะแนนเท่านี้ · ผลรวมต่อ log-odds
              </div>
              <div className="space-y-1.5">
                {contributions.slice(0, 6).map((c) => {
                  const w = Math.min(100, (Math.abs(c.contrib) / 1.5) * 100);
                  const positive = c.contrib >= 0;
                  return (
                    <div
                      key={c.feature}
                      className="flex items-center gap-2 text-[12px]"
                    >
                      <div className="w-28 truncate text-ink-1">{c.label}</div>
                      <div className="flex-1 relative h-2 bg-white/5 rounded-full overflow-hidden flex">
                        <div className="w-1/2 flex justify-end pr-px">
                          {!positive && (
                            <div
                              className="h-full rounded-full"
                              style={{
                                width: `${w}%`,
                                background: "#D85A5A"
                              }}
                            />
                          )}
                        </div>
                        <div className="w-px h-full bg-white/10" />
                        <div className="w-1/2">
                          {positive && (
                            <div
                              className="h-full rounded-full"
                              style={{
                                width: `${w}%`,
                                background: persona.color
                              }}
                            />
                          )}
                        </div>
                      </div>
                      <div
                        className="w-12 text-right font-mono"
                        style={{ color: positive ? persona.color : "#D85A5A" }}
                      >
                        {positive ? "+" : ""}
                        {c.contrib.toFixed(2)}
                      </div>
                    </div>
                  );
                })}
              </div>
              <p className="text-[11px] text-ink-2 mt-3 leading-relaxed">
                แท่งคือ ‘แต่ละฟีเจอร์ผลักคะแนนไปกี่ log-odds’. เอามาบวกกับ intercept แล้วยัดเข้า{" "}
                <span className="font-mono">σ(x)</span> ก็ได้เปอร์เซ็นต์ด้านบน. ลากสไลเดอร์เลย — ตัวเลขขยับตามทันที.
              </p>
            </div>
          </Card>
        </div>
      </div>
    </section>
  );
}
