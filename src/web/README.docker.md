# Deploy

ทุกอย่างที่ต้องใช้สำหรับ deploy อยู่ในโฟลเดอร์นี้แล้ว — ไม่ต้องไปแตะไฟล์อื่นในรีโป

## รันคำสั่งเดียว

```bash
cd src/web
docker compose up -d --build
```

หรือใช้ npm script ที่ตั้งไว้ให้แล้ว:

```bash
cd src/web
npm run deploy
```

เปิดที่ <http://localhost:8236>

## คำสั่งที่ใช้บ่อย

```bash
docker compose logs -f web        # ดู log สด
docker compose ps                  # เช็คสถานะ + healthcheck
docker compose restart web        # รีสตาร์ท container
docker compose down                # หยุด + ลบ container
docker compose down --rmi all      # หยุด + ลบ image ด้วย
```

## โครงไฟล์ deploy

- `Dockerfile` — multi-stage (deps → build → runner) base image `node:20-alpine`, รัน Next.js แบบ `output: "standalone"` ขนาด image เล็ก ไม่มีไฟล์ dev
- `docker-compose.yml` — ผูก port 8236 ของ host ↔ 8236 ของ container, restart `unless-stopped`, healthcheck ทุก 30 วิ
- `.dockerignore` — ตัด `node_modules/`, `.next/`, `.git/` ออก ทำให้ build context เล็ก
- `next.config.js` — ตั้ง `output: "standalone"` เพื่อให้ runner stage copy แค่ไฟล์ที่จำเป็น

## เปลี่ยนพอร์ต

แก้ที่ `docker-compose.yml`:
```yaml
ports:
  - "PORT_HOST:8236"
```
container ภายในยังคงใช้ 8236 เหมือนเดิม
