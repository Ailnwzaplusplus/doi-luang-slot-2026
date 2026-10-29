# คู่มือเฝ้าที่ว่าง (หลุดจอง) ดอยหลวงเชียงดาว

ไฟล์นี้รวมทุกอย่างที่ต้องใช้ย้ายไปรันบนเครื่องอื่น: วิธีติดตั้ง วิธีตั้งค่า โค้ดโปรแกรมฉบับเต็ม ปุ่มกรอกฟอร์มอัตโนมัติ และขั้นตอนจองตอนได้รับแจ้งเตือน

> ⚠️ ไฟล์นี้มี **Telegram token** ของบอทอยู่ในโค้ด อย่าแชร์ให้คนอื่น ถ้ากังวลว่าหลุด ให้พิมพ์ `/revoke` กับ @BotFather เพื่อขอ token ใหม่ แล้วแก้ในโค้ด

---

## 1. ข้อมูลสำคัญของระบบจอง

| หัวข้อ | รายละเอียด |
|---|---|
| เว็บจอง | https://q.wildlifesanctuaryfca16.com |
| ระบบเปิดรับจอง | 26 ต.ค. 2569 08:00 ถึง **30 ต.ค. 2569 16:00** เท่านั้น |
| วันที่เลือกเดินได้ | 16 พ.ย. 2569 ถึง 12 ก.พ. 2570 |
| วันที่จองไม่ได้ | วันพุธทุกสัปดาห์ |
| จำนวนคนต่อการจอง | สูงสุด 2 คน (ทั้งวันจำกัด 100 คน) |
| อบรมก่อนเดิน | 1 วันก่อนวันเดิน เวลา 09:00–12:00 ที่วัดถ้ำเชียงดาว |
| รหัสจองจากอีเมล | ใช้ได้ **30 นาที** หลังขอรหัส |
| ส่งเอกสาร + ชำระเงิน | ภายใน **6 ชั่วโมง** หลังลงทะเบียน ไม่งั้นใบจองเป็นโมฆะ |

**API ที่สคริปต์ใช้ (ไม่ต้องล็อกอิน)**

```
GET https://q.wildlifesanctuaryfca16.com/api/v1/bookings/availability?date=2027-01-23
```
ตอบกลับเป็น `{"success":true,"data":{"date":"2027-01-23","capacity":100,"available":0},"meta":null}`

ระบบไม่มี API แบบรายเดือน ต้องเช็กทีละวันเท่านั้น

**ที่หลุดมักมาจาก** รหัสจองที่ขอแล้วไม่ใช้ (หมดอายุใน 30 นาที) และใบจองที่ไม่จ่ายเงินหรือไม่ส่งเอกสารภายใน 6 ชั่วโมง

---

## 2. ติดตั้งบนเครื่องใหม่ (Windows)

### 2.1 ติดตั้ง Python
1. เข้า https://www.python.org/downloads/ แล้วดาวน์โหลดเวอร์ชันล่าสุด
2. ตอนติดตั้ง **ติ๊กช่อง "Add python.exe to PATH"** ก่อนกด Install Now
3. เปิด PowerShell แล้วพิมพ์ `python --version` ถ้าขึ้นเลขเวอร์ชันแปลว่าพร้อม

### 2.2 ติดตั้งไลบรารี
```
pip install requests
```

### 2.3 สร้างไฟล์โปรแกรม
1. สร้างโฟลเดอร์ เช่น `D:\จองเทพ`
2. เปิด Notepad แล้ววางโค้ดทั้งหมดจาก **หัวข้อ 8** ของไฟล์นี้
3. กด **File > Save As**
   - Save as type: **All Files (\*.\*)**
   - File name: `calendar_doiluang.py`
   - Encoding: **UTF-8**
4. ตรวจด้วยคำสั่ง `dir` ในโฟลเดอร์นั้นว่าชื่อไฟล์ไม่ใช่ `calendar_doiluang.py.txt`

(ถ้ามีไฟล์ `calendar_doiluang.py` จากเครื่องเดิมอยู่แล้ว ก๊อปไปวางได้เลย ไม่ต้องสร้างใหม่ ถ้าอยากเก็บวันที่เฝ้าเดิมไว้ด้วย ก๊อปไฟล์ `watch_dates.json` ไปด้วย)

### 2.4 ปิดโหมด Sleep
Settings > System > Power > "When plugged in, put my device to sleep after" ตั้งเป็น **Never** ถ้าคอมหลับ สคริปต์จะหยุดเช็ก

---

## 3. ตั้งค่า

แก้ในส่วน `ตั้งค่า (แก้ตรงนี้)` ด้านบนของไฟล์

| ค่า | ค่าเริ่มต้น | ความหมาย |
|---|---|---|
| `PEOPLE` | `1` | แจ้งเตือนเมื่อที่ว่าง ≥ จำนวนนี้ (สูงสุด 2) |
| `SCAN_WEEKDAYS` | `[0, 1, 3, 4, 5, 6]` | วันในสัปดาห์ที่เช็กบนปฏิทิน 0=จันทร์ … 6=อาทิตย์ เช่น ศุกร์–อาทิตย์ = `[4, 5, 6]` |
| `P0_SEC` | `30` | วันที่เฝ้าระดับ P0 (ด่วน) เช็กทุกกี่วินาที |
| `P1_SEC` | `60` | วันที่เฝ้าระดับ P1 เช็กทุกกี่วินาที |
| `FULL_REFRESH_MIN` | `10` | วันอื่นในปฏิทิน เช็กทุกกี่นาที |
| `RATE_PER_MIN` | `30` | งบคำขอสูงสุดต่อนาที ระบบจะไม่ยิงเกินนี้ ไม่ควรตั้งเกิน 30 |
| `COOLDOWN_MIN` | `5` | แจ้งซ้ำเมื่อที่ว่างเพิ่มขึ้น ได้ไม่ถี่กว่านี้ต่อวัน |
| `HEARTBEAT_HOURS` | `6` | ส่งข้อความ "ยังเฝ้าอยู่" ทุกกี่ชั่วโมง |
| `DEFAULT_WATCH` | 23, 24, 30, 31 ม.ค. 2570 ระดับ P1 | วันที่เฝ้าตอนรันครั้งแรก (หลังจากนั้นคลิกบนปฏิทินได้) |
| `TELEGRAM_TOKEN` / `TELEGRAM_CHAT_ID` | ของบอท Jonglnwwbot | ช่องทางแจ้งเตือน |
| `PORT` | `8000` | ถ้าเปิดหน้าเว็บไม่ได้เพราะพอร์ตชน ให้เปลี่ยนเป็น `8080` |

