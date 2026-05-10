"use client";
import { motion } from "framer-motion";
import {
  BarChart,
  Bar,
  Cell,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Sector
} from "recharts";
import { useState } from "react";
import { ds } from "@/lib/data";
import { Card, SectionHeader, Pill } from "./UI";

const GENDER_LABELS: Record<string, string> = {
  หญิง: "หญิง",
  ชาย: "ชาย",
  ไม่ระบุ: "ไม่ระบุ"
};
const AGE_LABELS: Record<string, string> = {
  "ต่ำกว่า 18ปี": "ต่ำกว่า 18",
  "18-22ปี": "18–22",
  "23-29ปี": "23–29",
  "30-39ปี": "30–39",
  "40-49ปี": "40–49",
  "50ปี ขึ้นไป": "50+"
};
const OCC_LABELS: Record<string, string> = {
  พนักงานบริษัทเอกชน: "พนักงานบริษัท",
  ธุรกิจส่วนตัว: "ธุรกิจส่วนตัว",
  นักเรียน: "นักเรียน",
  "ฟรีแลนซ์/อาชีพอิสระ": "ฟรีแลนซ์",
  นักศึกษา: "นักศึกษา",
  รับราชการ: "ข้าราชการ",
  แม่บ้าน: "แม่บ้าน"
};

