"use client";
import { Github } from "lucide-react";

export default function Footer() {
  return (
    <footer className="relative pt-16 pb-10">
      <div className="max-w-7xl mx-auto px-6">
        <div className="divider-grain mb-10" />
        <div className="grid grid-cols-12 gap-8">
          <div className="col-span-12 md:col-span-5">
            <div className="font-display text-3xl leading-tight font-semibold">
              จาก <span className="text-accent-gold">181 แถวข้อมูล</span> สู่แผนงบที่บวกแล้วได้ 100%
            </div>
            <p className="text-sm text-ink-2 mt-3 leading-relaxed max-w-md">
              ทุกกราฟในหน้านี้วาดจาก JSON ที่ออกมาจาก{" "}
              <span className="font-mono text-ink-1">run_pipeline.py</span> — ไม่มีรูปนิ่ง ไม่มี hardcode.
              รัน pipeline ใหม่ แดชบอร์ดอัปเดตตาม.
            </p>
          </div>
          <div className="col-span-6 md:col-span-3">
            <div className="text-xs font-mono text-ink-2 tracking-widest uppercase mb-3">
              สแตก
            </div>
            <ul className="space-y-1.5 text-sm text-ink-1/85 font-mono">
              <li>Next.js 14 · App Router</li>
              <li>Recharts (SVG ล้วน)</li>
              <li>Framer Motion</li>
              <li>Tailwind · IBM Plex Sans Thai</li>
              <li>Python · scikit-learn</li>
            </ul>
          </div>
          <div className="col-span-6 md:col-span-4">
            <div className="text-xs font-mono text-ink-2 tracking-widest uppercase mb-3">
              วิธีรันใหม่
            </div>
            <pre className="font-mono text-[11px] bg-bg-2 rounded-lg p-3 text-ink-1/85 leading-relaxed overflow-x-auto">
{`python -m src.data_cleaning.data_cleaning
python -m src.feature_engineering.feature_selection_visualization
python -m src.unsupervised.unsupervised_learning
python -m src.supervised.train
python -m src.supervised.per_cluster
cd web-next && npm run dev`}
            </pre>
          </div>
        </div>

        <div className="mt-10 flex flex-wrap items-center justify-between gap-4 text-xs text-ink-2 font-mono">
          <div>© Case 3 — พฤติกรรมสื่อ · บรีฟ launch RTD กาแฟ</div>
          <div className="flex items-center gap-4">
            <a
              href="https://github.com/"
              className="hover:text-accent-gold inline-flex items-center gap-1.5"
            >
              <Github size={13} /> source
            </a>
            <span>v1.0 · {new Date().getFullYear()}</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