**งบคำขอ:** ทุก P0 ใช้ 2 คำขอ/นาที, P1 ใช้ 1, วันอื่นรวมกันประมาณ 7–8 ถ้ารวมแล้วเกิน `RATE_PER_MIN` หน้าเว็บจะขึ้นคำเตือน และวันที่ไม่ได้เฝ้าจะถูกเช็กช้าลงเอง แนะนำ P0 ไม่เกิน 5 วัน และ P1 ไม่เกิน 10 วัน

---

## 4. วิธีรันและใช้งาน

```
cd D:\จองเทพ
python calendar_doiluang.py
```

- เบราว์เซอร์จะเปิด `http://localhost:8000` ให้เอง (ถ้าไม่เปิด พิมพ์เองได้)
- Telegram จะได้ข้อความ "เริ่มเฝ้าที่ว่าง… v2" แปลว่าระบบแจ้งเตือนใช้ได้
- ช่องที่มีที่ว่างจะมีปุ่ม **"จอง →"** เปิดเว็บจองพร้อมวันที่ (ใช้คู่กับปุ่ม bookmarklet ในหัวข้อ 6)
- **คลิกวันที่บนปฏิทินเพื่อวนระดับ:** ไม่เฝ้า → **P1** (กรอบแดง, ทุก 1 นาที) → **P0** (กรอบม่วงหนา, ทุก 30 วินาที) → ไม่เฝ้า และระบบจะเช็กวันนั้นทันทีที่คลิก
- สีเขียว = ว่างพอสำหรับคุณ, สีเหลือง = ว่างบ้างแต่ไม่พอ, สีเทา = เต็ม
- ด้านบนมี**นับถอยหลังเวลาปิดรับจอง** และจำนวนคำขอที่ใช้จริงต่อนาที
- หน้าเว็บอัปเดตเองทุก 3 วินาที
- ห้ามปิดหน้าต่าง PowerShell (ย่อได้) หยุดโปรแกรมด้วย **Ctrl + C**
- ระบบหยุดเช็กเองตอน 30 ต.ค. 2569 16:00 และส่งข้อความบอกใน Telegram

**ลำดับการเช็ก:** วันที่เพิ่งคลิก → P0 ที่ถึงคิว → P1 ที่ถึงคิว → วันอื่นในปฏิทิน

**แจ้งเตือนที่จะได้รับ (เฉพาะวันที่เฝ้า)**
- มีที่ว่างถึงจำนวนที่ต้องการ (แจ้งทันที)
- ที่ว่างเพิ่มขึ้นอีก (ไม่ถี่กว่าทุก 5 นาที)
- กลับมาเต็มแล้ว
- เช็กไม่สำเร็จติดกัน 5 ครั้ง (ระบบชะลอเองอัตโนมัติ) และเมื่อกลับมาปกติ
- "ยังเฝ้าอยู่" ทุก 6 ชั่วโมง

**ไฟล์ที่ระบบสร้างในโฟลเดอร์เดียวกัน**
- `watch_dates.json` วันที่เฝ้าและระดับ (ก๊อปไปเครื่องอื่นได้)
- `events.csv` ประวัติทุกครั้งที่ที่ว่างเปลี่ยน เปิดด้วย Excel ดูได้ว่ามักหลุดช่วงเวลาไหน

---

## 5. Telegram

- บอท: t.me/Jonglnwwbot
- chat_id: `<CHAT_ID>`
- ถ้าเปลี่ยนเครื่องแล้วไม่ได้รับข้อความ ให้เปิดแชทกับบอทในแอป Telegram แล้วกด Start ใหม่
- ขอ chat_id ใหม่: ส่งข้อความหาบอท แล้วเปิด `https://api.telegram.org/bot<TOKEN>/getUpdates` หาตัวเลขหลัง `"chat":{"id":`

---

## 6. ปุ่ม "จองเลย" (Bookmarklet)

กดปุ่มเดียวบนเว็บจอง ระบบจะติ๊กข้อตกลง กดถัดไป เลือกวันบนปฏิทิน เลือกจำนวนคน กดยอมรับ และกรอกชื่อ นามสกุล เลขบัตร เบอร์ และอีเมลให้ จนเหลือแค่ **ติ๊ก reCAPTCHA กับกดยืนยันเอง**

1. Chrome กด **Ctrl + Shift + B** เปิดแถบบุ๊กมาร์ก
2. คลิกขวาที่แถบ > **Add page**
3. Name: `จองเลย`
4. URL: วางโค้ดด้านล่าง (หรือจากไฟล์ `bookmarklet_jong.txt`) **แก้ 5 ค่าในบรรทัดแรก `const ME={...}` เป็นข้อมูลจริงก่อน**

