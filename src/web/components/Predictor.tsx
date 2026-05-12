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
import { ds, PERSONA, PersonaKey, TARGET_CHOICES, TargetChoiceKey, fmtPct } from "@/lib/data";

function softmax(logits: number[]) {
  const max = Math.max(...logits);
  const exps = logits.map((v) => Math.exp(v - max));
  const sum = exps.reduce((s, v) => s + v, 0);
  return exps.map((v) => v / sum);
}

const FEATURE_HELP: Record<string, string> = {
  coffee_value: "ราคาเทียบกับคุณภาพต้องคุ้ม — 1=ไม่สน, 5=สำคัญมาก",
  coffee_aroma: "กลิ่นต้องหอม ดมแล้วรู้สึกอยากดื่ม",
  coffee_nutrition: "น้ำตาลน้อย หรือมีส่วนผสมเพื่อสุขภาพ",
  coffee_convenience: "หยิบง่าย ดื่มได้เลย ไม่ต้องชง",
  coffee_caffeine: "คาเฟอีนพอให้ตื่นตัว ช่วยให้ทำงานได้",
  coffee_smooth: "รสชาตินุ่ม ไม่ขม ดื่มง่าย"
};

export default function Predictor() {
  const data = ds.clusterSupervised;
  const blocks = data.blocks.filter((b) => b.cluster_id !== null && b.model.fitted);
  const featureOrder = data.features.map((f) => f.name);
  const featureLabels = Object.fromEntries(data.features.map((f) => [f.name, f.label])) as Record<string, string>;

  const [activeId, setActiveId] = useState<PersonaKey>(blocks[0]!.cluster_id as PersonaKey);
  const [values, setValues] = useState<Record<string, number>>(() => {
    const obj: Record<string, number> = {};
    featureOrder.forEach((f) => (obj[f] = 4));
    return obj;
  });

  const block = blocks.find((b) => b.cluster_id === activeId)!;
  const persona = PERSONA[block.cluster_id as PersonaKey];

  const { probs, predicted, logit, contributions } = useMemo(() => {
    const m = block.model;
    const classes = m.classes!.map(String) as TargetChoiceKey[];
    const logits = classes.map((cls) => m.intercepts![cls]);
    const tryClass = "2" as TargetChoiceKey;
    const tryIndex = classes.indexOf(tryClass);
    const contribs: { feature: string; label: string; z: number; coef: number; contrib: number }[] = [];
    const tryCoefficients = m.coefficients_by_class![tryClass];
    featureOrder.forEach((f, i) => {
      const x = values[f];
      const mean = m.scaler_mean![i];
      const scale = m.scaler_scale![i] || 1;
      const z = (x - mean) / scale;
      classes.forEach((cls, clsIndex) => {
        const coefRow = m.coefficients_by_class![cls].find((c: any) => c.feature === f);
        const coef = coefRow ? coefRow.coefficient : 0;
        logits[clsIndex] += z * coef;
      });
      const coefRow = tryCoefficients.find((c: any) => c.feature === f);
      const coef = coefRow ? coefRow.coefficient : 0;
      contribs.push({ feature: f, label: coefRow ? coefRow.label : f, z, coef, contrib: z * coef });
    });
    contribs.sort((a, b) => Math.abs(b.contrib) - Math.abs(a.contrib));
    const probabilityList = softmax(logits);
    const probs = { "0": 0, "1": 0, "2": 0 } as Record<TargetChoiceKey, number>;
    classes.forEach((cls, i) => {
      probs[cls] = probabilityList[i] ?? 0;
    });
    const predicted = TARGET_CHOICES.reduce((best, choice) =>
      probs[choice.key] > probs[best.key] ? choice : best
    );
    return { probs, predicted, logit: logits[tryIndex], contributions: contribs };
  }, [block, values, featureOrder]);

  const tryProb = probs["2"];
  const probPct = tryProb * 100;
  const probColor = predicted.color;
  const radial = [{ name: "p", value: probPct, fill: probColor }];

  return (
    <section id="predict" className="py-20 md:py-28 bg-bg-2/40">
      <div className="max-w-6xl mx-auto px-6">
        <SectionHeader
          index="06"
          kicker="โมเดลใช้งานจริง"
          title="ลองให้คะแนนผู้ตอบสด ๆ ดูเลย"
          subtitle="เลือก persona แล้วลากสไลเดอร์. เราคำนวณ z-score เทียบกับการกระจายตัวของกลุ่มนั้น คูณด้วย log-odds เฉพาะคลัสเตอร์ แล้วเข้า softmax เพื่อแยก 3 คำตอบ."
        />

        <div className="grid grid-cols-12 gap-3 mb-6">
          {blocks.map((b) => {
            const p = PERSONA[b.cluster_id as PersonaKey];
            const isActive = b.cluster_id === activeId;
            return (
              <button
                key={b.cluster_id}
                onClick={() => setActiveId(b.cluster_id as PersonaKey)}
                className={`col-span-12 md:col-span-4 text-left rounded-xl p-4 border bg-white hover-lift ${
                  isActive ? "shadow-soft" : ""
                }`}
                style={isActive ? { borderColor: p.color } : { borderColor: "#e7e5e4" }}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-[11px] font-mono text-ink-2">{p.code}</div>
                    <div className="text-base font-semibold text-ink-0 leading-snug">{p.name}</div>
                  </div>
                  <div className="font-mono text-[11px] text-ink-2 text-right tabular leading-snug">
                    n={b.labelled_size}
                    <br />
                    ลอง {fmtPct(b.try_rate)}
                    <br />
                    อาจจะ {fmtPct(b.maybe_rate)}
                  </div>
                </div>
              </button>
            );
          })}
        </div>

        <div className="grid grid-cols-12 gap-5">
          <Card className="col-span-12 lg:col-span-7">
            <div className="tag mb-3">ให้คะแนนความสำคัญ {featureOrder.length} ข้อ</div>
            <div className="space-y-4">
              {featureOrder.map((f) => {
                const label = featureLabels[f] ?? f;
                const helpText = FEATURE_HELP[f] ?? `ให้คะแนนความสำคัญของ ${label} ต่อการตัดสินใจลองสินค้า`;
                const v = values[f];
                return (
                  <div key={f} className="grid grid-cols-12 gap-3 items-center">
                    <div className="col-span-12 md:col-span-4">
                      <div className="text-sm text-ink-0 font-medium">{label}</div>
                      <div className="text-[11px] text-ink-2 leading-snug">{helpText}</div>
                    </div>
                    <div className="col-span-9 md:col-span-7">
                      <input
                        type="range" min={1} max={5} step={1} value={v}
                        onChange={(e) => setValues((prev) => ({ ...prev, [f]: Number(e.target.value) }))}
                      />
                      <div className="flex justify-between text-[10px] text-ink-3 font-mono mt-1">
                        <span>1 · ไม่สำคัญ</span>
                        <span>2</span><span>3</span><span>4</span>
                        <span>5 · สำคัญสุด</span>
                      </div>
                    </div>
                    <div className="col-span-3 md:col-span-1 font-mono text-base text-right tabular" style={{ color: persona.color }}>
                      {v}/5
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>

          <Card className="col-span-12 lg:col-span-5">
            <div className="flex items-center justify-between mb-2">
              <Pill color={persona.color}>
                <Sparkles size={11} /> สด · {persona.code}
              </Pill>
              <div className="font-mono text-[11px] text-ink-2 tabular">
                base = {fmtPct(block.try_rate)} ลอง · {fmtPct(block.maybe_rate)} อาจจะ
              </div>
            </div>

            <div className="relative h-[240px]">
              <ResponsiveContainer>
                <RadialBarChart innerRadius="72%" outerRadius="100%" data={radial} startAngle={210} endAngle={-30}>
                  <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
                  <RadialBar background={{ fill: "#f5f5f4" }} dataKey="value" cornerRadius={20} />
                </RadialBarChart>
              </ResponsiveContainer>
              <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                <AnimatePresence mode="wait">
                  <motion.div
                    key={Math.round(probPct)}
                    initial={{ opacity: 0, y: 4 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -4 }}
                    transition={{ duration: 0.15 }}
                    className="text-5xl font-bold tabular"
                    style={{ color: probColor }}
                  >
                    {probPct.toFixed(0)}%
                  </motion.div>
                </AnimatePresence>
                <div className="text-[11px] font-mono text-ink-2 tracking-widest uppercase mt-1">โอกาสลองแน่นอน</div>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-2 mt-2">
              {TARGET_CHOICES.map((ch) => (
                <div key={ch.key} className="surface-muted p-2 text-center">
                  <div className="text-base font-semibold tabular" style={{ color: ch.color }}>
                    {fmtPct(probs[ch.key])}
                  </div>
                  <div className="text-[10px] text-ink-2 font-mono uppercase mt-0.5">{ch.shortLabel}</div>
                </div>
              ))}
            </div>

            <div className="mt-4 text-[11px] font-mono text-ink-2 grid grid-cols-2 gap-2">
              <div>
                <div className="uppercase tracking-widest">logit</div>
                <div className="text-ink-0 text-base tabular">{logit.toFixed(2)}</div>
              </div>
                <div>
                  <div className="uppercase tracking-widest">intercept</div>
                  <div className="text-ink-0 text-base tabular">
                    {block.model.intercepts!["2"].toFixed(2)}
                  </div>
                </div>
            </div>

            <div className="mt-5">
              <div className="tag mb-2">ทำไมได้คะแนนเท่านี้</div>
              <div className="space-y-1.5">
                {contributions.slice(0, 6).map((c) => {
                  const w = Math.min(100, (Math.abs(c.contrib) / 1.5) * 100);
                  const positive = c.contrib >= 0;
                  return (
                    <div key={c.feature} className="flex items-center gap-2 text-[12px]">
                      <div className="w-28 truncate text-ink-1">{c.label}</div>
                      <div className="flex-1 relative h-2 bg-bg-2 rounded-full overflow-hidden flex">
                        <div className="w-1/2 flex justify-end pr-px">
                          {!positive && (
                            <div className="h-full rounded-full" style={{ width: `${w}%`, background: "#B91C1C" }} />
                          )}
                        </div>
                        <div className="w-px h-full bg-ink-3" />
                        <div className="w-1/2">
                          {positive && (
                            <div className="h-full rounded-full" style={{ width: `${w}%`, background: persona.color }} />
                          )}
                        </div>
                      </div>
                      <div className="w-12 text-right font-mono tabular" style={{ color: positive ? persona.color : "#B91C1C" }}>
                        {positive ? "+" : ""}{c.contrib.toFixed(2)}
                      </div>
                    </div>
                  );
                })}
              </div>
              <p className="text-[11px] text-ink-2 mt-3 leading-relaxed">
                แท่งแสดงว่าแต่ละข้อมีผลต่อโอกาสที่จะลองแน่นอนมากน้อยแค่ไหน สีเขียวคือดันให้ลอง สีแดงคือลดโอกาส โมเดลรวมทุกอย่างแล้วคำนวณเป็นเปอร์เซ็นต์ด้านบน
              </p>
            </div>
          </Card>
        </div>
      </div>
    </section>
  );
}
