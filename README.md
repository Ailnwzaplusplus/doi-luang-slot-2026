# Doi Luang Chiang Dao Slot Availability Checker 2026

ระบบปฏิทินตรวจสอบที่ว่างหลุดจองดอยหลวงเชียงดาว + แจ้งเตือนผ่าน Telegram

## คุณสมบัติ
- ตรวจสอบคิวที่ว่างผ่าน API ของระบบจองดอยหลวงเชียงดาว
- หน้าเว็บแสดงปฏิทินแบบ Interactive อัปเดตสถานะแบบ Real-time
- เลือกระดับการเฝ้าแต่ละวันได้ (P0: ทุก 30 วินาที, P1: ทุก 60 วินาที)
- แจ้งเตือนทันทีผ่าน Telegram Bot เมื่อมีคิวว่าง
- รองรับการรันทั้งบน Local และ Deploy บน Cloud (Render, Railway, Fly.io, VPS)

## การติดตั้งและใช้งานบนเครื่องตนเอง (Local)

1. ติดตั้ง Python (>= 3.9)
2. ติดตั้ง Dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. รันโปรแกรม:
   ```bash
   python calendar_doiluang.py
   ```
4. เปิดเบราว์เซอร์ไปที่ `http://localhost:8000`

## การ Deploy บน Cloud / ใช้งานภายนอก (Online)

โปรแกรมรองรับ Environment Variables ต่อไปนี้สำหรับการรันบน Cloud:

| Environment Variable | รายละเอียด | ค่าเริ่มต้น |
|---|---|---|
| `PORT` | พอร์ตของ Web Server (Cloud ให้มาอัตโนมัติ) | `8000` |
| `HOST` | IP ที่ต้องการ Bind | `0.0.0.0` (หากรันบน Cloud) |
| `TELEGRAM_TOKEN` | Token บอท Telegram | ตั้งค่าในโค้ด |
| `TELEGRAM_CHAT_ID` | Telegram Chat ID สำหรับรับแจ้งเตือน | ตั้งค่าในโค้ด |
| `ADMIN_KEY` | รหัสเข้าใช้งานสำหรับแก้ไข/จัดการ | ตั้งค่าในโค้ด |
| `ALLOW_PHONE` | เปิดให้เครื่องอื่นในเครือข่ายเข้าดูได้ (`True`/`False`) | `False` |

### ตัวอย่างการ Deploy บน Render / Railway
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python calendar_doiluang.py`