```
javascript:(async()=>{const ME={"ชื่อ":"ชื่อจริง","นามสกุล":"นามสกุลจริง","เลขบัตรประชาชน":"1234567890123","เบอร์โทรศัพท์":"0812345678","อีเมล":"you@gmail.com"};const sleep=ms=>new Promise(r=>setTimeout(r,ms));const vis=el=>!!el&&el.offsetParent!==null;const clickNext=()=>{const b=[...document.querySelectorAll("button")].find(x=>vis(x)&&!x.disabled&&x.textContent.trim()==="ถัดไป");if(b)b.click();return !!b;};const waitIdle=async()=>{await sleep(400);for(let i=0;i<60;i++){if(!document.getElementById("NotiflixLoadingWrap"))break;await sleep(100);}await sleep(300);};const h=new URLSearchParams(location.hash.slice(1));const ds=h.get("d")||prompt("วันที่ต้องการ (ค.ศ. ปี-เดือน-วัน)","2027-01-23");if(!ds)return;const n=h.get("n")||prompt("จำนวนคน (1 หรือ 2)","2");if(!n)return;const p=ds.split("-").map(Number);const dt=new Date(p[0],p[1]-1,p[2]);const labels=["th-TH","en-US"].map(l=>dt.toLocaleDateString(l,{day:"numeric",month:"long",year:"numeric"}));for(let step=0;step<12;step++){const c1=document.getElementById("flexCheckDefault");const c2=document.getElementById("flexCheckDefault2");if(vis(c1)){if(!c1.checked)c1.click();await sleep(250);clickNext();await sleep(500);continue;}if(vis(c2)){if(!c2.checked)c2.click();await sleep(250);clickNext();await sleep(500);continue;}const cal=document.querySelector(".react-calendar");if(vis(cal)){let tile=null;for(let k=0;k<8&&!tile;k++){const ab=[...cal.querySelectorAll("abbr")].find(a=>labels.includes(a.getAttribute("aria-label")));if(ab&&ab.closest("button")&&!ab.closest("button").disabled){tile=ab.closest("button");}else{const nb=cal.querySelector(".react-calendar__navigation__next-button");if(!nb||nb.disabled)break;nb.click();await sleep(300);}}if(!tile){alert("หาวันที่ "+ds+" บนปฏิทินไม่เจอ หรือวันนั้นจองไม่ได้");return;}tile.click();await waitIdle();const dd=[...document.querySelectorAll("div.cursor-pointer")].find(e=>vis(e)&&e.querySelector("svg")&&/(เลือกจำนวนคน|\d+ คน)$/.test(e.textContent.trim()));if(!dd){alert("หาช่องเลือกจำนวนคนไม่เจอ");return;}if(dd.textContent.trim()!==n+" คน"){dd.click();await sleep(300);const opt=[...document.querySelectorAll("div")].find(e=>vis(e)&&e.children.length===0&&e.textContent.trim()===n+" คน"&&e!==dd.firstElementChild);if(!opt){alert("วันที่ "+ds+" ที่ว่างไม่พอสำหรับ "+n+" คน");return;}opt.click();await sleep(300);}if(!clickNext()){alert("กดถัดไปไม่ได้ วันนั้นอาจเต็มแล้ว");return;}await sleep(500);const ok=[...document.querySelectorAll("button")].find(x=>vis(x)&&x.textContent.trim()==="ยอมรับ");if(ok)ok.click();await sleep(600);continue;}const nameEl=document.getElementById("ชื่อ");if(vis(nameEl)){const set=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,"value").set;for(const [k,v] of Object.entries(ME)){const el=document.getElementById(k);if(el){set.call(el,v);el.dispatchEvent(new Event("input",{bubbles:true}));}}const cap=document.querySelector('iframe[title*="reCAPTCHA"]');if(cap)cap.scrollIntoView({block:"center"});return;}await sleep(400);}alert("ไม่พบขั้นตอนการจองบนหน้านี้ ระบบอาจปิดอยู่ หรือหน้าเว็บเปลี่ยนไป");})();
```

**ปุ่มรู้ได้ยังไงว่าจะจองวันไหน**
- ถ้าเปิดเว็บจองจากปุ่ม **"จอง →"** บนปฏิทินของเรา หรือจากลิงก์ใน Telegram ลิงก์จะมี `#d=2027-01-23&n=1` ต่อท้าย ปุ่มจะอ่านวันที่และจำนวนคนจากตรงนั้นเอง
- ถ้าเปิดเว็บจองเอง ปุ่มจะถามวันที่ (ปี ค.ศ.) และจำนวนคน

**ข้อควรรู้**
- หน้าเว็บต้องเป็นภาษา **TH**
- กดปุ่มได้จากทุกขั้น ปุ่มจะเริ่มต่อจากขั้นที่เปิดค้างอยู่
- ถ้าที่ว่างไม่พอ วันจองไม่ได้ หรือระบบปิด จะมีกล่องข้อความบอก
- **ทดสอบปุ่มก่อนวันจริง** โดยเลือกวันที่ยังว่างแล้วกดปุ่ม เมื่อขึ้นหน้ากรอกพร้อมข้อมูลครบแล้วก็พอ **ไม่ต้องติ๊ก reCAPTCHA หรือกดยืนยัน**

---

## 7. ขั้นตอนเมื่อได้รับแจ้งเตือน

**เตรียมไว้ก่อน**
- ล็อกอิน Google ใน Chrome ไว้ (reCAPTCHA จะผ่านง่ายขึ้น)
- เตรียมข้อมูล**ทั้ง 2 คน**: ชื่อ นามสกุล เลขบัตร เบอร์ วันเกิด อีเมล
- เตรียมไฟล์รูปบัตรประชาชน และใบขอเข้าเขตที่กรอกแล้ว ไว้ในโฟลเดอร์เดียว
- ทำอบรมออนไลน์ให้เสร็จก่อน: https://cmu.to/chiangdao101

**ตอนได้แจ้งเตือน (ประมาณ 20 วินาที)**
1. กดลิงก์ใน Telegram หรือกด **"จอง →"** บนปฏิทิน
2. กดปุ่ม bookmarklet **จองเลย**
3. ติ๊ก reCAPTCHA แล้วกด **ยืนยันการจอง**
4. เปิดอีเมลเอารหัสจอง แล้วไปหน้าลงทะเบียนให้เสร็จ**ภายใน 30 นาที**
5. อัปโหลดใบขอเข้าเขตและชำระเงิน**ภายใน 6 ชั่วโมง**
6. เช็กสถานะในเมนู "ตรวจสอบสถานะ"

