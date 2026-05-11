import clusterSupervised from "@/data/cluster_supervised.json";
import dashboardData from "@/data/dashboard_data.json";
import supervisedMetrics from "@/data/supervised_metrics.json";

export type ClusterSupervised = typeof clusterSupervised;
export type DashboardData = typeof dashboardData;
export type SupervisedMetrics = typeof supervisedMetrics;

export const ds = {
  clusterSupervised: clusterSupervised as ClusterSupervised,
  dashboard: dashboardData as DashboardData,
  metrics: supervisedMetrics as SupervisedMetrics
};

export const TARGET_CHOICES = [
  { key: "0", label: "ไม่ลอง", shortLabel: "ไม่ลอง", color: "#B91C1C" },
  { key: "1", label: "อาจจะลอง", shortLabel: "อาจจะ", color: "#C2410C" },
  { key: "2", label: "ลองแน่นอน", shortLabel: "ลอง", color: "#15803D" }
] as const;

export type TargetChoiceKey = (typeof TARGET_CHOICES)[number]["key"];

export const PERSONA = {
  0: {
    id: 0,
    code: "P0",
    name: "สายกาแฟตัวจริง",
    tagline: "กลุ่มหลัก ดื่มทุกวัน เน้นรสกับกลิ่น",
    color: "#C2410C",
    accent: "#9A3412",
    description:
      "ดื่มกาแฟประจำ ใส่ใจกลิ่นและรสเหมือนกาแฟสด ราคาไม่ได้แพ้รส คือกลุ่ม default ของ RTD เลย — ขายให้คนพวกนี้ก่อน.",
    iconLetter: "M"
  },
  1: {
    id: 1,
    code: "P1",
    name: "สายไม่กาแฟ",
    tagline: "ให้คะแนนทุกข้อต่ำกว่า 2 — ไม่ใช่กลุ่มเป้าหมาย",
    color: "#6D28D9",
    accent: "#4C1D95",
    description:
      "เกือบทุกคุณสมบัติของกาแฟ ให้คะแนนต่ำกว่า 2/5 หมด แปลว่าไม่ใช่ลูกค้ากาแฟ ใช้กลุ่มนี้ลองตลาดชา/wellness แทนจะคุ้มกว่า.",
    iconLetter: "S"
  },
  2: {
    id: 2,
    code: "P2",
    name: "สายพรีเมียม",
    tagline: "ใช้แบรนด์ + แพ็กเกจ + ความพรีเมียม เป็นสัญญาณคุณภาพ",
    color: "#15803D",
    accent: "#166534",
    description:
      "คะแนนแบรนด์ trust 4.5, แพ็กเกจ 4.5, premium feel 4.6 — ใช้ชื่อแบรนด์ ดีไซน์ขวด และความรู้สึกพรีเมียม เป็นเครื่องชี้ว่า ‘ของดีไหม’ ก่อนซื้อ. ไม่ใช่ลูกค้าประจำที่ผูกแบรนด์เดียว แต่เป็นคนเลือกของดีที่ยอมจ่ายเพิ่มถ้าเรื่องเล่าของ RTD แน่นพอ — เล่าจาก 4,000 สาขาเดิมได้สบาย.",
    iconLetter: "C"
  }
} as const;

export type PersonaKey = keyof typeof PERSONA;

export function fmtPct(n: number | null | undefined, digits = 0): string {
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  return `${(n * 100).toFixed(digits)}%`;
}
export function fmtNum(n: number, digits = 2): string {
  return n.toFixed(digits);
}
