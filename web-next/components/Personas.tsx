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
  PolarRadiusAxis
} from "recharts";
import { Card, SectionHeader, Pill } from "./UI";
import { ds, PERSONA, PersonaKey, TARGET_CHOICES, fmtPct } from "@/lib/data";
import { useState } from "react";

const RADAR_FEATURES = [
  "coffee_aroma", "coffee_value", "coffee_brand_trust", "coffee_packaging",
  "coffee_premium", "coffee_smooth", "coffee_convenience", "coffee_nutrition"
];
const SHORT: Record<string, string> = {
  coffee_aroma: "กลิ่น", coffee_value: "คุ้มราคา", coffee_brand_trust: "เชื่อแบรนด์",
  coffee_packaging: "แพ็กเกจ", coffee_premium: "พรีเมียม", coffee_smooth: "นุ่ม",
  coffee_convenience: "หยิบง่าย", coffee_nutrition: "สุขภาพ"
};

const TIP = {
  contentStyle: {
    background: "#fff",
    border: "1px solid #e7e5e4",
    borderRadius: 8,
    fontSize: 12,
    boxShadow: "0 4px 6px -1px rgba(0,0,0,0.05)"
  }
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
    <section id="personas" className="py-20 md:py-28 bg-bg-2/40">
      <div className="max-w-6xl mx-auto px-6">
        <SectionHeader
          index="04"
          kicker="Unsupervised — K-Means"
          title="3 กลุ่มลูกค้าที่ data จับเองโดยไม่ต้องบอก"
          subtitle="เอาคะแนนกาแฟ/ชา 19 ตัว มา standardize แล้วยุบลง 2 มิติด้วย PCA (PC1 = 31.4%, PC2 = 12.8%) จากนั้นรัน K-Means ที่ K=3 (silhouette = 0.30 สูงสุดในช่วง K=2..7). ชื่อ persona เกิดจากค่าเฉลี่ยของจุดศูนย์กลาง — ไม่ได้กำหนดมาก่อน."
        />

        <div className="grid grid-cols-12 gap-5">
          <Card className="col-span-12 lg:col-span-7">
            <div className="flex items-start justify-between mb-2">
              <div>
                <div className="tag">PCA 2 มิติ · 181 คน</div>
                <div className="text-base mt-1 font-semibold text-ink-0">จุดละ 1 คน · ระบายสีตามคลัสเตอร์</div>
              </div>
              <Pill color="#15803D">Silhouette = 0.30</Pill>
            </div>

            <div className="h-[400px]">
              <ResponsiveContainer>
                <ScatterChart margin={{ top: 16, right: 24, bottom: 30, left: 0 }}>
                  <CartesianGrid stroke="#e7e5e4" strokeDasharray="2 4" />
                  <XAxis
                    type="number" dataKey="x" name="PC1"
                    stroke="#a8a29e" tick={{ fontSize: 11, fill: "#a8a29e" }}
                    label={{ value: "PC1 (อธิบายได้ 31.4%)", position: "insideBottom", offset: -10, fill: "#57534E", fontSize: 11 }}
                  />
                  <YAxis
                    type="number" dataKey="y" name="PC2"
                    stroke="#a8a29e" tick={{ fontSize: 11, fill: "#a8a29e" }}
                    label={{ value: "PC2 (12.8%)", angle: -90, position: "insideLeft", fill: "#57534E", fontSize: 11 }}
                  />
                  <ZAxis range={[55, 55]} />
                  <Tooltip {...TIP} cursor={{ strokeDasharray: "3 3", stroke: "#C2410C" }} />
                  {[0, 1, 2].map((cid) => (
                    <Scatter
                      key={cid}
                      name={PERSONA[cid as PersonaKey].name}
                      data={scatter.filter((d) => d.cluster === cid)}
                      fill={PERSONA[cid as PersonaKey].color}
                      opacity={active === cid ? 1 : 0.45}
                      onMouseEnter={() => setActive(cid as PersonaKey)}
                    />
                  ))}
                </ScatterChart>
              </ResponsiveContainer>
            </div>

            <p className="mt-3 text-xs text-ink-2 leading-relaxed">
              <span className="text-ink-0 font-medium">PC1</span> แยกฝั่ง ‘เน้นแบรนด์/พรีเมียม’ (ขวา) ออกจาก ‘เน้นราคา’ (ซ้าย).{" "}
              <span className="text-ink-0 font-medium">PC2</span> มาจาก <span className="font-mono">coffee_intensity</span> — บนคือสายเข้มจัด, ล่างคือสายนุ่ม.
            </p>
          </Card>

          <Card className="col-span-12 lg:col-span-5">
            <div className="tag mb-2">ลายนิ้วมือคลัสเตอร์ · 8 ค่าเฉลี่ย Likert</div>
            <div className="h-[380px]">
              <ResponsiveContainer>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#e7e5e4" />
                  <PolarAngleAxis dataKey="feature" stroke="#a8a29e" tick={{ fontSize: 11, fill: "#292524" }} />
                  <PolarRadiusAxis angle={90} domain={[0, 5]} tick={{ fontSize: 10, fill: "#a8a29e" }} stroke="#e7e5e4" />
                  {clusters.map((c) => {
                    const p = PERSONA[c.cluster_id as PersonaKey];
                    return (
                      <Radar
                        key={c.cluster_id}
                        name={p.name}
                        dataKey={`c${c.cluster_id}`}
                        stroke={p.color}
                        fill={p.color}
                        fillOpacity={active === c.cluster_id ? 0.28 : 0.1}
                        strokeWidth={active === c.cluster_id ? 2 : 1.2}
                      />
                    );
                  })}
                  <Tooltip {...TIP} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
            <p className="text-xs text-ink-2 leading-relaxed">
              คลิกการ์ด persona ด้านล่าง — เส้นจะเด้งตาม. รัศมีคือค่าเฉลี่ย Likert (4.5 = ‘เกือบทุกคนในกลุ่มบอกข้อนี้สำคัญมาก’).
            </p>
          </Card>

          {clusters.map((c, i) => {
            const p = PERSONA[c.cluster_id as PersonaKey];
            const sharePct = (c.size / 181) * 100;
            const isActive = active === c.cluster_id;
            return (
              <motion.div
                key={c.cluster_id}
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.35, delay: i * 0.06 }}
                onMouseEnter={() => setActive(c.cluster_id as PersonaKey)}
                className="col-span-12 md:col-span-4"
              >
                <div
                  className={`surface hover-lift h-full p-6 cursor-pointer ${isActive ? "shadow-soft" : ""}`}
                  style={isActive ? { borderColor: p.color } : undefined}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div
                      className="w-10 h-10 rounded-md text-lg font-bold flex items-center justify-center"
                      style={{ background: `${p.color}14`, color: p.color, border: `1px solid ${p.color}40` }}
                    >
                      {p.iconLetter}
                    </div>
                    <div className="text-right">
                      <div className="font-mono text-[11px] text-ink-2">{p.code}</div>
                      <div className="text-2xl font-semibold tabular" style={{ color: p.color }}>
                        {sharePct.toFixed(0)}%
                      </div>
                      <div className="text-[11px] text-ink-2 font-mono">{c.size} จาก 181</div>
                    </div>
                  </div>

                  <div className="text-base font-semibold text-ink-0 leading-tight">{p.name}</div>
                  <div className="text-xs text-ink-2 mt-1">{p.tagline}</div>
                  <p className="text-[13px] text-ink-2 mt-3 leading-relaxed">{p.description}</p>

                  <div className="mt-4 grid grid-cols-3 gap-1.5">
                    {TARGET_CHOICES.map((choice) => (
                      <div key={choice.key} className="surface-muted p-2 text-center">
                        <div className="text-base font-semibold tabular" style={{ color: choice.color }}>
                          {fmtPct(c.choice_rates[choice.key])}
                        </div>
                        <div className="text-[10px] text-ink-2 font-mono mt-0.5">
                          {choice.shortLabel} · {c.choice_counts[choice.key]}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