---

## 8. แก้ปัญหาที่เจอบ่อย

| อาการ | วิธีแก้ |
|---|---|
| `can't open file … No such file or directory` | ไฟล์ไม่อยู่ในโฟลเดอร์ที่ `cd` เข้าไป หรือชื่อเป็น `.py.txt` ใช้คำสั่ง `dir` ตรวจ |
| `python` เปิด Microsoft Store | ยังไม่ได้ติดตั้ง Python หรือไม่ได้ติ๊ก Add to PATH ติดตั้งใหม่ตามหัวข้อ 2.1 |
| `ModuleNotFoundError: requests` | รัน `pip install requests` |
| แก้ค่าแล้วไม่เปลี่ยน | ยังไม่ได้กด Ctrl + S หรือแก้คนละไฟล์ ตรวจด้วย `Select-String -Path calendar_doiluang.py -Pattern "PEOPLE ="` |
| เปิด localhost ไม่ได้ / พอร์ตชน | เปลี่ยน `PORT = 8080` แล้วรันใหม่ |
| ช่องขึ้น "เช็กไม่ได้" หรือมีแถบเตือนสีเหลือง | อาจโดนจำกัดการเข้าถึง ระบบชะลอให้เองแล้ว ถ้ายังเป็นต่อ ลดจำนวน P0 หรือลด `RATE_PER_MIN` |
| Telegram ไม่เด้ง | เช็กว่ากด Start กับบอทแล้ว และ token / chat_id ถูกต้อง |

---

## 9. โค้ดโปรแกรมฉบับเต็ม (`calendar_doiluang.py`)

