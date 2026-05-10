"use client";
import { motion } from "framer-motion";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Cell
} from "recharts";
import { Card, SectionHeader, Pill } from "./UI";
import { ds, PERSONA, PersonaKey, fmtPct } from "@/lib/data";
import { useState } from "react";

const RADAR_FEATURES = [
  "coffee_aroma",
  "coffee_value",
  "coffee_brand_trust",
  "coffee_packaging",
  "coffee_premium",
  "coffee_smooth",
  "coffee_convenience",
  "coffee_nutrition"
];
const SHORT: Record<string, string> = {
  coffee_aroma: "กลิ่น",
  coffee_value: "คุ้มราคา",
  coffee_brand_trust: "เชื่อแบรนด์",
  coffee_packaging: "แพ็กเกจ",
  coffee_premium: "พรีเมียม",
  coffee_smooth: "นุ่ม",
  coffee_convenience: "หยิบง่าย",
  coffee_nutrition: "สุขภาพ"
};

export default function Personas() {
  const blocks = ds.clusterSupervised.blocks;
  const clusters = blocks.filter((b) => b.cluster_id !== null);
  const [active, setActive] = useState<PersonaKey>(0);

  const radarData = RADAR_FEATURES.map((f) => {
    const row: any = { feature: SHORT[f] };
    clusters.forEach((c) => {
      const fm = c.feature_means.find((x) => x.name === f);
      row[`c${c.cluster_id}`] = fm ? Number(fm.cluster_mean.toFixed(2)) : 0;
    });
    return row;
  });

  const scatter = ds.dashboard.pca_scatter;

  return (
    <section id="personas" className="py-24 md:py-32 relative">
      <div className="max-w-7xl mx-auto px-6">
        <SectionHeader
          index="04"
          kicker="Unsupervised — K-Means"
          title="3 กลุ่มลูกค้าที่ data จับเองโดยไม่ต้องบอก"
          subtitle="เอาคะแนนกาแฟ/ชา 19 ตัว มา standardize แล้วยุบลง 2 มิติด้วย PCA (PC1 อธิบาย variance ได้ 31.4%, PC2 อีก 12.8%) จากนั้นรัน K-Means ที่ K=3 (เลือกจาก silhouette = 0.30 ที่สูงสุดในช่วง K=2..7). ชื่อ persona เกิดจากค่าเฉลี่ยของจุดศูนย์กลางคลัสเตอร์ ไม่ได้กำหนดมาก่อน."
        />

        <div className="grid grid-cols-12 gap-6">
          <Card className="col-span-12 lg:col-span-7">
            <div className="flex items-start justify-between mb-2">
              <div>
                <div className="text-xs font-mono text-ink-2 tracking-widest uppercase">
                  PCA 2 มิติ · 181 คน
                </div>
                <div className="font-display text-xl mt-1 font-semibold">
                  จุดละ 1 คน ระบายสีตามคลัสเตอร์
                </div>
              </div>
              <Pill>Silhouette = 0.30</Pill>
            </div>

            <div className="h-[420px]">
              <ResponsiveContainer>
                <ScatterChart margin={{ top: 20, right: 30, bottom: 30, left: 0 }}>
                  <CartesianGrid stroke="#252019" strokeDasharray="2 4" />
                  <XAxis
                    type="number"
                    dataKey="x"
                    name="PC1"
                    stroke="#5C5547"
                    tick={{ fontSize: 11, fill: "#5C5547" }}
                    label={{
                      value: "PC1 (อธิบายได้ 31.4%)",
                      position: "insideBottom",
                      offset: -10,
                      fill: "#9A917F",
                      fontSize: 11
                    }}
                  />
                  <YAxis
                    type="number"
                    dataKey="y"
                    name="PC2"
                    stroke="#5C5547"
                    tick={{ fontSize: 11, fill: "#5C5547" }}
                    label={{
                      value: "PC2 (อธิบายได้ 12.8%)",
                      angle: -90,
                      position: "insideLeft",
                      fill: "#9A917F",
                      fontSize: 11
                    }}
                  />
                  <ZAxis range={[60, 60]} />
                  <Tooltip
                    cursor={{ strokeDasharray: "3 3", stroke: "#E0A458" }}
                    contentStyle={{
                      background: "#13110D",
                      border: "1px solid rgba(224,164,88,0.3)",
                      borderRadius: 8,
                      fontSize: 12
                    }}
                  />
                  {[0, 1, 2].map((cid) => (
                    <Scatter
                      key={cid}
                      name={PERSONA[cid as PersonaKey].name}
                      data={scatter.filter((d) => d.cluster === cid)}
                      fill={PERSONA[cid as PersonaKey].color}
                      opacity={active === cid ? 1 : 0.55}
                      onMouseEnter={() => setActive(cid as PersonaKey)}
                    />
                  ))}
                </ScatterChart>
              </ResponsiveContainer>
            </div>

            <p className="mt-3 text-xs text-ink-2 leading-relaxed">
              <span className="text-ink-1">PC1</span> คือแกนแยกฝั่ง ‘เน้นแบรนด์/พรีเมียม’ (ขวา)
              ออกจาก ‘เน้นราคา’ (ซ้าย). <span className="text-ink-1">PC2</span> ส่วนใหญ่มาจาก{" "}
              <span className="font-mono">coffee_intensity</span> — ด้านบนคือสายเข้มจัด
              ด้านล่างคือสายนุ่ม. การยุบเหลือ 2 มิติทำให้เราทิ้ง variance ไป 56% ก็จริง แต่โครงสร้างของกลุ่มยังอ่านออก
              และวาดบนหน้าจอได้.
            </p>
          </Card>

          <Card className="col-span-12 lg:col-span-5">
            <div className="text-xs font-mono text-ink-2 tracking-widest uppercase mb-1">
              ลายนิ้วมือคลัสเตอร์ · radar 8 ค่าเฉลี่ย Likert
            </div>
            <div className="h-[400px]">
              <ResponsiveContainer>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#332B22" />
                  <PolarAngleAxis
                    dataKey="feature"
                    stroke="#9A917F"
                    tick={{ fontSize: 11, fill: "#D9D2C2" }}
                  />
                  <PolarRadiusAxis
                    angle={90}
                    domain={[0, 5]}
                    tick={{ fontSize: 10, fill: "#5C5547" }}
                    stroke="#332B22"
                  />
                  {clusters.map((c) => {
                    const p = PERSONA[c.cluster_id as PersonaKey];
                    return (
                      <Radar
                        key={c.cluster_id}
                        name={p.name}
                        dataKey={`c${c.cluster_id}`}
                        stroke={p.color}
                        fill={p.color}
                        fillOpacity={active === c.cluster_id ? 0.32 : 0.16}
                        strokeWidth={active === c.cluster_id ? 2.5 : 1.5}
                      />
                    );
                  })}
                  <Tooltip
                    contentStyle={{
                      background: "#13110D",
                      border: "1px solid rgba(224,164,88,0.3)",
                      borderRadius: 8,
                      fontSize: 11
                    }}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>
            <p className="text-xs text-ink-2 mt-2 leading-relaxed">
              คลิกการ์ด persona ด้านล่าง — เส้น radar/scatter จะเด้งตามให้. รัศมีคือค่าเฉลี่ย Likert ตรงๆ
              ดังนั้น 4.5 แปลว่า ‘เกือบทุกคนในกลุ่มนี้บอกข้อนี้สำคัญมาก’.
            </p>
          </Card>

          {clusters.map((c, i) => {
            const p = PERSONA[c.cluster_id as PersonaKey];
            const sharePct = (c.size / 181) * 100;
            return (
              <motion.div
                key={c.cluster_id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                onMouseEnter={() => setActive(c.cluster_id as PersonaKey)}
                className="col-span-12 md:col-span-4"
              >
                <Card
                  className="h-full cursor-pointer transition-all"
                  glow={active === c.cluster_id}
                >
                  <div
                    className="absolute -top-12 -right-12 w-40 h-40 rounded-full opacity-30 blur-2xl"
                    style={{ background: p.color }}
                  />
                  <div className="flex items-start justify-between mb-3 relative">
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
                    <div className="text-right">
                      <div className="font-mono text-xs text-ink-2">{p.code}</div>
                      <div className="font-display text-3xl" style={{ color: p.color }}>
                        {sharePct.toFixed(0)}%
                      </div>
                      <div className="text-xs text-ink-2 font-mono">{c.size} จาก 181</div>
                    </div>
                  </div>

                  <div className="font-display text-xl leading-tight">{p.name}</div>
                  <div className="text-xs text-ink-2 mt-1">{p.tagline}</div>
                  <p className="text-sm text-ink-1/80 mt-3 leading-relaxed">{p.description}</p>

                  <div className="mt-4 grid grid-cols-3 gap-2 text-center">
                    <div className="rounded-lg bg-bg-2/60 p-2">
                      <div className="font-display text-lg" style={{ color: p.color }}>
                        {c.try_rate ? fmtPct(c.try_rate) : "—"}
                      </div>
                      <div className="text-[10px] text-ink-2 font-mono uppercase mt-0.5">
                        จะลอง
                      </div>
                    </div>
                    <div className="rounded-lg bg-bg-2/60 p-2">
                      <div className="font-display text-lg" style={{ color: p.color }}>
                        {c.try_count}
                      </div>
                      <div className="text-[10px] text-ink-2 font-mono uppercase mt-0.5">ลอง</div>
                    </div>
                    <div className="rounded-lg bg-bg-2/60 p-2">
                      <div className="font-display text-lg text-ink-1">{c.non_try_count}</div>
                      <div className="text-[10px] text-ink-2 font-mono uppercase mt-0.5">ไม่ลอง</div>
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
