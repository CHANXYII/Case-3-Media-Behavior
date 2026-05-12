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
  const globalBlock = blocks.find((b) => b.cluster_id === null)!;
  const fittedClusters = blocks.filter((b) => b.cluster_id !== null && b.model.fitted);
  const skippedClusters = blocks.filter((b) => b.cluster_id !== null && !b.model.fitted);
  const [activeId, setActiveId] = useState<PersonaKey>(fittedClusters[0]!.cluster_id as PersonaKey);
  const [activeChoice, setActiveChoice] = useState<TargetChoiceKey>("2");
  const active = fittedClusters.find((b) => b.cluster_id === activeId)!;
  const persona = PERSONA[active.cluster_id as PersonaKey];
  const choice = TARGET_CHOICES.find((c) => c.key === activeChoice)!;
  const activeCoefs = active.model.coefficients_by_class![activeChoice];
  const globalCoefs = globalBlock.model.coefficients_by_class![activeChoice];

  const coefRows = activeCoefs
    .slice()
    .sort((a, b) => b.coefficient - a.coefficient)
    .map((c) => ({ label: c.label, coef: Number(c.coefficient.toFixed(3)), odds: c.odds_ratio }));

  const compareData = activeCoefs.map((c) => {
    const g = globalCoefs.find((x) => x.feature === c.feature);
    return { label: c.label, cluster: Number(c.coefficient.toFixed(3)), global: g ? Number(g.coefficient.toFixed(3)) : 0 };
  });

  return (
    <section id="drivers" className="py-20 md:py-28">
      <div className="max-w-6xl mx-auto px-6">
        <SectionHeader
          index="05"
          kicker="Supervised × Unsupervised"
          title="แยกโมเดลทีละกลุ่ม เพื่อหาตัวขับที่แตกต่างกัน"
          subtitle="โมเดลรวมบอกแค่ภาพรวม แต่แต่ละกลุ่มมีเหตุผลในการตัดสินใจที่ต่างกัน เราเทรน Logistic Regression แยกทีละคลัสเตอร์ และแสดงค่า coefficient ของแต่ละคำตอบ แท่งบอกว่าแต่ละคุณสมบัติมีผลต่อการตัดสินใจมากน้อยแค่ไหน"
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
          {skippedClusters.map((c) => {
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
                    มีข้อมูลแค่ 10 คน และคนที่ตอบ ‘ลองแน่นอน’ มีแค่ 1 คน ข้อมูลน้อยเกินไปที่จะสร้างโมเดลที่เชว้เป็น watchlist
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
              <span className="text-ink-0 font-medium">วิธีอ่าน:</span> ค่า +0.9 แปลว่าคนที่ให้คะแนนสูงกว่าค่าเฉลี่ยจะมีโอกาส ‘{choice.label}’ มากขึ้นประมาณ 2.5 เท่า แท่งสีเขียวคือดันให้ลอง แท่งสีแดงคือลดโอกาส
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
              เปลี่ยนคำตอบด้านบนแล้วกราฟจะเปลี่ยนตาม คุณสมบัติเดียวกันอาจดัน ‘อาจจะลอง’ แต่กลับลด ‘ลองแน่นอน’ ได้ เพราะฉะนั้นต้องแยกวิเคราะห์ทั้ง 3 คำตอบ
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
                      กลุ่มหลักที่จะลองแน่นอนถูกดันด้วยโภชนาการและกลิ่นลุ่มนี้ลอง ต้องเน้นว่าดีต่อสุขภาพและมีกลิ่นหอม
                    </li>
                    <li>
                      <span className="text-accent-jade font-bold">P2 ·</span>{" "}
                      กลุ่มพรีเมียมที่จะลองแน่นอนถูกดันด้วยกลิ่นและความคุ้มค่า ต้องขายว่ากลิ่นดีและราคาคุ้มกับคุณภาพ
                    </li>
                    <li>
                      <span className="text-accent-violet font-bold">P1 ·</span>{" "}
                      กลุ่มไม่กาแฟมีคนที่จะลองแน่นอนแค่ 1 คนจาก 10 ข้อมูลน้อยเกินไปที่จะวิเคราะห์ ควรลองเสนอชาหรือเครื่องดื่มเพื่อสุขภาพแทน
                    </li>
                  </ul>
                </div>

                <div className="col-span-12 md:col-span-5">
                  <div className="grid grid-cols-2 gap-3">
                    {fittedClusters.map((c) => {
                      const p = PERSONA[c.cluster_id as PersonaKey];
                      const top = c.model.coefficients_by_class![activeChoice][0];
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