```python
# -*- coding: utf-8 -*-
"""
ปฏิทินที่ว่าง ดอยหลวงเชียงดาว v2 + แจ้งเตือน Telegram

รัน:   python calendar_doiluang.py
แล้วเปิด http://localhost:8000 (สคริปต์จะเปิดให้อัตโนมัติ)

คลิกวันที่บนปฏิทินเพื่อวนระดับการเฝ้า:
  ไม่เฝ้า -> P1 (เช็กทุก 60 วิ) -> P0 (เช็กทุก 30 วิ) -> ไม่เฝ้า
หยุด:  กด Ctrl + C ในหน้าต่าง PowerShell
"""
import os
import csv
import json
import time
import random
import datetime
import threading
import webbrowser
from collections import deque
from urllib.parse import urlparse, parse_qs
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

import requests

# ===================== ตั้งค่า (แก้ตรงนี้) =====================

API_URL = "https://q.wildlifesanctuaryfca16.com/api/v1/bookings/availability"
BOOKING_PAGE = "https://q.wildlifesanctuaryfca16.com"

START_DATE = "2026-11-16"    # วันแรกที่เปิดให้เดิน (ตามระบบจอง)
END_DATE = "2027-02-12"      # วันสุดท้ายที่เลือกได้ในระบบจอง
PEOPLE = 1                   # แจ้งเตือนเมื่อที่ว่าง >= จำนวนนี้ (ระบบจองได้สูงสุด 2 คนต่อครั้ง)

# วันในสัปดาห์ที่จะเช็กในปฏิทินภาพรวม: 0=จันทร์ 1=อังคาร 3=พฤหัส 4=ศุกร์ 5=เสาร์ 6=อาทิตย์
# (วันพุธปิดอยู่แล้ว) เช่น เช็กแค่ศุกร์-อาทิตย์ ใส่ [4, 5, 6]
SCAN_WEEKDAYS = [0, 1, 3, 4, 5, 6]

BOOKING_CLOSE = "2026-10-30 16:00"   # ระบบปิดรับจอง หลังจากนี้สคริปต์หยุดเอง

P0_SEC = 30                  # วันที่เฝ้าระดับ P0: เช็กทุกกี่วินาที
P1_SEC = 60                  # วันที่เฝ้าระดับ P1: เช็กทุกกี่วินาที
FULL_REFRESH_MIN = 10        # วันอื่นในปฏิทิน: เช็กทุกกี่นาที
RATE_PER_MIN = 30            # งบคำขอสูงสุดต่อนาที (กันโดนบล็อก) ไม่ควรเกิน 30

COOLDOWN_MIN = 5             # แจ้งซ้ำเมื่อที่ว่างเพิ่มขึ้น ได้ไม่ถี่กว่านี้ต่อวัน
HEARTBEAT_HOURS = 6          # ส่งข้อความ "ยังทำงานอยู่" ทุกกี่ชั่วโมง

# วันที่เฝ้าเริ่มต้น (หลังจากนั้นคลิกบนปฏิทินได้ ระบบจะจำไว้ในไฟล์ watch_dates.json)
DEFAULT_WATCH = {"2027-01-23": "P1", "2027-01-24": "P1", "2027-01-30": "P1", "2027-01-31": "P1"}

TELEGRAM_TOKEN = "<TELEGRAM_TOKEN>"
TELEGRAM_CHAT_ID = "<CHAT_ID>"

PORT = 8000

# ===========================================================

BACKOFF_BASE_SEC = 10       # เช็กพลาด: พักเริ่มที่ 10 วิ แล้วเพิ่มเป็น 2 เท่าจนถึง 10 นาที

HERE = os.path.dirname(os.path.abspath(__file__))
WATCH_FILE = os.path.join(HERE, "watch_dates.json")
EVENTS_FILE = os.path.join(HERE, "events.csv")

lock = threading.Lock()
state = {
    "dates": {}, "last_check": None, "progress": None, "checks": 0,
    "error_streak": 0, "backoff_until": 0.0, "status": "กำลังทำงาน",
}
watch = {}          # วันที่ -> "P0" / "P1"
next_due = {}       # วันที่ -> เวลาที่ต้องเช็กครั้งถัดไป
force = []          # วันที่ที่เพิ่งกดเฝ้า ให้เช็กทันที
req_times = deque() # เวลาของคำขอในช่วง 60 วินาทีล่าสุด
last_alert = {}     # วันที่ -> เวลาที่แจ้งเตือนล่าสุด
alerted = set()     # วันที่ที่แจ้งว่า "ว่าง" ไปแล้วและยังว่างอยู่

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (personal availability checker)",
    "Referer": BOOKING_PAGE,
    "Accept": "application/json",
})


def now():
    return datetime.datetime.now().strftime("%H:%M:%S")


def today_str():
    return datetime.date.today().isoformat()


def load_watch():
    global watch
    try:
        with open(WATCH_FILE, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):  # ไฟล์จากเวอร์ชันเก่า
            watch = {d: "P1" for d in data}
        else:
            watch = {d: p for d, p in data.items() if p in ("P0", "P1")}
    except Exception:
        watch = dict(DEFAULT_WATCH)
    save_watch()


def save_watch():
    with open(WATCH_FILE, "w", encoding="utf-8") as f:
        json.dump(dict(sorted(watch.items())), f, indent=1)


def _send(text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": text},
            timeout=10,
        )
    except Exception as e:
        print(f"[{now()}] ส่ง Telegram ไม่สำเร็จ: {e}")


def notify(text):
    """ส่งแบบไม่รอ เพื่อไม่ให้การเช็กครั้งถัดไปช้าลง"""
    threading.Thread(target=_send, args=(text,), daemon=True).start()


def log_event(d, old, new):
    """เก็บประวัติทุกครั้งที่ที่ว่างเปลี่ยน ไว้ดูว่ามักหลุดช่วงไหน (เปิดด้วย Excel ได้)"""
    try:
        is_new = not os.path.exists(EVENTS_FILE)
        with open(EVENTS_FILE, "a", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            if is_new:
                w.writerow(["time", "date", "old_available", "new_available"])
            w.writerow([datetime.datetime.now().isoformat(timespec="seconds"), d, old, new])
    except Exception as e:
        print(f"[{now()}] บันทึก events.csv ไม่ได้: {e}")


def all_dates():
    """วันที่ในช่วงจองได้ ตามวันในสัปดาห์ที่เลือกไว้ (ไม่รวมวันพุธ)"""
    d = max(datetime.date.today(), datetime.date.fromisoformat(START_DATE))
    end = datetime.date.fromisoformat(END_DATE)
    out = []
    while d <= end:
        if d.weekday() != 2 and d.weekday() in SCAN_WEEKDAYS:
            out.append(d.isoformat())
        d += datetime.timedelta(days=1)
    return out


def check(date):
    r = session.get(API_URL, params={"date": date}, timeout=10)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}")
    j = r.json()
    if not j.get("success"):
        raise RuntimeError(f"ระบบตอบกลับไม่สำเร็จ: {str(j)[:80]}")
    d = j["data"]
    return int(d["available"]), int(d["capacity"])


def demand_per_min():
    """คำขอที่ต้องใช้ต่อนาทีตามการตั้งค่าตอนนี้"""
    t = today_str()
    with lock:
        w = {d: p for d, p in watch.items() if d >= t}
    n0 = sum(1 for p in w.values() if p == "P0")
    n1 = sum(1 for p in w.values() if p == "P1")
    nbg = len([d for d in all_dates() if d not in w])
    return n0 * 60 / P0_SEC + n1 * 60 / P1_SEC + nbg / FULL_REFRESH_MIN


def handle_change(d, prio, prev, avail, cap):
    if prev is not None and prev != avail:
        log_event(d, prev, avail)
    if prio is None:
        return
    t = time.time()
    if avail >= PEOPLE:
        crossed = prev is None or prev < PEOPLE
        grew = prev is not None and avail > prev and t - last_alert.get(d, 0) >= COOLDOWN_MIN * 60
        if crossed or grew:
            last_alert[d] = t
            alerted.add(d)
            notify(
                f"[{prio}] มีที่ว่างแล้ว! วันที่ {d}\n"
                f"ว่าง {avail} จาก {cap} ที่\n"
                f"กดเพื่อจอง: {BOOKING_PAGE}/#d={d}&n={PEOPLE}\n"
                f"(เปิดแล้วกดปุ่ม bookmarklet ระบบจะพาไปหน้ากรอกให้)"
            )
    elif d in alerted:
        alerted.discard(d)
        notify(f"[{prio}] วันที่ {d} เต็มแล้ว (ว่าง {avail})")


def pick_next(now_t):
    """ลำดับ: วันที่เพิ่งกดเฝ้า > P0 ที่ถึงคิว > P1 ที่ถึงคิว > วันอื่นที่ถึงคิว"""
    t = today_str()
    with lock:
        while force:
            d = force.pop(0)
            if d >= t:
                return d, watch.get(d)
        w = {d: p for d, p in watch.items() if d >= t}
    for level in ("P0", "P1"):
        due = [d for d, p in w.items() if p == level and next_due.get(d, 0) <= now_t]
        if due:
            return min(due, key=lambda d: next_due.get(d, 0)), level
    due = [d for d in all_dates() if d not in w and next_due.get(d, 0) <= now_t]
    if due:
        return min(due, key=lambda d: next_due.get(d, 0)), None
    return None, None


def poll_loop():
    with lock:
        w0 = ", ".join(f"{d} ({p})" for d, p in sorted(watch.items()))
    notify(f"เริ่มเฝ้าที่ว่างดอยหลวงเชียงดาว v2: {w0 or '-'} สำหรับ {PEOPLE} คน")
    close_at = datetime.datetime.strptime(BOOKING_CLOSE, "%Y-%m-%d %H:%M")
    min_gap = 60.0 / RATE_PER_MIN
    last_req = 0.0
    last_hb = time.time()
    warned_budget = False

    while True:
        if datetime.datetime.now() >= close_at:
            print(f"[{now()}] ระบบจองปิดแล้ว ({BOOKING_CLOSE}) หยุดเช็ก")
            notify("ระบบจองดอยหลวงปิดแล้ว สคริปต์หยุดเช็กแล้วครับ")
            with lock:
                state["status"] = "ระบบจองปิดแล้ว"
                state["progress"] = None
            return

        if time.time() - last_hb >= HEARTBEAT_HOURS * 3600:
            last_hb = time.time()
            with lock:
                n = state["checks"]
            notify(f"ยังเฝ้าอยู่ครับ เช็กไปแล้ว {n} ครั้ง")

        need = demand_per_min()
        if need > RATE_PER_MIN and not warned_budget:
            warned_budget = True
            print(f"[{now()}] คำเตือน: ตั้งค่าตอนนี้ต้องใช้ {need:.0f} คำขอ/นาที เกินงบ {RATE_PER_MIN} "
                  f"วันอื่นในปฏิทินจะถูกเช็กช้าลง (ลด P0 หรือเพิ่ม FULL_REFRESH_MIN)")
        elif need <= RATE_PER_MIN:
            warned_budget = False

        with lock:
            backoff_until = state["backoff_until"]
        if time.time() < backoff_until:
            with lock:
                state["progress"] = "ชะลอชั่วคราวถึง " + datetime.datetime.fromtimestamp(backoff_until).strftime("%H:%M:%S")
            time.sleep(1)
            continue

        d, prio = pick_next(time.time())
        if d is None:
            with lock:
                state["progress"] = None
            time.sleep(0.5)
            continue

        # คุมงบคำขอ: เว้นระยะขั้นต่ำระหว่างคำขอ + jitter
        wait = last_req + min_gap * random.uniform(1.0, 1.2) - time.time()
        if wait > 0:
            time.sleep(wait)
        last_req = time.time()

        with lock:
            state["progress"] = f"{prio or 'ปฏิทิน'} {d}"
            req_times.append(last_req)
            while req_times and req_times[0] < last_req - 60:
                req_times.popleft()

        try:
            avail, cap = check(d)
            err = None
        except Exception as e:
            avail, cap, err = None, None, str(e)[:150]

        with lock:
            prev = state["dates"].get(d, {}).get("available")
            state["dates"][d] = {
                "available": avail if err is None else prev,
                "capacity": cap if err is None else state["dates"].get(d, {}).get("capacity"),
                "error": err, "updated": now(),
            }
            state["last_check"] = now()
            state["checks"] += 1
            if err is None:
                recovered = state["error_streak"] >= 5
                state["error_streak"] = 0
            else:
                state["error_streak"] += 1
                streak = state["error_streak"]
                state["backoff_until"] = time.time() + min(600, BACKOFF_BASE_SEC * 2 ** (streak - 1))

        if err is None:
            if recovered:
                notify("กลับมาเช็กได้ตามปกติแล้วครับ")
            handle_change(d, prio, prev, avail, cap)
            if prio:
                print(f"[{now()}] {prio} {d}: ว่าง {avail}/{cap}")
        else:
            print(f"[{now()}] {d}: เช็กไม่สำเร็จ ({err}) ชะลอการเช็กชั่วคราว")
            if streak == 5:
                notify(f"เช็กไม่สำเร็จติดกัน 5 ครั้ง ({err}) ระบบชะลอการเช็กอัตโนมัติ ลองเปิดเว็บจองดูว่ายังเข้าได้ไหม")

        if prio == "P0":
            interval = P0_SEC + random.uniform(0, 3)
        elif prio == "P1":
            interval = P1_SEC + random.uniform(0, 5)
        else:
            interval = FULL_REFRESH_MIN * 60 + random.uniform(0, 30)
        next_due[d] = time.time() + interval


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype):
        b = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            self._send(200, PAGE, "text/html; charset=utf-8")
        elif path == "/data":
            need = demand_per_min()
            with lock:
                t = time.time()
                payload = {
                    "dates": dict(state["dates"]),
                    "watch": dict(watch),
                    "people": PEOPLE,
                    "p0_sec": P0_SEC, "p1_sec": P1_SEC, "full_min": FULL_REFRESH_MIN,
                    "rate_budget": RATE_PER_MIN,
                    "rate_actual": len([x for x in req_times if x >= t - 60]),
                    "demand": round(need, 1),
                    "last_check": state["last_check"],
                    "progress": state["progress"],
                    "status": state["status"],
                    "checks": state["checks"],
                    "error_streak": state["error_streak"],
                    "today": today_str(),
                    "start_date": START_DATE,
                    "end_date": END_DATE,
                    "scan_weekdays": SCAN_WEEKDAYS,
                    "booking_close": BOOKING_CLOSE.replace(" ", "T") + ":00+07:00",
                    "booking_page": BOOKING_PAGE,
                }
            self._send(200, json.dumps(payload, ensure_ascii=False), "application/json; charset=utf-8")
        else:
            self._send(404, "not found", "text/plain")

    def do_POST(self):
        u = urlparse(self.path)
        if u.path != "/toggle":
            return self._send(404, "not found", "text/plain")
        d = parse_qs(u.query).get("date", [""])[0]
        try:
            datetime.date.fromisoformat(d)
        except ValueError:
            return self._send(400, "bad date", "text/plain")
        with lock:
            cur = watch.get(d)
            nxt = {None: "P1", "P1": "P0", "P0": None}[cur]
            if nxt:
                watch[d] = nxt
                force.append(d)  # เพิ่งเปลี่ยนระดับ ให้เช็กทันที
            else:
                watch.pop(d, None)
            save_watch()
            w = dict(watch)
        print(f"[{now()}] {d}: {cur or 'ไม่เฝ้า'} -> {nxt or 'ไม่เฝ้า'}")
        self._send(200, json.dumps({"watch": w}), "application/json")

    def log_message(self, *args):
        pass


PAGE = r"""<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ที่ว่าง ดอยหลวงเชียงดาว</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@400;500;700&display=swap" rel="stylesheet">
<style>
:root{
  --pine:#1f3b2d; --bg:#eceeea; --card:#ffffff; --text:#1c2420; --muted:#66706a; --line:#d6dbd5;
  --ok:#cfeedd; --ok-t:#0f5a32; --some:#fbe7b0; --some-t:#6e4f00;
  --full:#f4f5f2; --full-t:#8a928c; --off:#e3e6e1; --p1:#b3262e; --p0:#5b2bbf; --warn:#fbe7b0;
  color-scheme:light;
}
@media (prefers-color-scheme:dark){:root{
  --pine:#16291f; --bg:#121614; --card:#1b201d; --text:#e6ebe7; --muted:#97a19a; --line:#2e3631;
  --ok:#153d27; --ok-t:#8fe3b2; --some:#43360c; --some-t:#f1d273;
  --full:#1f2421; --full-t:#7d867f; --off:#171b19; --p1:#ef5a62; --p0:#b49cff; --warn:#43360c;
  color-scheme:dark;
}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);
  font-family:"IBM Plex Sans Thai","Leelawadee UI","Tahoma",system-ui,sans-serif;font-size:15px;line-height:1.5}
header{background:var(--pine);color:#eef4ef;padding:16px 24px 14px;position:sticky;top:0;z-index:2}
.row{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 20px}
h1{font-size:22px;font-weight:700;margin:0}
.countdown{font-size:15px;font-weight:500}
.countdown b{font-size:18px}
.status{font-size:13px;opacity:.85;margin-top:4px;display:flex;flex-wrap:wrap;gap:4px 16px}
.alert{margin-top:8px;padding:6px 10px;border-radius:6px;background:var(--warn);color:var(--text);font-size:13px;display:none}
.legend{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:13px;margin-top:10px;align-items:center}
.legend span{display:inline-flex;align-items:center;gap:6px}
.sw{width:14px;height:14px;border-radius:3px;display:inline-block}
header a{color:#fff;font-weight:500}
main{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:20px;padding:20px 24px 40px;max-width:1500px}
.month{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px}
.month h2{font-size:17px;font-weight:700;margin:0 0 10px}
.grid{display:grid;grid-template-columns:repeat(7,1fr);gap:4px}
.dow{font-size:12px;color:var(--muted);text-align:center}
.cell{min-height:66px;border-radius:6px;padding:4px 5px;background:var(--full);color:var(--full-t);
  border:2px solid transparent;display:flex;flex-direction:column;cursor:pointer;font:inherit;text-align:left}
.cell:focus-visible{outline:2px solid var(--text);outline-offset:2px}
.cell .d{font-size:12px;color:var(--muted)}
.cell .v{font-size:17px;font-weight:700;line-height:1.2;margin-top:auto}
.cell .v small{font-size:11px;font-weight:400}
.cell .w{font-size:11px;font-weight:700;min-height:15px}
.cell.ok{background:var(--ok);color:var(--ok-t)}
.cell.some{background:var(--some);color:var(--some-t)}
.cell.off,.cell.past,.cell.skip{background:var(--off);cursor:default}
.cell.past,.cell.off{pointer-events:none}
.cell.skip{cursor:pointer}
.cell.past{opacity:.45}
.cell.off .v,.cell.skip .v{font-size:12px;font-weight:500}
.cell.p1{border-color:var(--p1)} .cell.p1 .w{color:var(--p1)}
.cell.p0{border-color:var(--p0);border-width:3px} .cell.p0 .w{color:var(--p0)}
.cell.err .v{font-size:12px;color:var(--p1)}
.cell .book{font-size:12px;font-weight:700;color:inherit;text-decoration:underline;margin-top:2px;align-self:flex-start;padding:2px 0}
.cell .book:hover{opacity:.75}
.fresh{animation:flash 1.2s ease-out}
@keyframes flash{from{box-shadow:0 0 0 4px var(--ok-t)}to{box-shadow:0 0 0 0 transparent}}
@media (prefers-reduced-motion:reduce){.fresh{animation:none}}
@media (max-width:420px){main{grid-template-columns:1fr;padding:12px}.cell{min-height:52px}}
</style>
</head>
<body>
<header>
  <div class="row">
    <h1>ที่ว่าง ดอยหลวงเชียงดาว</h1>
    <div class="countdown" id="countdown"></div>
  </div>
  <div class="status" id="status">กำลังโหลดข้อมูล</div>
  <div class="alert" id="alert"></div>
  <div class="legend">
    <span><i class="sw" style="background:var(--ok)"></i>ว่างพอสำหรับคุณ</span>
    <span><i class="sw" style="background:var(--some)"></i>ว่างบ้าง แต่ไม่พอ</span>
    <span><i class="sw" style="background:var(--full)"></i>เต็ม</span>
    <span><i class="sw" style="border:2px solid var(--p1)"></i>P1 เช็กทุก 1 นาที</span>
    <span><i class="sw" style="border:3px solid var(--p0)"></i>P0 เช็กทุก 30 วินาที</span>
    <span>คลิกวันที่: ไม่เฝ้า → P1 → P0 → ไม่เฝ้า</span>
    <span>กด "จอง →" ในช่องที่ว่าง เพื่อเปิดเว็บจองพร้อมวันที่</span>
    <a href="https://q.wildlifesanctuaryfca16.com" target="_blank" rel="noopener">เปิดหน้าจอง</a>
  </div>
</header>
<main id="cal"></main>
<script>
const TH=["มกราคม","กุมภาพันธ์","มีนาคม","เมษายน","พฤษภาคม","มิถุนายน","กรกฎาคม","สิงหาคม","กันยายน","ตุลาคม","พฤศจิกายน","ธันวาคม"];
const DOW=["อา","จ","อ","พ","พฤ","ศ","ส"];
const pad=n=>String(n).padStart(2,"0");
let prevAvail={}, closeAt=null;

async function load(){
  try{
    const r=await fetch("/data",{cache:"no-store"});
    render(await r.json());
  }catch(e){
    document.getElementById("status").textContent="เชื่อมต่อสคริปต์ไม่ได้ ตรวจว่าหน้าต่าง PowerShell ยังเปิดอยู่";
  }
}
async function toggle(ds){
  await fetch("/toggle?date="+ds,{method:"POST"});
  load();
}
function tick(){
  const el=document.getElementById("countdown");
  if(!closeAt){el.textContent="";return;}
  let s=Math.floor((closeAt-Date.now())/1000);
  if(s<=0){el.textContent="ระบบจองปิดแล้ว";return;}
  const d=Math.floor(s/86400);s%=86400;const h=Math.floor(s/3600);s%=3600;const m=Math.floor(s/60);s%=60;
  el.innerHTML="ปิดรับจองในอีก <b>"+(d?d+" วัน ":"")+pad(h)+":"+pad(m)+":"+pad(s)+"</b>";
}
function render(j){
  closeAt=Date.parse(j.booking_close);
  const st=document.getElementById("status");
  st.innerHTML="";
  [
    j.status,
    "ไป "+j.people+" คน",
    "คำขอ "+j.rate_actual+"/"+j.rate_budget+" ต่อนาที",
    j.progress?("กำลังเช็ก "+j.progress):null,
    j.last_check?("เช็กล่าสุด "+j.last_check):null,
    "รวม "+j.checks+" ครั้ง"
  ].filter(Boolean).forEach(p=>{const s=document.createElement("span");s.textContent=p;st.appendChild(s);});

  const al=document.getElementById("alert");
  const msgs=[];
  if(j.demand>j.rate_budget)msgs.push("ตั้งค่าตอนนี้ต้องใช้ "+j.demand+" คำขอ/นาที เกินงบ "+j.rate_budget+" วันที่ไม่ได้เฝ้าจะถูกเช็กช้าลง ลองลดจำนวนวัน P0");
  if(j.error_streak>0)msgs.push("เช็กไม่สำเร็จติดกัน "+j.error_streak+" ครั้ง ระบบชะลอการเช็กอัตโนมัติ");
  al.style.display=msgs.length?"block":"none";
  al.textContent=msgs.join(" | ");

  const watch=j.watch;
  const from=j.today>j.start_date?j.today:j.start_date;
  const [ty,tm]=from.split("-").map(Number);
  const [ey,em]=j.end_date.split("-").map(Number);
  const scan=new Set(j.scan_weekdays);
  const cal=document.getElementById("cal");
  cal.innerHTML="";
  let y=ty,m=tm;
  while(y<ey||(y===ey&&m<=em)){
    const box=document.createElement("section");box.className="month";
    const h=document.createElement("h2");h.textContent=TH[m-1]+" "+(y+543);box.appendChild(h);
    const g=document.createElement("div");g.className="grid";
    DOW.forEach(x=>{const e=document.createElement("div");e.className="dow";e.textContent=x;g.appendChild(e);});
    const first=new Date(y,m-1,1).getDay(), days=new Date(y,m,0).getDate();
    for(let i=0;i<first;i++)g.appendChild(document.createElement("div"));
    for(let d=1;d<=days;d++){
      const ds=y+"-"+pad(m)+"-"+pad(d);
      const dow=new Date(y,m-1,d).getDay();
      const c=document.createElement("div");c.className="cell";
      const w=watch[ds];
      let v="",cls="",canBook=false;
      if(ds<j.today||ds<j.start_date||ds>j.end_date){cls="past";}
      else if(dow===3){cls="off";v="หยุด";}
      else{
        const x=j.dates[ds];
        if(!x){
          if(!w&&!scan.has((dow+6)%7)){cls="skip";v="ไม่เช็ก";}
          else{v="…";}
        }
        else if(x.available===null||x.available===undefined){cls="err";v="เช็กไม่ได้";c.title=x.error||"";}
        else{
          v=x.available+"<small>/"+x.capacity+"</small>";
          cls=x.available>=j.people?"ok":(x.available>0?"some":"");
          canBook=x.available>0;
          c.title="อัปเดต "+x.updated+(x.error?" (รอบล่าสุดผิดพลาด: "+x.error+")":"");
          if(prevAvail[ds]!==undefined&&x.available>prevAvail[ds])c.classList.add("fresh");
          prevAvail[ds]=x.available;
        }
      }
      if(cls)c.classList.add(cls);
      if(w)c.classList.add(w.toLowerCase());
      c.innerHTML='<span class="d">'+d+'</span><span class="w">'+(w==="P0"?"P0 ด่วน":w==="P1"?"P1 เฝ้า":"")+'</span><span class="v">'+v+'</span>';
      if(canBook){
        const a=document.createElement("a");a.className="book";a.textContent="จอง →";
        a.href=j.booking_page+"/#d="+ds+"&n="+j.people;a.target="doiluang-book";a.rel="noopener";
        a.onclick=e=>e.stopPropagation();
        c.appendChild(a);
      }
      if(cls!=="past"&&cls!=="off"){
        c.tabIndex=0;c.setAttribute("role","button");c.setAttribute("aria-label",ds+(w?" "+w:""));
        c.onclick=()=>toggle(ds);
        c.onkeydown=e=>{if(e.target===c&&(e.key==="Enter"||e.key===" ")){e.preventDefault();toggle(ds);}};
      }
      g.appendChild(c);
    }
    box.appendChild(g);cal.appendChild(box);
    m++;if(m>12){m=1;y++;}
  }
  tick();
}
load();
setInterval(load,3000);
setInterval(tick,1000);
</script>
</body>
</html>
"""


def main():
    load_watch()
    threading.Thread(target=poll_loop, daemon=True).start()
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://localhost:{PORT}"
    print(f"[{now()}] เปิดปฏิทินที่ {url}  (กด Ctrl+C เพื่อหยุด)")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nหยุดเฝ้าแล้ว")


if __name__ == "__main__":
    main()
```
