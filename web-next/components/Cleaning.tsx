"use client";
import { motion } from "framer-motion";
import { ArrowRight, FileText, Languages, Filter, Tag, Hash } from "lucide-react";
import { Card, SectionHeader, Pill } from "./UI";

const STEPS = [
  {
    icon: Languages,
    title: "แปลชื่อคอลัมน์ไทย → อังกฤษ",
    metric: "76 → 76",
    sub: "เป็น snake_case ใช้ต่อได้",
    desc:
      "ชื่อคอลัมน์ไทยยาวๆ เขียนยาก พิมพ์ผิดง่าย เราเลยจับคู่เป็นภาษาอังกฤษสั้นๆ (เช่น ‘เพศ’ → gender, ‘บรรจุภัณฑ์’ → coffee_packaging) แล้วเก็บตารางคู่ไว้ที่ data/processed/column_mapping.json เวลาทำสไลด์/โมเดล/แดชบอร์ด จะได้พูดภาษาเดียวกัน.",
    output: '{ "เพศ": "gender", "อายุ": "age", … อีก 74 }'
  },
  {
    icon: Filter,
    title: "ตัดคนที่กรอกไม่ครบทิ้ง",
    metric: "200 → 181",
    sub: "−19 คน (−9.5%)",
    desc:
      "ถ้าคนไหนไม่บอกเพศ/อายุ/อาชีพ พอจะ group by ทีหลังก็พังหมด เราเลยลบ 19 คนนี้ตั้งแต่ต้นให้ทุกกราฟใช้ N เท่ากัน. ส่วนคะแนน Likert ที่เว้น เราไม่ตัด — เดี๋ยวโมเดลเติมให้ด้วยค่า median.",
    output: "df.dropna(subset=['gender','age','occupation'])"
  },
  {
    icon: Hash,
    title: "แปลงคะแนนเป็นตัวเลข",
    metric: "1–5 numeric",
    sub: "‘สำคัญที่สุด’ → 5",
    desc:
      "แบบสอบถามให้เลือก ‘สำคัญน้อย/ปานกลาง/มาก/มากที่สุด’ กับคุณสมบัติกาแฟ 13 ข้อ เราเลยแปลงเป็นเลข 1-5 จะได้เอาไปหาค่าเฉลี่ย/สหสัมพันธ์/ความสำคัญของฟีเจอร์ได้. 5 แปลตรงตัวว่า ‘ข้อนี้สำคัญที่สุดตอนเลือก RTD’.",
    output: "{'สำคัญน้อย':1, 'ปานกลาง':3, 'สำคัญที่สุด':5}"
  },
  {
    icon: Tag,
    title: "แตกคำตอบเลือกหลายข้อ",
    metric: "+12 คอลัมน์ใหม่",
    sub: "‘FB; IG; TikTok’ → 3 คอลัมน์",
    desc:
      "คำถามเลือกหลายข้อมาเป็นสตริงยาวคั่นด้วย ;. เราแตกให้เป็น 1 คอลัมน์ต่อ 1 ช่องทาง (social_FB, social_IG, social_TikTok) โมเดลจะได้เห็นน้ำหนักของแต่ละแพลตฟอร์มแยกกัน ไม่ใช่มองว่า ‘FB; IG’ กับ ‘FB; TikTok’ เป็นคนละก้อนไปเลย.",
    output: "df.assign(**{f'social_{k}': df.contains(k) for k in PLATFORMS})"
  },
  {
    icon: FileText,
    title: "สร้าง customer_segment",
    metric: "4 กลุ่ม",
    sub: "ใช้กฎง่ายๆ",
    desc:
      "จาก ดื่มกาแฟ × ดื่มชา × ซื้อ RTD เราเอามาคูณกันเป็นป้ายเดียว: Coffee-only / Tea-only / ทั้งคู่ / ไม่ดื่ม. ไว้ใช้ในสไลด์และแผนการตลาด — เทียบได้กับ cluster id ของ K-Means แต่อ่านเข้าใจง่ายกว่า.",
    output: "Coffee-only · 64% · ทั้งคู่ · 22% · ไม่ดื่ม · 8%"
  },
  {
    icon: Hash,
    title: "สร้าง target_try_new_rtd_coffee",
    metric: "118 คนที่ label ได้",
    sub: "1 = จะลอง, 0 = ไม่ลอง",
    desc:
      "เป้าของโมเดลมาจากคำถาม ‘จะลองดื่ม RTD ใหม่ไหม’. เราแปลง: ‘ใช่/อาจจะ’ → 1, ‘ไม่’ → 0, เว้น → NaN (ตัดออกจากการเทรน). สัดส่วนคลาสคือ 79/21 — กลัวโมเดลเอียงเลยใส่ class_weight=‘balanced’ กันไว้.",
    output: "y = {'ใช่':1, 'อาจจะ':1, 'ไม่':0}"
  }
];

