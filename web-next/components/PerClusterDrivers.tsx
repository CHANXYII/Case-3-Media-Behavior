"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  Cell,
  ReferenceLine
} from "recharts";
import { Card, SectionHeader, Pill } from "./UI";
import { ds, PERSONA, PersonaKey, TARGET_CHOICES, TargetChoiceKey, fmtPct } from "@/lib/data";

const TIP = {
  contentStyle: {
    background: "#fff",
    border: "1px solid #e7e5e4",
    borderRadius: 8,
    fontSize: 12,
    boxShadow: "0 4px 6px -1px rgba(0,0,0,0.05)"
  }
};

export default function PerClusterDrivers() {
  const blocks = ds.clusterSupervised.blocks;
  const fittedClusters = blocks.filter((b) => b.cluster_id !== null && b.model.fitted);
  const [activeId, setActiveId] = useState<PersonaKey>(0);
  const [activeChoice, setActiveChoice] = useState<TargetChoiceKey>("2");
  const active = fittedClusters.find((b) => b.cluster_id === activeId) || fittedClusters[0];
  const persona = PERSONA[active.cluster_id as PersonaKey];
  const choice = TARGET_CHOICES.find((c) => c.key === activeChoice) ?? TARGET_CHOICES[2];

  const coefRows = (active.model.coefficients_by_class?.[activeChoice] ?? active.model.coefficients ?? [])
    .slice()
    .sort((a, b) => b.coefficient - a.coefficient)
    .map((c) => ({ label: c.label, coef: Number(c.coefficient.toFixed(3)), odds: c.odds_ratio }));

  const globalBlock = blocks.find((b) => b.cluster_id === null);
  const compareData = (active.model.coefficients_by_class?.[activeChoice] ?? active.model.coefficients ?? []).map((c) => {
    const globalCoefs = globalBlock?.model.fitted
      ? globalBlock.model.coefficients_by_class?.[activeChoice] ?? globalBlock.model.coefficients ?? []
      : [];
    const g = globalCoefs.find((x) => x.feature === c.feature);
    return { label: c.label, cluster: Number(c.coefficient.toFixed(3)), global: g ? Number(g.coefficient.toFixed(3)) : 0 };
  });

  return (
    <section id="drivers" className="py-20 md:py-28">
      <div className="max-w-6xl mx-auto px-6">
        <SectionHeader
          index="05"
          kicker="Supervised × Unsupervised"
          title="ฟิตโมเดลแยกทีละกลุ่ม — นี่คือไฮไลต์"
          subtitle="โมเดลรวมก้อนเดียวบอกแค่ ‘กลิ่นสำคัญ’. แต่ target แยก 3 คำตอบ. เราเทรน Logistic Regression แยกทีละ cluster และแสดง coefficient แยกตาม choice. ทุกฟีเจอร์ Likert ผ่าน standardize — แท่งคือ ‘log-odds เปลี่ยนเท่าไรเมื่อ +1 SD’."
        />

        <div className="grid grid-cols-12 gap-3 mb-6">
          {fittedClusters.map((c) => {
            const p = PERSONA[c.cluster_id as PersonaKey];
            const isActive = c.cluster_id === activeId;
            return (
              <button
                key={c.cluster_id}
                onClick={() => setActiveId(c.cluster_id as PersonaKey)}
                className={`col-span-12 md:col-span-4 text-left rounded-xl p-5 border bg-white hover-lift ${
                  isActive ? "shadow-soft" : ""
                }`}
                style={isActive ? { borderColor: p.color } : { borderColor: "#e7e5e4" }}
              >
                <div className="flex items-center justify-between mb-2">
                  <Pill color={p.color}>{p.code}</Pill>
                  <div className="font-mono text-[11px] text-ink-2 tabular">
                    n={c.labelled_size} · acc={(c.model.train_accuracy! * 100).toFixed(0)}%
                  </div>
                </div>
                <div className="text-base font-semibold text-ink-0 leading-snug">{p.name}</div>
                <div className="text-xs text-ink-2 mt-1">{p.tagline}</div>
                <div className="mt-3 grid grid-cols-3 gap-1 text-center">
                  {TARGET_CHOICES.map((ch) => (
                    <div key={ch.key}>
                      <div className="text-sm font-semibold tabular" style={{ color: ch.color }}>
                        {fmtPct(c.choice_rates[ch.key])}
                      </div>
                      <div className="text-[9px] text-ink-2 font-mono uppercase">{ch.shortLabel}</div>
                    </div>
                  ))}
                </div>
              </button>
            );
          })}
          {blocks
            .filter((b) => b.cluster_id !== null && !b.model.fitted)
            .map((c) => {
              const p = PERSONA[c.cluster_id as PersonaKey];
              return (
                <div
                  key={c.cluster_id}
                  className="col-span-12 md:col-span-4 rounded-xl p-5 border border-dashed border-ink-3 bg-bg-2/30"
                >
                  <div className="flex items-center justify-between mb-2">
                    <Pill color={p.color}>{p.code}</Pill>
                    <div className="font-mono text-[11px] text-ink-2">n={c.labelled_size} · ข้าม</div>
                  </div>
                  <div className="text-base font-semibold text-ink-0 leading-snug">{p.name}</div>
                  <div className="text-xs text-ink-2 mt-1 leading-relaxed">
                    มีแค่ 10 คนที่ label และคลาส ‘ลองแน่นอน’ มี 1 คน — ฟิต logistic regression 3 คลาสบน 10 แถวจะแกว่ง. เก็บไว้เป็น watchlist.
                  </div>
                </div>
              );
            })}
        </div>

        <div className="flex flex-wrap gap-2 mb-5">
          {TARGET_CHOICES.map((option) => {
            const isActive = option.key === activeChoice;
            return (
              <button
                key={option.key}
                onClick={() => setActiveChoice(option.key)}
                className={`rounded-full px-4 py-1.5 text-xs font-mono border transition ${
                  isActive ? "border-transparent" : "border-ink-3 text-ink-2 bg-white hover:border-ink-2"
                }`}
                style={isActive ? { background: `${option.color}14`, color: option.color, borderColor: `${option.color}50` } : undefined}
              >
                coefficient → {option.label}
              </button>
            );
          })}
        </div>

        <div className="grid grid-cols-12 gap-5">
          <Card className="col-span-12 lg:col-span-7">
            <div className="flex items-start justify-between mb-1">
              <div>
                <div className="tag">ตัวขับเชิงพฤติกรรม · {persona.name}</div>
                <div className="text-base mt-1 font-semibold text-ink-0">
                  เรียงตาม log-odds (บวก = ดันให้ ‘{choice.label}’)
                </div>
              </div>
              <Pill color={choice.color}>{persona.code} · {choice.shortLabel}</Pill>
            </div>

            <div className="h-[440px] mt-4">
              <ResponsiveContainer>
                <BarChart data={coefRows} layout="vertical" margin={{ top: 10, right: 30, bottom: 10, left: 110 }}>
                  <CartesianGrid stroke="#e7e5e4" strokeDasharray="2 4" horizontal={false} />
                  <XAxis type="number" stroke="#a8a29e" tick={{ fontSize: 10, fill: "#a8a29e" }} axisLine={false} tickLine={false} />
                  <YAxis type="category" dataKey="label" stroke="#a8a29e" tick={{ fontSize: 11, fill: "#292524" }} axisLine={false} tickLine={false} width={150} />
                  <Tooltip
                    {...TIP}
                    cursor={{ fill: "rgba(194,65,12,0.04)" }}
                    formatter={(_v: any, _n: any, p: any) => {
                      const odds = p.payload.odds.toFixed(2);
                      return [`coef = ${p.payload.coef} · OR = ${odds}×`, ""];
                    }}
                  />
                  <ReferenceLine x={0} stroke="#a8a29e" />
                  <Bar dataKey="coef" radius={[0, 4, 4, 0]}>
                    {coefRows.map((d, i) => (
                      <Cell key={i} fill={d.coef >= 0 ? choice.color : "#B91C1C"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            <p className="text-xs text-ink-2 mt-2 leading-relaxed">
              <span className="text-ink-0 font-medium">วิธีอ่าน:</span> coefficient +0.9 บนกลิ่นแปลว่า คนที่ใส่ใจกลิ่นมากกว่าค่าเฉลี่ย 1 SD จะมีโอกาสเข้า ‘{choice.label}’ <span className="font-mono text-accent-gold">e^0.9 ≈ 2.46×</span> ของคนทั่วไปในกลุ่ม. แท่งลบคือกลับด้าน.
            </p>
          </Card>

          <Card className="col-span-12 lg:col-span-5">
            <div className="tag mb-3">คลัสเตอร์ vs โกลบอล · {choice.shortLabel}</div>
            <div className="h-[440px]">
              <ResponsiveContainer>
                <BarChart data={compareData} layout="vertical" margin={{ top: 10, right: 20, bottom: 10, left: 90 }} barCategoryGap={6}>
                  <CartesianGrid stroke="#e7e5e4" strokeDasharray="2 4" horizontal={false} />
                  <XAxis type="number" stroke="#a8a29e" tick={{ fontSize: 10, fill: "#a8a29e" }} axisLine={false} tickLine={false} />
                  <YAxis type="category" dataKey="label" stroke="#a8a29e" tick={{ fontSize: 10, fill: "#292524" }} axisLine={false} tickLine={false} width={130} />
                  <ReferenceLine x={0} stroke="#a8a29e" />
                  <Tooltip {...TIP} cursor={{ fill: "rgba(194,65,12,0.04)" }} />
                  <Bar dataKey="global" name="โกลบอล" fill="#a8a29e" radius={[0, 3, 3, 0]} />
                  <Bar dataKey="cluster" name={persona.code} fill={choice.color} radius={[0, 3, 3, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <p className="text-xs text-ink-2 mt-2 leading-relaxed">
              เปลี่ยน choice ด้านบนแล้วกราฟจะสลับ coefficient ตามคลาสทันที. ฟีเจอร์เดียวกันอาจดัน ‘อาจจะลอง’ แต่กด ‘ลองแน่นอน’ ลงได้ — จึงไม่ควรรวม target เป็น binary.
            </p>
          </Card>

          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="col-span-12"
          >
            <Card>
              <div className="grid grid-cols-12 gap-6 items-center">
                <div className="col-span-12 md:col-span-7">
                  <div className="tag mb-2">เรื่องเล่าหนึ่งประโยคต่อกลุ่ม</div>
                  <ul className="space-y-3 text-[14px] leading-relaxed text-ink-2">
                    <li>
                      <span className="text-accent-gold font-bold">P0 ·</span>{" "}
                      สาย Mainstream ที่จะลองแน่นอนถูกดันด้วยโภชนาการ + กลิ่น — เน้น <span className="font-mono text-ink-1">+0.55 Nutrition</span>, <span className="font-mono text-ink-1">+0.54 Aroma</span>.
                    </li>
                    <li>
                      <span className="text-accent-jade font-bold">P2 ·</span>{" "}
                      สาย Premium ที่จะลองแน่นอนถูกดันด้วยกลิ่น + ความคุ้มค่า — เน้น <span className="font-mono text-ink-1">+0.75 Aroma</span>, <span className="font-mono text-ink-1">+0.63 Value</span>; ห้ามขายความนุ่มเกินไป.
                    </li>
                    <li>
                      <span className="text-accent-violet font-bold">P1 ·</span>{" "}
                      สายไม่กาแฟมี ‘ลองแน่นอน’ แค่ 1 คนจาก 10 — ยังไม่พอทำ coefficient. เก็บไว้ยิงด้วย SKU ชา/wellness แทน.
                    </li>
                  </ul>
                </div>

                <div className="col-span-12 md:col-span-5">
                  <div className="grid grid-cols-2 gap-3">
                    {fittedClusters.map((c) => {
                      const p = PERSONA[c.cluster_id as PersonaKey];
                      const top = (c.model.coefficients_by_class?.[activeChoice] ?? c.model.coefficients ?? [])[0];
                      return (
                        <div
                          key={c.cluster_id}
                          className="rounded-lg p-4 border bg-white"
                          style={{ borderColor: `${p.color}30` }}
                        >
                          <div className="text-[11px] font-mono text-ink-2 mb-1">{p.code} · {choice.shortLabel}</div>
                          <div className="text-sm font-semibold leading-snug text-ink-0">{p.name}</div>
                          {top && (
                            <>
                              <div className="mt-3 text-[11px] font-mono text-ink-2 uppercase tracking-wider">ตัวขับอันดับ 1</div>
                              <div className="text-sm font-semibold mt-0.5" style={{ color: choice.color }}>{top.label}</div>
                              <div className="text-xs font-mono text-ink-1 mt-1 tabular">
                                {top.coefficient > 0 ? "+" : ""}{top.coefficient.toFixed(2)} · OR = {top.odds_ratio.toFixed(2)}×
                              </div>
                            </>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </Card>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
