"use client";
import { useState } from "react";
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
import { ds } from "@/lib/data";
import { Card, SectionHeader, Pill, Callout } from "./UI";
import { CountUp } from "./Motion";

const GENDER_LABELS: Record<string, string> = { หญิง: "หญิง", ชาย: "ชาย", ไม่ระบุ: "ไม่ระบุ" };
const AGE_LABELS: Record<string, string> = {
  "ต่ำกว่า 18ปี": "< 18",
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

const CHART_COLORS = ["#C2410C", "#15803D", "#A8A29E"];
const TIP = {
  contentStyle: {
    background: "#fff",
    border: "1px solid #e7e5e4",
    borderRadius: 8,
    fontSize: 12,
    boxShadow: "0 4px 6px -1px rgba(0,0,0,0.05)"
  }
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
    <section id="raw" className="py-20 md:py-28">
      <div className="max-w-6xl mx-auto px-6">
        <SectionHeader
          index="01"
          kicker="ข้อมูลดิบ"
          title="เริ่มจากข้อมูลพื้นฐานก่อน"
          subtitle="เก็บข้อมูลจากแบบสอบถามภาษาไทย 76 ข้อ ถามเรื่องข้อมูลส่วนตัว พฤติกรรมดูสื่อ ความชอบกาแฟ/ชา (ให้คะแนน 1-5) และจะลองกาแฟพร้อมดื่มตัวใหม่ไหม"
        />

        <div className="grid grid-cols-12 gap-5">
          <Card className="col-span-12 md:col-span-4">
            <div className="tag mb-2">จำนวนคนตอบ</div>
            <div className="text-5xl font-bold text-ink-0 tabular">
              <CountUp to={total} duration={1.5} />
            </div>
            <p className="text-ink-2 mt-3 text-sm leading-relaxed">
              <span className="text-ink-0 font-medium">181 คนที่ตอบครบ</span> หลังตัดแถวที่ข้อมูลไม่ครบออก
              ไฟล์ดิบตอนแรกมี <span className="font-mono text-ink-1">200</span> แถว × <span className="font-mono text-ink-1">76</span> คอลัมน์
            </p>
            <div className="mt-4 flex flex-wrap gap-2">
              <Pill>ภาษาไทย</Pill>
              <Pill color="#15803D">คะแนน 1–5</Pill>
              <Pill color="#6D28D9">เลือกหลายข้อ</Pill>
            </div>
          </Card>

          <Card className="col-span-12 md:col-span-4">
            <div className="tag mb-2">สัดส่วนเพศ</div>
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
                        <Sector {...props} outerRadius={props.outerRadius + 5} />
                        <text x={props.cx} y={props.cy - 6} textAnchor="middle" fill="#0C0A09" fontSize={18} fontWeight={600}>
                          {props.payload.name}
                        </text>
                        <text x={props.cx} y={props.cy + 14} textAnchor="middle" fill="#57534E" fontSize={12} className="font-mono">
                          {props.payload.value} · {((props.payload.value / total) * 100).toFixed(0)}%
                        </text>
                      </g>
                    )}
                  >
                    {genderData.map((_, i) => (
                      <Cell key={i} fill={CHART_COLORS[i % 3]} stroke="#fff" strokeWidth={2} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            </div>
            <p className="text-xs text-ink-2 mt-2 leading-relaxed">
              ผู้หญิงมากกว่า (<span className="font-mono text-ink-1">{demo.gender["หญิง"]}/{total}</span> คน หรือ {((demo.gender["หญิง"] / total) * 100).toFixed(0)}%)
            </p>
          </Card>

          <Card className="col-span-12 md:col-span-4">
            <div className="tag mb-2">ช่วงอายุ</div>
            <div className="h-[180px]">
              <ResponsiveContainer>
                <BarChart data={ageData} margin={{ top: 6, right: 0, bottom: 0, left: -28 }}>
                  <CartesianGrid stroke="#e7e5e4" strokeDasharray="2 4" vertical={false} />
                  <XAxis dataKey="name" stroke="#a8a29e" tick={{ fontSize: 11, fill: "#57534E" }} axisLine={false} tickLine={false} />
                  <YAxis stroke="#a8a29e" tick={{ fontSize: 10, fill: "#a8a29e" }} axisLine={false} tickLine={false} />
                  <Tooltip {...TIP} cursor={{ fill: "rgba(194,65,12,0.04)" }} />
                  <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                    {ageData.map((_, i) => (
                      <Cell key={i} fill={i === 3 ? "#C2410C" : "#E7E5E4"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <p className="text-xs text-ink-2 mt-2 leading-relaxed">
              อายุ <span className="font-mono text-accent-gold">30-39</span> มากที่สุด {demo.age_group["30-39ปี"]} คน (39%) ซึ่งเป็นกลุ่มหลักที่ซื้อกาแฟพร้อมดื่มในเซเว่น
            </p>
          </Card>

          <Card className="col-span-12 md:col-span-7">
            <div className="tag mb-2">อาชีพยอดฮิต</div>
            <div className="h-[240px]">
              <ResponsiveContainer>
                <BarChart data={occData} layout="vertical" margin={{ top: 6, right: 20, bottom: 0, left: 80 }}>
                  <CartesianGrid stroke="#e7e5e4" strokeDasharray="2 4" horizontal={false} />
                  <XAxis type="number" stroke="#a8a29e" tick={{ fontSize: 11, fill: "#a8a29e" }} axisLine={false} tickLine={false} />
                  <YAxis dataKey="name" type="category" stroke="#a8a29e" tick={{ fontSize: 11, fill: "#292524" }} axisLine={false} tickLine={false} width={120} />
                  <Tooltip {...TIP} cursor={{ fill: "rgba(194,65,12,0.04)" }} />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                    {occData.map((_, i) => (
                      <Cell key={i} fill={i === 0 ? "#C2410C" : "#d6d3d1"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>

          <Card className="col-span-12 md:col-span-5">
            <div className="tag mb-3">"ดิบ" คือหน้าตาประมาณนี้</div>
            <div className="font-mono text-[11px] leading-6 text-ink-1 bg-bg-2 rounded-lg p-4 overflow-x-auto">
              <div className="text-ink-3"># แถวที่ 47</div>
              <div><span className="text-accent-gold">เพศ</span>: หญิง, <span className="text-accent-gold">อายุ</span>: 34</div>
              <div><span className="text-accent-gold">อาชีพ</span>: พนักงานบริษัทเอกชน</div>
              <div><span className="text-accent-gold">รสชาติ...กาแฟสด</span>: <span className="text-accent-copper font-medium">5</span></div>
              <div><span className="text-accent-gold">บรรจุภัณฑ์</span>: <span className="text-accent-copper font-medium">4</span></div>
              <div><span className="text-accent-gold">RTD แบรนด์</span>: Birdy, Boss, Nescafé...</div>
              <div><span className="text-accent-gold">ดื่มกาแฟ?</span>: <span className="text-accent-jade">ใช่</span></div>
            </div>
            <Callout label="ก่อนไปต่อ">
              ชื่อคอลัมน์ไทย/อังกฤษผสม, คำตอบเลือกหลายข้อเชื่อมด้วย ; , ยี่ห้อไทย-อังกฤษปน — ขั้นต่อไปคือเคลียร์ทั้งหมดนี้.
            </Callout>
          </Card>
        </div>
      </div>
    </section>
  );
}
