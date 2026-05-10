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

export const PERSONA = {
  0: {
    id: 0,
    code: "P0",
    name: "สายกาแฟตัวจริง",
    tagline: "กลุ่มหลัก ดื่มทุกวัน เน้นรสกับกลิ่น",
    color: "#E0A458",
    accent: "#C77B3C",
    description:
      "ดื่มกาแฟประจำ ใส่ใจกลิ่นและรสเหมือนกาแฟสด ราคาไม่ได้แพ้รส คือกลุ่ม default ของ RTD เลย — ขายให้คนพวกนี้ก่อน.",
    iconLetter: "M"
  },
  1: {
    id: 1,
    code: "P1",
    name: "สายไม่กาแฟ",
    tagline: "ให้คะแนนทุกข้อต่ำกว่า 2 — ไม่ใช่กลุ่มเป้าหมาย",
    color: "#8B7AD0",
    accent: "#5C4FA3",
    description:
      "เกือบทุกคุณสมบัติของกาแฟ ให้คะแนนต่ำกว่า 2/5 หมด แปลว่าไม่ใช่ลูกค้ากาแฟ ใช้กลุ่มนี้ลองตลาดชา/wellness แทนจะคุ้มกว่า.",
    iconLetter: "S"
  },
  2: {
    id: 2,
    code: "P2",
    name: "สายพรีเมียม",
    tagline: "เน้นแบรนด์ + แพ็กเกจ + ความพรีเมียม",
    color: "#5BB89A",
    accent: "#2E8B72",
    description:
      "คะแนนแบรนด์ trust 4.5, แพ็กเกจ 4.5, premium feel 4.6. ยอมจ่ายเพิ่มถ้าเรื่องเล่าของ RTD แน่นพอ — เล่าจาก 4,000 สาขาเดิมได้สบาย.",
    iconLetter: "C"
  }
} as const;

export type PersonaKey = keyof typeof PERSONA;

export function fmtPct(n: number, digits = 0): string {
  return `${(n * 100).toFixed(digits)}%`;
}
export function fmtNum(n: number, digits = 2): string {
  return n.toFixed(digits);
}
