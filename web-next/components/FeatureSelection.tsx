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
  {
    feature: "ไม่มีแบรนด์ RTD ประจำ",
    fScore: 22.48,
    pValue: 6.09e-6,
    effect: "−32.9 จุด try-rate",
    direction: -1,
    plain:
      "คนที่ตอบ ‘ไม่ดื่มกาแฟ Ready to drink เลย’ มีโอกาสลองตัวใหม่ต่ำลง 33 จุด% เทียบกับคนทั่วไป สัญญาณลบที่แรงสุดในทั้ง dataset."
  },
  {
    feature: "ราคาคุ้มไหม (1–5)",
    fScore: 15.47,
    pValue: 0.00014,
    effect: "+1.15 คะแนนเฉลี่ย",
    direction: 1,
    plain:
      "คนที่บอกว่า ‘คุ้มราคาสำคัญมาก’ ให้คะแนนสูงกว่าคนไม่ลองอยู่ 1.15 ตัวขับเชิงบวกที่แรงสุดของฝั่งตัวเลข."
  },
  {
    feature: "กลิ่นหอม",
    fScore: 12.67,
    pValue: 0.00054,
    effect: "+0.88 คะแนนเฉลี่ย",
    direction: 1,
    plain:
      "คนที่ใส่ใจกลิ่น มักจะลอง RTD ใหม่กว่า — เขาเชื่อกลิ่นตอนเปิดขวดเป็นตัวการันตีคุณภาพ."
  },
  {
    feature: "หยิบง่าย/พกง่าย",
    fScore: 10.8,
    pValue: 0.00134,
    effect: "+0.84 คะแนนเฉลี่ย",
    direction: 1,
    plain:
      "‘ขอแบบหยิบเดินแล้วดื่มได้เลย’ มี correlation สูงกับการลอง — ก็คือ value-prop ของ RTD ในเซเว่นเป๊ะๆ."
  },
  {
    feature: "ดีต่อสุขภาพ",
    fScore: 10.22,
    pValue: 0.0018,
    effect: "+0.86 คะแนนเฉลี่ย",
    direction: 1,
    plain:
      "สายสุขภาพยอมลองถ้าฉลากบอกชัดว่า น้ำตาลน้อย/มีฟังก์ชันเสริม."
  },
  {
    feature: "ใช้เน็ตเกิน 6 ชม./วัน",
    fScore: 9.02,
    pValue: 0.00328,
    effect: "+22.3 จุด try-rate",
    direction: 1,
    plain:
      "คนติดเน็ตหนักมีโอกาสลองสูงกว่า 22 จุด — เห็นโฆษณาบน TikTok/IG ก่อน แล้ว friction การซื้อก็ต่ำ."
  },
  {
    feature: "รสนุ่มละมุน",
    fScore: 8.15,
    pValue: 0.0051,
    effect: "+0.76 คะแนนเฉลี่ย",
    direction: 1,
    plain:
      "สายนุ่มชอบ RTD แมส (ไม่เปรี้ยวมาก) ข้อมูลนี้ส่งต่อให้ R&D ได้เลย."
  },
  {
    feature: "ความน่าเชื่อถือของแบรนด์",
    fScore: 7.26,
    pValue: 0.0081,
    effect: "+0.74 คะแนนเฉลี่ย",
    direction: 1,
    plain:
      "ยิ่งใส่ใจแบรนด์ ยิ่งลอง — งั้นใช้ทุนเก่าจาก 4,000 สาขามาเล่าต่อคือทางถูก."
  },
  {
    feature: "พรีเซนเตอร์มีผล",
    fScore: 6.68,
    pValue: 0.011,
    effect: "+19.6 จุด try-rate",
    direction: 1,
    plain:
      "คนที่ยอมรับว่า ‘ใช่ พรีเซนเตอร์มีผลกับฉันแหละ’ มี try-rate สูงกว่า 20 จุด ใช้ดารา/influencer ได้คุ้ม."
  }
];