export default function Cleaning() {
  return (
    <section id="clean" className="py-24 md:py-32 relative">
      <div className="max-w-7xl mx-auto px-6">
        <SectionHeader
          index="02"
          kicker="กระบวนการเคลียร์"
          title="คำว่า ‘clean data’ จริงๆ คืออะไร? 6 สเต็ปนี่แหละ"
          subtitle="พูดคำว่า ‘เคลียร์ข้อมูล’ มันดูเบลอๆ. จริงๆ ในโปรเจกต์นี้มันคือ 6 สเต็ปตามลำดับ แต่ละสเต็ปวัดผลได้ว่า input กี่แถว output กี่แถว. ทั้ง pipeline reproduce ได้ — ลบโฟลเดอร์ outputs/ แล้วรันใหม่ได้ไฟล์เดิมเป๊ะๆ."
        />

        <div className="grid grid-cols-12 gap-6">
          {STEPS.map((s, i) => (
            <motion.div
              key={s.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.5, delay: i * 0.05 }}
              className="col-span-12 md:col-span-6 lg:col-span-4"
            >
              <Card className="h-full hover:border-accent-gold/30 transition-colors group">
                <div className="flex items-start justify-between mb-3">
                  <div className="w-10 h-10 rounded-lg bg-accent-gold/10 border border-accent-gold/30 flex items-center justify-center">
                    <s.icon size={18} className="text-accent-gold" />
                  </div>
                  <div className="text-right">
                    <div className="font-display text-2xl text-accent-gold">{s.metric}</div>
                    <div className="text-[10px] font-mono uppercase tracking-wider text-ink-2">
                      {s.sub}
                    </div>
                  </div>
                </div>
                <div className="font-display text-xl mb-2 leading-tight">{s.title}</div>
                <p className="text-sm text-ink-1/80 leading-relaxed mb-4">{s.desc}</p>
                <div className="font-mono text-[11px] bg-bg-2 rounded-md px-3 py-2 text-ink-1/70 overflow-x-auto whitespace-nowrap">
                  {s.output}
                </div>
              </Card>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="mt-12"
        >
          <Card>
            <div className="grid grid-cols-12 gap-6 items-center">
              <div className="col-span-12 md:col-span-7">
                <div className="text-xs font-mono text-ink-2 tracking-widest uppercase mb-2">
                  สรุปผลของการเคลียร์
                </div>
                <div className="font-display text-3xl md:text-4xl leading-tight font-bold">
                  จากคำถามไทยดิบ 76 ข้อ →{" "}
                  <span className="text-accent-gold">120 คอลัมน์ที่ใช้ต่อได้</span> ใน 181 แถว.
                </div>
                <p className="mt-3 text-ink-1/80 max-w-xl text-sm leading-relaxed">
                  ใน 120 คอลัมน์นี้ มี 13 ตัวเป็นคะแนน 1–5 (ใช้เทรนโมเดล), 28 ตัวเป็น
                  multi-select (ใช้ดูการเข้าถึงสื่อ), 8 ตัวเป็นข้อมูลพื้นฐาน, 1 ตัวคือเป้า. ที่เหลือเป็นของ
                  derived (cluster id, PCA, anomaly flag) ซึ่งจะโผล่มาตอน step unsupervised.
                </p>
                <div className="flex flex-wrap gap-2 mt-4">
                  <Pill>13 Likert</Pill>
                  <Pill color="#5BB89A">28 multi-select</Pill>
                  <Pill color="#8B7AD0">8 demographic</Pill>
                  <Pill color="#D85A5A">1 target</Pill>
                </div>
              </div>
              <div className="col-span-12 md:col-span-5">
                <div className="grid grid-cols-3 items-center gap-2 font-mono text-xs">
                  <div className="text-center">
                    <div className="text-ink-2 uppercase tracking-widest text-[10px] mb-2">ดิบ</div>
                    <div className="rounded-lg border border-white/10 p-4 bg-bg-2">
                      <div className="text-2xl font-display text-ink-0 font-bold">200</div>
                      <div className="text-[10px] text-ink-2 mt-1">แถว</div>
                      <div className="text-2xl font-display text-ink-0 mt-2 font-bold">76</div>
                      <div className="text-[10px] text-ink-2 mt-1">คอลัมน์</div>
                    </div>
                  </div>
                  <ArrowRight className="text-accent-gold mx-auto" size={20} />
                  <div className="text-center">
                    <div className="text-ink-2 uppercase tracking-widest text-[10px] mb-2">เคลียร์แล้ว</div>
                    <div className="rounded-lg border border-accent-gold/40 p-4 bg-accent-gold/5">
                      <div className="text-2xl font-display text-accent-gold font-bold">181</div>
                      <div className="text-[10px] text-ink-2 mt-1">แถว</div>
                      <div className="text-2xl font-display text-accent-gold mt-2 font-bold">120</div>
                      <div className="text-[10px] text-ink-2 mt-1">คอลัมน์</div>
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