export default function RawData() {
  const demo = ds.dashboard.demographics;
  const total = demo.total;

  const genderData = Object.entries(demo.gender).map(([k, v]) => ({
    name: GENDER_LABELS[k] || k,
    value: v as number
  }));

  const ageOrder = ["ต่ำกว่า 18ปี", "18-22ปี", "23-29ปี", "30-39ปี", "40-49ปี", "50ปี ขึ้นไป"];
  const ageData = ageOrder
    .filter((k) => (demo.age_group as Record<string, number>)[k])
    .map((k) => ({
      name: AGE_LABELS[k] || k,
      value: (demo.age_group as Record<string, number>)[k]
    }));

  const occData = Object.entries(demo.occupation)
    .sort((a, b) => (b[1] as number) - (a[1] as number))
    .slice(0, 6)
    .map(([k, v]) => ({ name: OCC_LABELS[k] || k, value: v as number }));

  const [activeIdx, setActiveIdx] = useState(0);

  return (
    <section id="raw" className="py-24 md:py-32 relative">
      <div className="max-w-7xl mx-auto px-6">
        <SectionHeader
          index="01"
          kicker="ข้อมูลดิบ"
          title="เริ่มจากตัวเลขพวกนี้ก่อน"
          subtitle="เก็บข้อมูลจากแบบสอบถามภาษาไทย 76 ข้อผ่าน Google Forms ถามตั้งแต่ข้อมูลส่วนตัว พฤติกรรมเสพสื่อ 4 ช่องทาง ความชอบกาแฟ/ชาแบบเลือกคะแนน 1–5 ไปจนถึงจะลอง RTD ตัวใหม่ไหม ด้านล่างคือหน้าตาข้อมูลจริงๆ ที่ได้มา (ยังไม่ตบแต่งอะไรเลย)."
        />

        <div className="grid grid-cols-12 gap-6">
          <Card className="col-span-12 md:col-span-4">
            <div className="text-xs font-mono text-ink-2 tracking-widest uppercase mb-1">
              จำนวนคนตอบ
            </div>
            <div className="font-display text-6xl text-accent-gold font-bold">{total}</div>
            <p className="text-ink-1/85 mt-3 text-sm leading-relaxed">
              <span className="text-ink-0 font-medium">181 คนที่ตอบครบ</span> หลังจากตัด{" "}
              <span className="font-mono">3</span> แถวที่เว้นข้อมูลพื้นฐานทิ้ง.
              ไฟล์ดิบก่อนเคลียร์มี <span className="font-mono">200</span> แถว ×{" "}
              <span className="font-mono">76</span> คอลัมน์คำถาม.
            </p>
            <div className="mt-4 flex flex-wrap gap-2">
              <Pill>ภาษาไทย</Pill>
              <Pill color="#5BB89A">คะแนน 1–5</Pill>
              <Pill color="#8B7AD0">เลือกหลายข้อ</Pill>
            </div>
          </Card>

          <Card className="col-span-12 md:col-span-4">
            <div className="text-xs font-mono text-ink-2 tracking-widest uppercase mb-1">
              สัดส่วนเพศ
            </div>
            <div className="h-[180px]">
              <ResponsiveContainer>
                <PieChart>
                  <Pie
                    data={genderData}
                    dataKey="value"
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={75}
                    activeIndex={activeIdx}
                    onMouseEnter={(_, i) => setActiveIdx(i)}
                    activeShape={(props: any) => (
                      <g>
                        <Sector {...props} outerRadius={props.outerRadius + 6} />
                        <text
                          x={props.cx}
                          y={props.cy - 5}
                          textAnchor="middle"
                          fill="#F4EFE6"
                          className="font-display"
                          fontSize={22}
                        >
                          {props.payload.name}
                        </text>
                        <text
                          x={props.cx}
                          y={props.cy + 18}
                          textAnchor="middle"
                          fill="#E0A458"
                          className="font-mono"
                          fontSize={13}
                        >
                          {props.payload.value} · {((props.payload.value / total) * 100).toFixed(0)}%
                        </text>
                      </g>
                    )}
                  >
                    {genderData.map((_, i) => (
                      <Cell
                        key={i}
                        fill={["#E0A458", "#5BB89A", "#5C5547"][i % 3]}
                        stroke="rgba(0,0,0,0.4)"
                      />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            </div>
            <p className="text-xs text-ink-2 mt-2 leading-relaxed">
              ผู้หญิงเยอะกว่าเยอะ (
              <span className="font-mono text-ink-1">{demo.gender["หญิง"]}/{total}</span> ={" "}
              {((demo.gender["หญิง"] / total) * 100).toFixed(0)}%). เดี๋ยวพอถึงสรุปเราจะถ่วงน้ำหนัก
              และบอกตรงๆ ว่าข้อไหนเอียงไปทางหญิง.
            </p>
          </Card>

          <Card className="col-span-12 md:col-span-4">
            <div className="text-xs font-mono text-ink-2 tracking-widest uppercase mb-1">
              ช่วงอายุ
            </div>
            <div className="h-[180px]">
              <ResponsiveContainer>
                <BarChart data={ageData} margin={{ top: 6, right: 0, bottom: 0, left: -28 }}>
                  <CartesianGrid stroke="#252019" strokeDasharray="2 4" vertical={false} />
                  <XAxis
                    dataKey="name"
                    stroke="#9A917F"
                    tick={{ fontSize: 11, fill: "#9A917F" }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis stroke="#5C5547" tick={{ fontSize: 10, fill: "#5C5547" }} axisLine={false} tickLine={false} />
                  <Tooltip
                    cursor={{ fill: "rgba(224,164,88,0.06)" }}
                    contentStyle={{
                      background: "#13110D",
                      border: "1px solid rgba(224,164,88,0.3)",
                      borderRadius: 8,
                      fontSize: 12
                    }}
                  />
                  <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                    {ageData.map((d, i) => (
                      <Cell key={i} fill={i === 3 ? "#E0A458" : "#7A4520"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <p className="text-xs text-ink-2 mt-2 leading-relaxed">
              ช่วง <span className="text-accent-gold font-mono">30–39</span> มาเยอะสุดที่{" "}
              <span className="font-mono text-ink-1">{demo.age_group["30-39ปี"]}</span> คน (39%) —
              คือกลุ่มหลักที่เดินซื้อ RTD ใน 7-Eleven/โลตัส ตรงเป้าเลย.
            </p>
          </Card>

          <Card className="col-span-12 md:col-span-7">
            <div className="text-xs font-mono text-ink-2 tracking-widest uppercase mb-1">
              อาชีพยอดฮิต
            </div>
            <div className="h-[260px]">
              <ResponsiveContainer>
                <BarChart
                  data={occData}
                  layout="vertical"
                  margin={{ top: 6, right: 30, bottom: 0, left: 80 }}
                >
                  <CartesianGrid stroke="#252019" strokeDasharray="2 4" horizontal={false} />
                  <XAxis type="number" stroke="#5C5547" tick={{ fontSize: 11, fill: "#5C5547" }} axisLine={false} tickLine={false} />
                  <YAxis
                    dataKey="name"
                    type="category"
                    stroke="#9A917F"
                    tick={{ fontSize: 11, fill: "#D9D2C2" }}
                    axisLine={false}
                    tickLine={false}
                    width={120}
                  />
                  <Tooltip
                    cursor={{ fill: "rgba(224,164,88,0.05)" }}
                    contentStyle={{
                      background: "#13110D",
                      border: "1px solid rgba(224,164,88,0.3)",
                      borderRadius: 8,
                      fontSize: 12
                    }}
                  />
                  <Bar dataKey="value" radius={[0, 6, 6, 0]}>
                    {occData.map((_, i) => (
                      <Cell
                        key={i}
                        fill={`rgb(${224 - i * 18},${164 - i * 12},${88 + i * 6})`}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="col-span-12 md:col-span-5"
          >
            <Card className="h-full">
              <div className="text-xs font-mono text-ink-2 tracking-widest uppercase mb-3">
                "ดิบ" คือหน้าตาประมาณนี้
              </div>
              <div className="font-mono text-[11px] leading-6 text-ink-1/80 bg-bg-2 rounded-lg p-4 overflow-x-auto">
                <div className="text-ink-2"># แถวที่ 47</div>
                <div>
                  <span className="text-accent-gold">เพศ</span>: หญิง,{" "}
                  <span className="text-accent-gold">อายุ</span>: 34
                </div>
                <div>
                  <span className="text-accent-gold">อาชีพ</span>: พนักงานบริษัทเอกชน
                </div>
                <div>
                  <span className="text-accent-gold">รสชาติ...กาแฟสด</span>:{" "}
                  <span className="text-accent-cream">5</span>
                </div>
                <div>
                  <span className="text-accent-gold">บรรจุภัณฑ์</span>:{" "}
                  <span className="text-accent-cream">4</span>
                </div>
                <div>
                  <span className="text-accent-gold">RTD แบรนด์</span>:{" "}
                  Birdy, Boss, Nescafé...
                </div>
                <div>
                  <span className="text-accent-gold">ดื่มกาแฟ?</span>:{" "}
                  <span className="text-accent-jade">ใช่</span>
                </div>
              </div>
              <p className="text-xs text-ink-2 mt-3 leading-relaxed">
                ชื่อคอลัมน์ไทย/อังกฤษผสม, คำตอบเลือกหลายข้อเชื่อมด้วย ; , ยี่ห้อบางอันเขียนไทยบางอันอังกฤษ, มีช่องว่างบ้าง —
                ขั้นต่อไปคือเคลียร์ทั้งหมดนี้ให้เป็นระเบียบ.
              </p>
            </Card>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
