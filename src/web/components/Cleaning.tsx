"use client";
import { motion } from "framer-motion";
import { ArrowRight, FileText, Languages, Filter, Tag, Hash } from "lucide-react";
import { Card, SectionHeader, Pill } from "./UI";

const STEPS = [
  {
    icon: Languages,
    title: "แปลชื่อคอลัมน์ไทย → อังกฤษ",
    metric: "76 → 76",
    sub: "เป็น snake_case",
    desc:
      "ชื่อคอลัมน์ไทยยาวๆ พิมพ์ผิดง่าย เราจับคู่เป็นภาษาอังกฤษสั้นๆ (เช่น ‘เพศ’ → gender, ‘บรรจุภัณฑ์’ → coffee_packaging) แล้วเก็บตารางคู่ไว้ที่ data/processed/column_mapping.json.",
    output: '{ "เพศ": "gender", "อายุ": "age", … อีก 74 }'
  },
  {
    icon: Filter,
    title: "ตัดคนที่กรอกไม่ครบทิ้ง",
    metric: "200 → 181",
    sub: "−19 คน (−9.5%)",
    desc:
      "ถ้าคนไหนไม่บอกเพศ/อายุ/อาชีพ พอจะ group by ทีหลังก็พังหมด เราเลยลบ 19 คนนี้ตั้งแต่ต้นให้ทุกกราฟใช้ N เท่ากัน. คะแนน Likert ที่เว้น โมเดลเติมให้ด้วยค่า median.",
    output: "df.dropna(subset=['gender','age','occupation'])"
  },
  {
    icon: Hash,
    title: "แปลงคะแนนเป็นตัวเลข",
    metric: "1–5 numeric",
    sub: "‘สำคัญที่สุด’ → 5",
    desc:
      "แบบสอบถามให้เลือก ‘สำคัญน้อย/ปานกลาง/มาก/มากที่สุด’ กับคุณสมบัติกาแฟ 13 ข้อ. แปลงเป็นเลข 1–5 จะได้เอาไปหาค่าเฉลี่ย/สหสัมพันธ์/ความสำคัญของฟีเจอร์ได้.",
    output: "{'สำคัญน้อย':1, 'ปานกลาง':3, 'สำคัญที่สุด':5}"
  },
  {
    icon: Tag,
    title: "แตกคำตอบเลือกหลายข้อ",
    metric: "+12 คอลัมน์ใหม่",
    sub: "‘FB; IG; TikTok’ → 3 คอลัมน์",
    desc:
      "คำถามเลือกหลายข้อมาเป็นสตริงคั่นด้วย ;. แตกให้เป็น 1 คอลัมน์ต่อ 1 ช่องทาง (social_FB, social_IG, social_TikTok) โมเดลจะได้เห็นน้ำหนักของแต่ละแพลตฟอร์มแยกกัน.",
    output: "df.assign(**{f'social_{k}': df.contains(k) for k in PLATFORMS})"
  },
  {
    icon: FileText,
    title: "สร้าง customer_segment",
    metric: "4 กลุ่ม",
    sub: "ใช้กฎง่ายๆ",
    desc:
      "จาก ดื่มกาแฟ × ดื่มชา × ซื้อ RTD เอามาคูณกันเป็นป้ายเดียว: Coffee-only / Tea-only / ทั้งคู่ / ไม่ดื่ม. ใช้ในสไลด์และแผนการตลาด อ่านเข้าใจง่ายกว่า cluster id ของ K-Means.",
    output: "Coffee-only · 64% · ทั้งคู่ · 22% · ไม่ดื่ม · 8%"
  },
  {
    icon: Hash,
    title: "สร้าง target 3 คลาส",
    metric: "118 คนที่ label ได้",
    sub: "0/1/2 = ไม่ลอง/อาจจะ/ลอง",
    desc:
      "เป้าของโมเดลมาจากคำถาม ‘จะลองดื่ม RTD ใหม่ไหม’: ‘ไม่ลอง’ → 0, มีเงื่อนไข/รอดูโปร/รีวิว → 1, ‘ลองเลย’ → 2. สัดส่วนคลาส 21/64/14 — ใช้ class_weight=‘balanced’ กันโมเดลเทไปหา ‘อาจจะ’.",
    output: "y = {'ไม่ลอง':0, 'อาจจะลอง':1, 'ลองแน่นอน':2}"
  }
];

