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
import { ds, PERSONA, PersonaKey } from "@/lib/data";

export default function PerClusterDrivers() {
  const blocks = ds.clusterSupervised.blocks;
  const fittedClusters = blocks.filter(
    (b) => b.cluster_id !== null && b.model.fitted
  );
  const [activeId, setActiveId] = useState<PersonaKey>(0);
  const active = fittedClusters.find((b) => b.cluster_id === activeId) || fittedClusters[0];
  const persona = PERSONA[active.cluster_id as PersonaKey];

  const coefRows = (active.model.coefficients ?? [])
    .slice()
    .sort((a, b) => b.coefficient - a.coefficient)
    .map((c) => ({
      label: c.label,
      coef: Number(c.coefficient.toFixed(3)),
      odds: c.odds_ratio
    }));

  const globalBlock = blocks.find((b) => b.cluster_id === null);
  const compareData = (active.model.coefficients ?? []).map((c) => {
    const g = globalBlock?.model.fitted
      ? globalBlock.model.coefficients.find((x) => x.feature === c.feature)
      : undefined;
    return {
      label: c.label,
      cluster: Number(c.coefficient.toFixed(3)),
      global: g ? Number(g.coefficient.toFixed(3)) : 0
    };
  });

  return (
    <section id="drivers" className="py-24 md:py-32 relative">
      <div className="max-w-7xl mx-auto px-6">
        <SectionHeader
          index="05"
          kicker="Supervised × Unsupervised"
          title="ฟิตโมเดลแยกทีละกลุ่ม — นี่คือไฮไลต์"
          subtitle="โมเดลรวมก้อนเดียวบอกแค่ว่า ‘กลิ่นสำคัญ’. แต่ ‘กลิ่น’ สำคัญต่างกันในแต่ละกลุ่ม — สาย Premium จริงๆ แล้วใส่ใจ ‘คุ้มราคา’ มากกว่า, สาย Mainstream เน้น ‘หยิบง่าย’. เราเลยเทรน Logistic Regression แยกทีละ cluster ทำให้ได้สมการ log-odds ของตัวเอง. ทุกฟีเจอร์ Likert ผ่าน standardize แล้ว แท่งกราฟคือ ‘log-odds เปลี่ยนเท่าไรเมื่อ +1 SD’."
        />

        <div className="grid grid-cols-12 gap-3 mb-8">
          {fittedClusters.map((c) => {
            const p = PERSONA[c.cluster_id as PersonaKey];
            const isActive = c.cluster_id === activeId;
            return (
              <button
                key={c.cluster_id}
                onClick={() => setActiveId(c.cluster_id as PersonaKey)}
                className={`col-span-12 md:col-span-4 text-left rounded-2xl p-5 border transition-all ${
                  isActive ? "border-accent-gold/60" : "border-white/8 hover:border-white/20"
                }`}
                style={
                  isActive
                    ? {
                        background: `linear-gradient(135deg, ${p.color}18, ${p.color}05)`,
                        boxShadow: `0 0 50px -20px ${p.color}80`
                      }
                    : { background: "rgba(255,255,255,0.02)" }
                }
              >
                <div className="flex items-center justify-between mb-2">
                  <Pill color={p.color}>{p.code}</Pill>
                  <div className="font-mono text-xs text-ink-2">
                    n={c.labelled_size} · acc={(c.model.train_accuracy! * 100).toFixed(0)}%
                  </div>
                </div>
                <div className="font-display text-lg leading-tight font-semibold">{p.name}</div>
                <div className="text-xs text-ink-2 mt-1">{p.tagline}</div>
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
                  className="col-span-12 md:col-span-4 text-left rounded-2xl p-5 border border-dashed border-white/10 bg-white/[0.01]"
                >
                  <div className="flex items-center justify-between mb-2">
                    <Pill color={p.color}>{p.code}</Pill>
                    <div className="font-mono text-xs text-ink-2">
                      n={c.labelled_size} · ข้าม
                    </div>
                  </div>
                  <div className="font-display text-lg leading-tight font-semibold">{p.name}</div>
                  <div className="text-xs text-ink-2 mt-1">
                    มีแค่ 10 คนที่ label แบ่ง 6/4 — ฟิต logistic regression บน 10 แถวจะได้
                    coefficient ที่แกว่ง (CI พาดเส้น 0). ขอเก็บไว้เป็น watchlist ก่อน ยังไม่ใช่กลุ่มเป้าหมาย.
                  </div>
                </div>
              );
            })}
        </div>

        <div className="grid grid-cols-12 gap-6">
          <Card className="col-span-12 lg:col-span-7" glow>
            <div className="flex items-start justify-between mb-1">
              <div>
                <div className="text-xs font-mono text-ink-2 tracking-widest uppercase">
                  ตัวขับเชิงพฤติกรรม · {persona.name}
                </div>
                <div className="font-display text-2xl mt-1 font-semibold">
                  เรียงตาม log-odds (บวก = ดันให้ ‘จะลอง’).
                </div>
              </div>
              <Pill color={persona.color}>{persona.code}</Pill>
            </div>

            <div className="h-[460px] mt-4">
              <ResponsiveContainer>
                <BarChart
                  data={coefRows}
                  layout="vertical"
                  margin={{ top: 10, right: 30, bottom: 10, left: 110 }}
                >
                  <CartesianGrid stroke="#252019" strokeDasharray="2 4" horizontal={false} />
                  <XAxis
                    type="number"
                    stroke="#5C5547"
                    tick={{ fontSize: 10, fill: "#5C5547" }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    type="category"
                    dataKey="label"
                    stroke="#9A917F"
                    tick={{ fontSize: 11, fill: "#D9D2C2" }}
                    axisLine={false}
                    tickLine={false}
                    width={150}
                  />
                  <Tooltip
                    cursor={{ fill: "rgba(224,164,88,0.05)" }}
                    contentStyle={{
                      background: "#13110D",
                      border: `1px solid ${persona.color}55`,
                      borderRadius: 8,
                      fontSize: 12
                    }}
                    formatter={(_v: any, _n: any, p: any) => {
                      const odds = p.payload.odds.toFixed(2);
                      return [`coef = ${p.payload.coef} · OR = ${odds}×`, ""];
                    }}
                  />
                  <ReferenceLine x={0} stroke="#5C5547" />
                  <Bar dataKey="coef" radius={[0, 6, 6, 0]}>
                    {coefRows.map((d, i) => (
                      <Cell
                        key={i}
                        fill={d.coef >= 0 ? persona.color : "#D85A5A"}
                        opacity={0.85 + Math.min(0.15, Math.abs(d.coef) / 5)}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            <p className="text-xs text-ink-2 mt-2 leading-relaxed">
              <span className="text-ink-1">วิธีอ่านแท่ง:</span> coefficient +0.9 บนกลิ่น (ที่ผ่าน standardize)
              แปลว่า คนที่ใส่ใจกลิ่นมากกว่าค่าเฉลี่ยของกลุ่มอยู่ 1 SD จะมีโอกาสลอง RTD ใหม่{" "}
              <span className="font-mono text-accent-gold">e^0.9 ≈ 2.46×</span> ของคนทั่วไปในกลุ่ม.
              แท่งลบคือกลับด้าน — ยิ่งใส่ใจ ยิ่งไม่ลอง.
            </p>
          </Card>

          <Card className="col-span-12 lg:col-span-5">
            <div className="text-xs font-mono text-ink-2 tracking-widest uppercase mb-3">
              คลัสเตอร์ vs โกลบอล · ฟีเจอร์เดียวกัน น้ำหนักต่างกัน
            </div>
            <div className="h-[460px]">
              <ResponsiveContainer>
                <BarChart
                  data={compareData}
                  layout="vertical"
                  margin={{ top: 10, right: 20, bottom: 10, left: 90 }}
                  barCategoryGap={6}
                >
                  <CartesianGrid stroke="#252019" strokeDasharray="2 4" horizontal={false} />
                  <XAxis
                    type="number"
                    stroke="#5C5547"
                    tick={{ fontSize: 10, fill: "#5C5547" }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    type="category"
                    dataKey="label"
                    stroke="#9A917F"
                    tick={{ fontSize: 10, fill: "#D9D2C2" }}
                    axisLine={false}
                    tickLine={false}
                    width={130}
                  />
                  <ReferenceLine x={0} stroke="#5C5547" />
                  <Tooltip
                    cursor={{ fill: "rgba(224,164,88,0.05)" }}
                    contentStyle={{
                      background: "#13110D",
                      border: "1px solid rgba(224,164,88,0.3)",
                      borderRadius: 8,
                      fontSize: 11
                    }}
                  />
                  <Bar dataKey="global" name="โกลบอล" fill="#5C5547" radius={[0, 4, 4, 0]} />
                  <Bar dataKey="cluster" name={persona.code} fill={persona.color} radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <p className="text-xs text-ink-2 mt-2 leading-relaxed">
              ดู <span className="text-ink-1">กลิ่น</span>: ในระดับโกลบอลคือตัวขับสำคัญ แต่กับสาย Premium (P2)
              เกือบเป็น 0 เพราะเขาคิดว่ากลิ่นต้องดีอยู่แล้ว ตัดสินใจที่ ‘คุ้มราคา’ กับ ‘แพ็กเกจ’ แทน.
              นี่แหละสาเหตุที่ต้องแยกโมเดลทีละกลุ่ม ไม่งั้น nuance พวกนี้หายเรียบ.
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
                  <div className="text-xs font-mono text-ink-2 tracking-widest uppercase mb-2">
                    เรื่องเล่าหนึ่งประโยคต่อกลุ่ม
                  </div>
                  <ul className="space-y-3 text-sm leading-relaxed">
                    <li>
                      <span className="font-display text-base text-accent-gold font-bold">P0 ·</span>{" "}
                      <span className="text-ink-1">
                        สาย Mainstream จะลองเมื่อกลิ่นโดน + ราคาหยิบง่าย — เน้น{" "}
                        <span className="font-mono">+0.90 กลิ่น</span>,{" "}
                        <span className="font-mono">+0.45 หยิบง่าย</span>.
                      </span>
                    </li>
                    <li>
                      <span className="font-display text-base text-accent-jade font-bold">P2 ·</span>{" "}
                      <span className="text-ink-1">
                        สาย Premium จะลองเมื่อรู้สึกคุ้ม + แพ็กเกจดูดี — เน้น{" "}
                        <span className="font-mono">+1.05 คุ้มราคา</span>,{" "}
                        <span className="font-mono">+0.72 แพ็กเกจ</span>;
                        ห้ามเคลมว่าเข้มเกิน (สัมประสิทธิ์ติดลบ).
                      </span>
                    </li>
                    <li>
                      <span className="font-display text-base text-accent-violet font-bold">P1 ·</span>{" "}
                      <span className="text-ink-1">
                        สายไม่กาแฟให้คะแนนทุกข้อ 1.x — ไม่ใช่ลูกค้ากาแฟ. เก็บไว้ยิงด้วย SKU ชา/wellness แทน.
                      </span>
                    </li>
                  </ul>
                </div>

                <div className="col-span-12 md:col-span-5">
                  <div className="grid grid-cols-2 gap-3">
                    {fittedClusters.map((c) => {
                      const p = PERSONA[c.cluster_id as PersonaKey];
                      const top = (c.model.coefficients ?? [])[0];
                      return (
                        <div
                          key={c.cluster_id}
                          className="rounded-xl p-4 border"
                          style={{ borderColor: `${p.color}44`, background: `${p.color}10` }}
                        >
                          <div className="text-xs font-mono text-ink-2 mb-1">{p.code}</div>
                          <div className="font-display text-sm leading-tight font-semibold">{p.name}</div>
                          {top && (
                            <>
                              <div className="mt-3 font-mono text-xs text-ink-2">ตัวขับอันดับ 1</div>
                              <div className="font-display text-base font-bold" style={{ color: p.color }}>
                                {top.label}
                              </div>
                              <div className="text-xs font-mono text-ink-1 mt-1">
                                {top.coefficient > 0 ? "+" : ""}
                                {top.coefficient.toFixed(2)} · OR ={" "}
                                {top.odds_ratio.toFixed(2)}×
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
