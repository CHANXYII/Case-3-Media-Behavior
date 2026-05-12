"use client";
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

const FEATURES = [
  { feature: "ไม่มีแบรนด์ RTD ประจำ", fScore: 15.61, pValue: 1.0e-6, effect: "−21.6 จุดลองแน่", direction: -1, plain: "คนที่ตอบ ‘ไม่ดื่ม RTD เลย’ มีโอกาสอยู่คลาส ‘ลองแน่นอน’ ต่ำลง 22 จุด% และ ‘อาจจะลอง’ ต่ำลง 11 จุด." },
  { feature: "ราคาคุ้มไหม (1–5)", fScore: 7.87, pValue: 0.00062, effect: "+1.32 คะแนนเฉลี่ย", direction: 1, plain: "คนคลาส ‘ลองแน่นอน’ ให้คะแนนความคุ้มค่าสูงกว่าคนไม่ลอง 1.32 คะแนน — ตัวขับเชิงบวกแรงสุดของฝั่งตัวเลข." },
  { feature: "กลิ่นหอม", fScore: 6.81, pValue: 0.0016, effect: "+1.11 คะแนนเฉลี่ย", direction: 1, plain: "คนใส่ใจกลิ่นมีแนวโน้มขยับจากไม่ลองไปเป็น ‘ลองแน่นอน’ — กลิ่นตอนเปิดขวดเป็นสัญญาณคุณภาพที่แรง." },
  { feature: "RTD tea ประจำ = Orishi Gold", fScore: 6.77, pValue: 0.00166, effect: "+62.7 จุดลองแน่", direction: 1, plain: "กลุ่มที่มี RTD tea ประจำตอบ ‘ลองแน่นอน’ สูงกว่าเฉลี่ยมาก เป็นสัญญาณของคนชอบลองเครื่องดื่มพร้อมดื่มอยู่แล้ว." },
  { feature: "ใช้เน็ต 1–2 ชม./วัน", fScore: 6.64, pValue: 0.00187, effect: "+38.2 จุดลองแน่", direction: 1, plain: "กลุ่มใช้ออนไลน์ระดับเบาแยกตัวจากกลุ่ม ‘อาจจะ’ ชัด — segment เล็กที่ตอบ ‘ลองแน่นอน’ สูงกว่าค่าเฉลี่ย." },
  { feature: "ดีต่อสุขภาพ", fScore: 5.79, pValue: 0.00403, effect: "+1.16 คะแนนเฉลี่ย", direction: 1, plain: "สายสุขภาพยอมขยับจาก ‘อาจจะ’ ไป ‘ลองแน่นอน’ ถ้าฉลากบอกชัดว่า น้ำตาลน้อย/มีฟังก์ชันเสริม." },
  { feature: "รสนุ่มละมุน", fScore: 4.66, pValue: 0.01127, effect: "+1.03 คะแนนเฉลี่ย", direction: 1, plain: "สายนุ่มยังเป็นสัญญาณบวก แต่แรงรองจากราคา กลิ่น และ nutrition." },
  { feature: "ความน่าเชื่อถือของแบรนด์", fScore: 5.47, pValue: 0.00536, effect: "+0.96 คะแนนเฉลี่ย", direction: 1, plain: "‘ขอแบบหยิบเดินแล้วดื่มได้เลย’ ยังแยกคนลองแน่นอนออกจากคนไม่ลองได้ — value-prop ของ RTD ในเซเว่น." },
  { feature: "คาเฟอีน/ความดีด", fScore: 4.94, pValue: 0.00878, effect: "+1.19 คะแนนเฉลี่ย", direction: 1, plain: "คนที่ตอบ ‘ลองแน่นอน’ ให้คะแนนความดีดสูงกว่าคนไม่ลอง 1.19 คะแนน — ใช้กับข้อความตื่นตัว/พร้อมทำงานได้." }
];

const TIP = {
  contentStyle: {
    background: "#fff",
    border: "1px solid #e7e5e4",
    borderRadius: 8,
    fontSize: 12,
    boxShadow: "0 4px 6px -1px rgba(0,0,0,0.05)"
  }
};