export default function Cleaning() {
  return (
    <section id="clean" className="py-20 md:py-28 bg-bg-2/40">
      <div className="max-w-6xl mx-auto px-6">
        <SectionHeader
          index="02"
          kicker="กระบวนการเคลียร์"
          title="6 สเต็ปจากข้อมูลดิบสู่ตารางที่ใช้งานได้"
          subtitle="แต่ละสเต็ปวัดผลได้ว่า input กี่แถว output กี่แถว. ทั้ง pipeline reproduce ได้ — ลบ outputs/ แล้วรันใหม่ได้ไฟล์เดิม."
        />

        <div className="grid grid-cols-12 gap-5">
          {STEPS.map((s, i) => (
            <motion.div
              key={s.title}
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.35, delay: i * 0.04 }}
              className="col-span-12 md:col-span-6 lg:col-span-4"
            >
              <Card className="h-full hover-lift hover:border-accent-gold/40">
                <div className="flex items-start justify-between mb-3">
                  <div className="w-9 h-9 rounded-md bg-accent-cream flex items-center justify-center">
                    <s.icon size={16} className="text-accent-gold" />
                  </div>
                  <div className="text-right">
                    <div className="text-xl font-semibold text-accent-gold tabular">{s.metric}</div>
                    <div className="text-[10px] font-mono uppercase tracking-wider text-ink-2 mt-0.5">{s.sub}</div>
                  </div>
                </div>
                <div className="text-base font-semibold text-ink-0 mb-2 leading-snug">{s.title}</div>
                <p className="text-[13px] text-ink-2 leading-relaxed mb-4">{s.desc}</p>
                <div className="font-mono text-[11px] bg-bg-2 border border-ink-3/40 rounded px-3 py-2 text-ink-1 overflow-x-auto whitespace-nowrap">
                  {s.output}
                </div>
              </Card>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.4 }}
          className="mt-8"
        >
          <Card>
            <div className="grid grid-cols-12 gap-6 items-center">
              <div className="col-span-12 md:col-span-7">
                <div className="tag mb-2">สรุปผลของการเคลียร์</div>
                <div className="text-xl md:text-2xl leading-snug font-semibold text-ink-0">
                  จากคำถามไทยดิบ 76 ข้อ → <span className="text-accent-gold">120 คอลัมน์ที่ใช้ต่อได้</span> ใน 181 แถว.
                </div>
                <p className="mt-3 text-ink-2 max-w-xl text-sm leading-relaxed">
                  ใน 120 คอลัมน์: 13 ตัวเป็นคะแนน Likert (เทรนโมเดล), 28 ตัวเป็น multi-select (ดูการเข้าถึงสื่อ), 8 ตัวเป็นข้อมูลพื้นฐาน, 1 ตัวคือเป้า. ที่เหลือเป็นของ derived (cluster id, PCA, anomaly flag).
                </p>
                <div className="flex flex-wrap gap-2 mt-4">
                  <Pill color="#C2410C">13 Likert</Pill>
                  <Pill color="#15803D">28 multi-select</Pill>
                  <Pill color="#6D28D9">8 demographic</Pill>
                  <Pill color="#B91C1C">1 target · 3 choices</Pill>
                </div>
              </div>
              <div className="col-span-12 md:col-span-5">
                <div className="grid grid-cols-3 items-center gap-2">
                  <div className="text-center">
                    <div className="tag mb-2">ดิบ</div>
                    <div className="surface-muted p-4">
                      <div className="text-xl font-semibold text-ink-0 tabular">200</div>
                      <div className="text-[10px] text-ink-2 font-mono mt-0.5">แถว</div>
                      <div className="text-xl font-semibold text-ink-0 mt-2 tabular">76</div>
                      <div className="text-[10px] text-ink-2 font-mono mt-0.5">คอลัมน์</div>
                    </div>
                  </div>
                  <ArrowRight className="text-ink-3 mx-auto" size={18} />
                  <div className="text-center">
                    <div className="tag mb-2 text-accent-copper">เคลียร์แล้ว</div>
                    <div className="rounded-xl border border-accent-gold/40 bg-accent-cream/40 p-4">
                      <div className="text-xl font-semibold text-accent-gold tabular">181</div>
                      <div className="text-[10px] text-ink-2 font-mono mt-0.5">แถว</div>
                      <div className="text-xl font-semibold text-accent-gold mt-2 tabular">120</div>
                      <div className="text-[10px] text-ink-2 font-mono mt-0.5">คอลัมน์</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </motion.div>
      </div>
    </section>
  );
}