export default function FeatureSelection() {
  const chartData = FEATURES.map((f) => ({
    name: f.feature,
    fScore: f.fScore,
    direction: f.direction
  }));

  return (
    <section id="select" className="py-24 md:py-32 relative">
      <div className="max-w-7xl mx-auto px-6">
        <SectionHeader
          index="03"
          kicker="คัดฟีเจอร์"
          title="คำถามไหนทำนายว่าจะลองได้จริง?"
          subtitle="มี 120 คอลัมน์ ถ้าโยนใส่โมเดลหมดเลยจะ overfit แล้วของไม่เกี่ยวก็โผล่มา (เช่น ‘ระดับรายได้’ ที่จริงๆ คือ ‘ช่วงอายุ’ ปลอมตัวมา). เราเลย ANOVA F-test ทุกฟีเจอร์ตัวเลขเทียบกับ target. F-score ตอบคำถาม ‘ค่าเฉลี่ยของกลุ่มคนที่จะลอง vs จะไม่ลอง ห่างกันแค่ไหน?’ — ยิ่งสูงยิ่งสัญญาณชัด. p-value < 0.05 แปลว่า โอกาสที่ความต่างนี่จะเกิดจากดวงน้อยกว่า 5%."
        />

        <div className="grid grid-cols-12 gap-6">
          <Card className="col-span-12 lg:col-span-8">
            <div className="flex justify-between items-center mb-4">
              <div>
                <div className="text-xs font-mono text-ink-2 tracking-widest uppercase">
                  ANOVA F-score · Top 9 ฟีเจอร์
                </div>
                <div className="font-display text-xl mt-1 font-semibold">
                  ‘ไม่มีแบรนด์ RTD ประจำ’ ทิ้งห่างที่ 1 ไป 1.5×
                </div>
              </div>
              <Pill>p &lt; 0.05 · ผ่านทุกตัว</Pill>
            </div>

            <div className="h-[460px]">
              <ResponsiveContainer>
                <BarChart
                  data={chartData}
                  layout="vertical"
                  margin={{ top: 10, right: 30, bottom: 10, left: 130 }}
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
                    dataKey="name"
                    stroke="#9A917F"
                    tick={{ fontSize: 11, fill: "#D9D2C2" }}
                    axisLine={false}
                    tickLine={false}
                    width={170}
                  />
                  <Tooltip
                    cursor={{ fill: "rgba(224,164,88,0.05)" }}
                    contentStyle={{
                      background: "#13110D",
                      border: "1px solid rgba(224,164,88,0.3)",
                      borderRadius: 8,
                      fontSize: 12
                    }}
                    formatter={(v: any) => [`F = ${Number(v).toFixed(2)}`, ""]}
                  />
                  <ReferenceLine x={3.84} stroke="#D85A5A" strokeDasharray="3 3">
                    <text x={290} y={20} fill="#D85A5A" fontSize={10} fontFamily="monospace">
                      F=3.84 · เส้น p=0.05
                    </text>
                  </ReferenceLine>
                  <Bar dataKey="fScore" radius={[0, 6, 6, 0]}>
                    {chartData.map((d, i) => (
                      <Cell key={i} fill={d.direction === -1 ? "#D85A5A" : "#E0A458"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="mt-4 grid grid-cols-2 md:grid-cols-3 gap-3 text-xs">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded bg-accent-gold" /> ตัวขับเชิงบวก
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded bg-accent-ruby" /> ตัวขับเชิงลบ
              </div>
              <div className="flex items-center gap-2 text-ink-2">
                <span className="w-3 h-0.5 bg-accent-ruby" /> เส้นนัยสำคัญ 5%
              </div>
            </div>
          </Card>

          <Card className="col-span-12 lg:col-span-4">
            <div className="text-xs font-mono text-ink-2 tracking-widest uppercase mb-3">
              วิธีอ่านกราฟ
            </div>
            <ul className="space-y-4 text-sm text-ink-1/85 leading-relaxed">
              <li>
                <span className="text-accent-gold font-mono mr-2">F-score</span>
                อัตราส่วนของความแปรปรวนระหว่างกลุ่มต่อในกลุ่ม. ยิ่งใหญ่แปลว่ากลุ่มจะลอง vs จะไม่ลอง
                ค่าเฉลี่ยห่างกันชัดมาก.
              </li>
              <li>
                <span className="text-accent-gold font-mono mr-2">p-value</span>
                ความน่าจะเป็นที่ F สูงขนาดนี้เกิดจากความบังเอิญ. เราเก็บเฉพาะ{" "}
                <span className="font-mono">p ≤ 0.05</span> — โอกาสฟลุก &lt; 1 ใน 20.
              </li>
              <li>
                <span className="text-accent-gold font-mono mr-2">Effect size</span>
                เราบอกในหน่วยจริงของฟีเจอร์: ถ้าเป็นหมวดให้เป็นจุด% ถ้าเป็นตัวเลขให้เป็นคะแนน Likert.
                นักการตลาดจะหยิบไปใช้ต่อได้เลย.
              </li>
              <li>
                <span className="text-accent-gold font-mono mr-2">Top-K</span>
                เสร็จแล้ว dedupe ตาม source variable แล้วเก็บ{" "}
                <span className="font-mono">5</span> ตัวที่ F สูงสุด ส่งต่อไปเทรน Logistic Regression
                / Random Forest / Gradient Boosting.
              </li>
            </ul>
          </Card>

          {FEATURES.slice(0, 6).map((f, i) => (
            <motion.div
              key={f.feature}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.04 }}
              className="col-span-12 md:col-span-6 lg:col-span-4"
            >
              <Card>
                <div className="flex items-center justify-between mb-2">
                  <div className="font-display text-lg leading-tight">{f.feature}</div>
                  <div
                    className="font-mono text-sm"
                    style={{ color: f.direction === 1 ? "#5BB89A" : "#D85A5A" }}
                  >
                    {f.effect}
                  </div>
                </div>
                <div className="flex items-center gap-3 mb-3 text-xs font-mono text-ink-2">
                  <span>F={f.fScore.toFixed(2)}</span>
                  <span>p={f.pValue < 0.001 ? f.pValue.toExponential(1) : f.pValue.toFixed(4)}</span>
                </div>
                <p className="text-sm text-ink-1/80 leading-relaxed">{f.plain}</p>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