export default function FeatureSelection() {
  const chartData = FEATURES.map((f) => ({ name: f.feature, fScore: f.fScore, direction: f.direction }));

  return (
    <section id="select" className="py-20 md:py-28">
      <div className="max-w-6xl mx-auto px-6">
        <SectionHeader
          index="03"
          kicker="คัดฟีเจอร์"
          title="คำถามไหนแยก 3 choice ได้จริง?"
          subtitle="มี 120 คอลัมน์ — โยนใส่หมดเลย overfit. เราใช้ ANOVA F-test ทุกฟีเจอร์เทียบกับ target 3 คลาส (ไม่ลอง / อาจจะ / ลองแน่นอน). F-score ตอบคำถาม ‘ค่าเฉลี่ยของ 3 กลุ่มห่างกันแค่ไหน’ ยิ่งสูงยิ่งสัญญาณชัด. เก็บเฉพาะ p ≤ 0.05."
        />

        <div className="grid grid-cols-12 gap-5">
          <Card className="col-span-12 lg:col-span-8">
            <div className="flex justify-between items-start mb-4">
              <div>
                <div className="tag">ANOVA F-score · Top 9</div>
                <div className="text-base mt-1 font-semibold text-ink-0">
                  ‘ไม่มีแบรนด์ RTD ประจำ’ เป็นสัญญาณลบแรงสุด
                </div>
              </div>
              <Pill color="#15803D">p &lt; 0.05 · ผ่านทุกตัว</Pill>
            </div>

            <div className="h-[440px]">
              <ResponsiveContainer>
                <BarChart data={chartData} layout="vertical" margin={{ top: 10, right: 30, bottom: 10, left: 130 }}>
                  <CartesianGrid stroke="#e7e5e4" strokeDasharray="2 4" horizontal={false} />
                  <XAxis type="number" stroke="#a8a29e" tick={{ fontSize: 10, fill: "#a8a29e" }} axisLine={false} tickLine={false} />
                  <YAxis type="category" dataKey="name" stroke="#a8a29e" tick={{ fontSize: 11, fill: "#292524" }} axisLine={false} tickLine={false} width={170} />
                  <Tooltip {...TIP} cursor={{ fill: "rgba(194,65,12,0.04)" }} formatter={(v: any) => [`F = ${Number(v).toFixed(2)}`, ""]} />
                  <ReferenceLine x={3.84} stroke="#B91C1C" strokeDasharray="3 3">
                    <text x={290} y={20} fill="#B91C1C" fontSize={10} fontFamily="monospace">F=3.84 · เส้น p=0.05</text>
                  </ReferenceLine>
                  <Bar dataKey="fScore" radius={[0, 4, 4, 0]}>
                    {chartData.map((d, i) => (
                      <Cell key={i} fill={d.direction === -1 ? "#B91C1C" : "#C2410C"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="mt-4 grid grid-cols-2 md:grid-cols-3 gap-3 text-xs text-ink-2">
              <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-sm bg-accent-gold" /> ตัวขับเชิงบวก</div>
              <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-sm bg-accent-ruby" /> ตัวขับเชิงลบ</div>
              <div className="flex items-center gap-2"><span className="w-3 h-0.5 bg-accent-ruby" /> เส้นนัยสำคัญ 5%</div>
            </div>
          </Card>

          <Card className="col-span-12 lg:col-span-4">
            <div className="tag mb-3">วิธีอ่านกราฟ</div>
            <ul className="space-y-4 text-[13px] text-ink-2 leading-relaxed">
              <li>
                <div className="text-ink-0 font-semibold text-sm mb-0.5">F-score</div>
                อัตราส่วนความแปรปรวนระหว่างกลุ่มต่อในกลุ่ม. ยิ่งใหญ่ = ค่าเฉลี่ย/สัดส่วนของ 3 กลุ่มห่างกันชัด.
              </li>
              <li>
                <div className="text-ink-0 font-semibold text-sm mb-0.5">p-value</div>
                ความน่าจะเป็นที่ F สูงขนาดนี้เกิดจากดวง. เก็บเฉพาะ <span className="font-mono">p ≤ 0.05</span> — โอกาสฟลุก &lt; 1 ใน 20.
              </li>
              <li>
                <div className="text-ink-0 font-semibold text-sm mb-0.5">Effect size</div>
                บอกในหน่วยจริง: หมวด → จุด%, ตัวเลข → คะแนน Likert. นักการตลาดหยิบใช้ต่อได้.
              </li>
              <li>
                <div className="text-ink-0 font-semibold text-sm mb-0.5">Top-K</div>
                dedupe ตาม source variable แล้วเก็บ <span className="font-mono">5</span> ตัวที่ F สูงสุด ส่งต่อไปเทรน Logistic Regression.
              </li>
            </ul>
          </Card>

          {FEATURES.slice(0, 6).map((f, i) => (
            <motion.div
              key={f.feature}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.3, delay: i * 0.03 }}
              className="col-span-12 md:col-span-6 lg:col-span-4"
            >
              <Card className="hover-lift h-full">
                <div className="flex items-start justify-between gap-3 mb-2">
                  <div className="text-[15px] font-semibold leading-snug text-ink-0">{f.feature}</div>
                  <div className="font-mono text-xs whitespace-nowrap" style={{ color: f.direction === 1 ? "#15803D" : "#B91C1C" }}>
                    {f.effect}
                  </div>
                </div>
                <div className="flex items-center gap-3 mb-3 text-xs font-mono text-ink-2 tabular">
                  <span>F={f.fScore.toFixed(2)}</span>
                  <span>p={f.pValue < 0.001 ? f.pValue.toExponential(1) : f.pValue.toFixed(4)}</span>
                </div>
                <p className="text-[13px] text-ink-2 leading-relaxed">{f.plain}</p>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
