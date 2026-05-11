import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "RTD Coffee Launch — แดชบอร์ดเข้าใจลูกค้า",
  description:
    "จาก 181 แถวแบบสอบถาม กลายเป็นแผนการตลาดที่บอกว่าควรคุยกับใคร พูดเรื่องอะไร และลงเงินที่ไหน"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
