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
PEOPLE = 2                   # แจ้งเตือนเมื่อที่ว่าง >= จำนวนนี้ (ระบบจองได้สูงสุด 2 คนต่อครั้ง)

# วันในสัปดาห์ที่จะเช็กในปฏิทินภาพรวม: 0=จันทร์ 1=อังคาร 3=พฤหัส 4=ศุกร์ 5=เสาร์ 6=อาทิตย์
# (วันพุธปิดอยู่แล้ว) เช่น เช็กแค่ศุกร์-อาทิตย์ ใส่ [4, 5, 6]
SCAN_WEEKDAYS = [0, 1, 3, 4, 5, 6]

BOOKING_CLOSE = "2026-10-30 16:00"   # ระบบปิดรับจอง หลังจากนี้สคริปต์หยุดเอง

P0_SEC = 10                  # วันที่เฝ้าระดับ P0: เช็กทุกกี่วินาที
P1_SEC = 30                  # วันที่เฝ้าระดับ P1: เช็กทุกกี่วินาที
FULL_REFRESH_MIN = 1        # วันอื่นในปฏิทิน: เช็กทุกกี่นาที
RATE_PER_MIN = 200           # งบคำขอสูงสุดต่อนาที (กันโดนบล็อก) ไม่ควรเกิน 30

COOLDOWN_MIN = 5             # แจ้งซ้ำเมื่อที่ว่างเพิ่มขึ้น ได้ไม่ถี่กว่านี้ต่อวัน
HEARTBEAT_HOURS = 6          # ส่งข้อความ "ยังทำงานอยู่" ทุกกี่ชั่วโมง

# วันที่เฝ้าเริ่มต้น (หลังจากนั้นคลิกบนปฏิทินได้ ระบบจะจำไว้ในไฟล์ watch_dates.json)
DEFAULT_WATCH = {"2027-01-23": "P1", "2027-01-24": "P1", "2027-01-30": "P1", "2027-01-31": "P1"}

# ค่าลับ (token, chat_id, รหัสผู้ดูแล) ไม่เขียนในโค้ด: อ่านจาก environment variable
# หรือไฟล์ .env ข้างสคริปต์ (บรรทัดละ KEY=VALUE) ห้ามเอา .env ขึ้น git
HERE = os.path.dirname(os.path.abspath(__file__))


def _load_env_file():
    try:
        with open(os.path.join(HERE, ".env"), encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    except FileNotFoundError:
        pass


_load_env_file()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
# ส่งหาหลายคนได้ คั่นด้วยจุลภาค เช่น "<CHAT_ID>,123456789" หรือใส่ chat_id ของกลุ่ม (ขึ้นต้นด้วย -)
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# บน cloud ผู้ให้บริการจะกำหนด PORT มาให้ ถ้ามี PORT สคริปต์จะเปิดรับการเชื่อมต่อจากภายนอกเอง
PORT = int(os.environ.get("PORT", 8000))

# ดูหน้าปฏิทินจากมือถือที่ต่อ Wi-Fi เดียวกับคอม (True = เปิด) หรือรันบน cloud (เปิดให้อัตโนมัติ)
# ครั้งแรก Windows จะถามเรื่อง Firewall ให้กด Allow (เลือก Private network)
ON_CLOUD = "PORT" in os.environ
ALLOW_PHONE = os.environ.get("ALLOW_PHONE", "False").lower() in ("true", "1") or ON_CLOUD
HOST = os.environ.get("HOST", "0.0.0.0" if ALLOW_PHONE else "127.0.0.1")

# รหัสผู้ดูแล: คนที่เปิดลิงก์โดยไม่มีรหัสจะ "ดูได้อย่างเดียว" (กดเฝ้า/ดึงใหม่/ทดสอบ Telegram ไม่ได้)
# คอมเครื่องนี้ที่เปิด http://localhost:8000 ตรง ๆ เป็นผู้ดูแลอัตโนมัติ
# เครื่องอื่นหรือผ่านลิงก์ภายนอก ให้เปิดแบบ  http://ที่อยู่:8000/?key=รหัส
# บน cloud ต้องตั้ง ADMIN_KEY ไม่งั้นจะกดเฝ้าวันที่จากหน้าเว็บไม่ได้
ADMIN_KEY = os.environ.get("ADMIN_KEY", "เปลี่ยนรหัสนี้")

# ===========================================================

MANUAL_GAP_SEC = 20          # ปุ่ม "ดึงใหม่" กดซ้ำได้ทุกกี่วินาที
BACKOFF_BASE_SEC = 10       # เช็กพลาด: พักเริ่มที่ 10 วิ แล้วเพิ่มเป็น 2 เท่าจนถึง 10 นาที

# โฟลเดอร์เก็บ watch_dates.json กับ events.csv: บน cloud ดิสก์มักถูกล้างทุกครั้งที่รีสตาร์ท
# ให้ชี้ DATA_DIR ไปที่ volume ถาวร (เช่น /data) ถ้าไม่ตั้ง จะใช้โฟลเดอร์เดียวกับสคริปต์
DATA_DIR = os.environ.get("DATA_DIR", HERE)
os.makedirs(DATA_DIR, exist_ok=True)
WATCH_FILE = os.path.join(DATA_DIR, "watch_dates.json")
EVENTS_FILE = os.path.join(DATA_DIR, "events.csv")

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
fresh_watch = set() # วันที่เพิ่งกดเฝ้า ถ้าว่างอยู่แล้วให้แจ้งทันทีในการเช็กครั้งแรก
last_manual = {"watch": 0.0, "all": 0.0}  # เวลาที่กดปุ่มดึงใหม่ล่าสุด

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
    """ส่งข้อความ คืนค่า None ถ้าสำเร็จ หรือข้อความ error ถ้าไม่สำเร็จ"""
    errors = []
    for chat in [c.strip() for c in TELEGRAM_CHAT_ID.split(",") if c.strip()]:
        try:
            r = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                data={"chat_id": chat, "text": text},
                timeout=10,
            )
            j = r.json()
            if not j.get("ok"):
                errors.append(f"{chat}: {j.get('description', r.status_code)}")
        except Exception as e:
            errors.append(f"{chat}: {e}")
    if errors:
        err = " | ".join(errors)
        print(f"[{now()}] ส่ง Telegram ไม่สำเร็จ: {err}")
        return err
    return None


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
    with lock:
        first = d in fresh_watch
        fresh_watch.discard(d)
    if avail >= PEOPLE:
        crossed = prev is None or prev < PEOPLE or (first and d not in alerted)
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
                "ts": time.time() if err is None else state["dates"].get(d, {}).get("ts"),
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
    def _is_admin(self):
        """localhost ตรง ๆ = ผู้ดูแล, ผ่าน tunnel/เครื่องอื่น ต้องมี ?key= ที่ถูกต้อง"""
        forwarded = self.headers.get("X-Forwarded-For") or self.headers.get("Cf-Connecting-Ip")
        if self.client_address[0] in ("127.0.0.1", "::1") and not forwarded:
            return True
        key = parse_qs(urlparse(self.path).query).get("key", [""])[0]
        return bool(ADMIN_KEY) and ADMIN_KEY != "เปลี่ยนรหัสนี้" and key == ADMIN_KEY

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
            admin = self._is_admin()
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
                    "server_time": t,
                    "admin": admin,
                }
            self._send(200, json.dumps(payload, ensure_ascii=False), "application/json; charset=utf-8")
        else:
            self._send(404, "not found", "text/plain")

    def _refresh(self, scope):
        if scope not in ("watch", "all"):
            return self._send(400, "bad scope", "text/plain")
        t = time.time()
        today = today_str()
        with lock:
            wait = MANUAL_GAP_SEC - (t - last_manual[scope])
            if wait <= 0:
                last_manual[scope] = t
                w = sorted((d for d in watch if d >= today), key=lambda d: (watch[d] != "P0", d))
                force.extend(d for d in w if d not in force)
        if wait > 0:
            return self._send(200, json.dumps({"ok": False, "wait": int(wait) + 1}), "application/json")
        count = len(w)
        if scope == "all":
            rest = [d for d in all_dates() if d not in w]
            for d in rest:
                next_due[d] = 0
            count += len(rest)
        minutes = max(1, round(count / RATE_PER_MIN))
        print(f"[{now()}] กดดึงใหม่ ({'ทั้งหมด' if scope == 'all' else 'วันที่เฝ้า'}) {count} วัน")
        self._send(200, json.dumps({"ok": True, "count": count, "minutes": minutes}), "application/json")

    def do_POST(self):
        u = urlparse(self.path)
        if not self._is_admin():
            return self._send(403, json.dumps({"ok": False, "error": "ดูได้อย่างเดียว ต้องใช้ลิงก์ที่มีรหัสผู้ดูแล"}, ensure_ascii=False), "application/json; charset=utf-8")
        if u.path == "/test-telegram":
            err = _send(f"ทดสอบแจ้งเตือนจากปฏิทินดอยหลวง ({now()}) ถ้าเห็นข้อความนี้ แปลว่า Telegram ใช้งานได้")
            return self._send(200, json.dumps({"ok": err is None, "error": err}, ensure_ascii=False), "application/json; charset=utf-8")
        if u.path == "/refresh":
            return self._refresh(parse_qs(u.query).get("scope", ["watch"])[0])
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
                if cur is None:
                    fresh_watch.add(d)
            else:
                watch.pop(d, None)
                alerted.discard(d)
                fresh_watch.discard(d)
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
  font-family:"IBM Plex Sans Thai","Leelawadee UI","Tahoma",system-ui,sans-serif;font-size:14px;line-height:1.45}
header{background:var(--pine);color:#eef4ef;padding:8px 20px 8px;position:sticky;top:0;z-index:2}
.row{display:flex;flex-wrap:wrap;align-items:baseline;gap:2px 18px}
h1{font-size:18px;font-weight:700;margin:0}
.countdown{font-size:14px;font-weight:500}
.ro{display:none;font-size:12px;font-weight:700;background:#eef4ef;color:var(--pine);border-radius:999px;padding:1px 10px}
.countdown b{font-size:16px}
.status{font-size:12px;opacity:.85;display:flex;flex-wrap:wrap;gap:2px 14px}
.alert{margin-top:6px;padding:4px 10px;border-radius:6px;background:var(--warn);color:var(--text);font-size:12px;display:none}
.legend{display:flex;flex-wrap:wrap;gap:3px 14px;font-size:12px;margin-top:4px;align-items:center}
.legend span{display:inline-flex;align-items:center;gap:5px}
.sw{width:12px;height:12px;border-radius:3px;display:inline-block}
header a{color:#fff;font-weight:500}
.top{display:flex;flex-wrap:wrap;gap:10px;align-items:stretch;padding:10px 20px 0}
.kpis{flex:1 1 640px;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
.kpi{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--line);border-radius:8px;padding:5px 12px;min-width:0}
.kpi .k{font-size:12px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.kpi .n{font-size:20px;font-weight:700;line-height:1.25}
.kpi .s{font-size:11px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.kpi.good{border-left-color:var(--ok-t)} .kpi.good .n{color:var(--ok-t)}
.kpi.mid{border-left-color:var(--some-t)} .kpi.mid .n{color:var(--some-t)}
.kpi.bad{border-left-color:var(--p1)} .kpi.bad .n{color:var(--p1)}
.tools{display:flex;flex-direction:column;justify-content:center;gap:5px}
.btn{font:inherit;font-size:13px;font-weight:500;padding:3px 12px;border-radius:999px;border:1px solid var(--line);background:var(--card);color:var(--text);cursor:pointer;white-space:nowrap}
.btn:hover{border-color:var(--text)}
.rfmsg{font-size:11px;color:var(--muted);max-width:240px}
main{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;padding:10px 20px}
@media (max-width:1100px){main{grid-template-columns:repeat(2,minmax(0,1fr))}}
.month{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px;min-width:0}
.month h2{font-size:14px;font-weight:700;margin:0 0 4px}
.grid{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:3px}
.dow{font-size:11px;color:var(--muted);text-align:center}
.cell{min-height:50px;border-radius:5px;padding:2px 4px;background:var(--full);color:var(--full-t);
  border:2px solid transparent;display:flex;flex-direction:column;cursor:pointer;font:inherit;text-align:left;min-width:0;overflow:hidden}
.cell:focus-visible{outline:2px solid var(--text);outline-offset:1px}
.cell .t1{display:flex;justify-content:space-between;align-items:baseline;gap:2px}
.cell .d{font-size:11px;color:var(--muted)}
.cell .w{font-size:10px;font-weight:700}
.cell .v{font-size:15px;font-weight:700;line-height:1.15;margin-top:auto;white-space:nowrap}
.cell .v small{font-size:9px;font-weight:400}
.cell .foot{font-size:10px;font-weight:700;line-height:1.35;white-space:nowrap;min-height:13px}
.cell .book{color:inherit;text-decoration:underline}
.cell .book:hover{opacity:.75}
.cell .sh{background:var(--p1);color:#fff;border-radius:999px;padding:0 5px}
.cell.ok{background:var(--ok);color:var(--ok-t)}
.cell.some{background:var(--some);color:var(--some-t)}
.cell.off,.cell.past,.cell.skip{background:var(--off);cursor:default}
.cell.past,.cell.off{pointer-events:none}
.cell.skip{cursor:pointer}
.cell.past{opacity:.45}
.cell.off .v,.cell.skip .v{font-size:11px;font-weight:500}
.cell.p1{border-color:var(--p1)} .cell.p1 .w{color:var(--p1)}
.cell.p0{border-color:var(--p0);box-shadow:inset 0 0 0 1px var(--p0)} .cell.p0 .w{color:var(--p0)}
.cell.err .v{font-size:11px;color:var(--p1)}
.fresh{animation:flash 1.2s ease-out}
@keyframes flash{from{box-shadow:0 0 0 4px var(--ok-t)}to{box-shadow:0 0 0 0 transparent}}
@media (prefers-reduced-motion:reduce){.fresh{animation:none}}
.list{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 12px;margin:0 20px 30px}
.list h2{font-size:14px;font-weight:700;margin:0}
.list .hint{font-size:11px;color:var(--muted);margin:0 0 8px}
.rows{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:5px}
.r{display:flex;align-items:center;gap:8px;padding:4px 10px;border-radius:6px;background:var(--full);border-left:4px solid transparent;font-size:13px}
.r .dt{font-weight:700;min-width:100px;white-space:nowrap}
.r .av{font-weight:700;white-space:nowrap}
.r .tg{font-size:11px;font-weight:700;padding:1px 8px;border-radius:999px;white-space:nowrap}
.r .tm{margin-left:auto;font-size:11px;color:var(--muted)}
.r.ok{background:var(--ok);color:var(--ok-t)} .r.some{background:var(--some);color:var(--some-t)}
.r.p1{border-left-color:var(--p1)} .r.p0{border-left-color:var(--p0)}
.tg.short{background:var(--p1);color:#fff} .tg.enough{background:var(--ok-t);color:var(--card)}
.r a{color:inherit;font-size:12px;font-weight:700;white-space:nowrap}
@media (max-width:600px){
  header{position:static;padding:10px 12px}
  .top{padding:10px 10px 0}.kpis{flex-basis:100%;gap:6px}.kpi{padding:5px 8px}.kpi .k{font-size:11px}.kpi .n{font-size:17px}.kpi .s{display:none}
  .tools{flex-direction:row;flex-wrap:wrap}
  main{grid-template-columns:1fr;padding:10px}
  .list{margin:0 10px 24px}.rows{grid-template-columns:1fr}
}
</style>
</head>
<body>
<header>
  <div class="row">
    <h1>ที่ว่าง ดอยหลวงเชียงดาว</h1>
    <span class="ro" id="ro">โหมดดูอย่างเดียว</span>
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
    <span>"จอง →" เปิดเว็บจองพร้อมวันที่</span>
    <a href="https://q.wildlifesanctuaryfca16.com" target="_blank" rel="noopener">เปิดหน้าจอง</a>
  </div>
</header>
<div class="top">
  <div class="kpis" id="kpis"></div>
  <div class="tools">
    <button class="btn" id="rf-watch" type="button">↻ ดึงใหม่ วันที่เฝ้า</button>
    <button class="btn" id="rf-all" type="button">↻ ดึงใหม่ ทั้งหมด</button>
    <button class="btn" id="tg-test" type="button">✉ ทดสอบ Telegram</button>
    <span class="rfmsg" id="rfmsg"></span>
  </div>
</div>
<main id="cal"></main>
<section class="list">
  <h2>เทียบรายวัน</h2>
  <p class="hint">วันที่เฝ้าทั้งหมด และทุกวันที่มีที่ว่าง เรียงตามวันที่</p>
  <div class="rows" id="rows"></div>
</section>
<script>
const TH=["มกราคม","กุมภาพันธ์","มีนาคม","เมษายน","พฤษภาคม","มิถุนายน","กรกฎาคม","สิงหาคม","กันยายน","ตุลาคม","พฤศจิกายน","ธันวาคม"];
const DOW=["อา","จ","อ","พ","พฤ","ศ","ส"];
const pad=n=>String(n).padStart(2,"0");
const THS=["ม.ค.","ก.พ.","มี.ค.","เม.ย.","พ.ค.","มิ.ย.","ก.ค.","ส.ค.","ก.ย.","ต.ค.","พ.ย.","ธ.ค."];
const thDate=ds=>{const [y,m,d]=ds.split("-").map(Number);return d+" "+THS[m-1]+" "+(y+543);};
const ago=s=>s<60?Math.round(s)+" วิ":Math.round(s/60)+" นาที";
let prevAvail={}, closeAt=null, isAdmin=false;
const KEY=new URLSearchParams(location.search).get("key")||"";
const q=(u)=>u+(u.includes("?")?"&":"?")+"key="+encodeURIComponent(KEY);

async function load(){
  try{
    const r=await fetch(q("/data"),{cache:"no-store"});
    render(await r.json());
  }catch(e){
    document.getElementById("status").textContent="เชื่อมต่อสคริปต์ไม่ได้ ตรวจว่าหน้าต่าง PowerShell ยังเปิดอยู่";
  }
}
async function refresh(scope){
  const msg=document.getElementById("rfmsg");
  try{
    const r=await (await fetch(q("/refresh?scope="+scope),{method:"POST"})).json();
    msg.textContent=r.ok?("กำลังดึงใหม่ "+r.count+" วัน ประมาณ "+r.minutes+" นาทีจะครบ"):("กดได้อีกครั้งใน "+r.wait+" วินาที");
  }catch(e){msg.textContent="เชื่อมต่อสคริปต์ไม่ได้";}
  setTimeout(()=>{msg.textContent="";},8000);
  load();
}
document.getElementById("rf-watch").onclick=()=>refresh("watch");
document.getElementById("rf-all").onclick=()=>refresh("all");
document.getElementById("tg-test").onclick=async()=>{
  const msg=document.getElementById("rfmsg");
  msg.textContent="กำลังส่งข้อความทดสอบ…";
  try{
    const r=await (await fetch(q("/test-telegram"),{method:"POST"})).json();
    msg.textContent=r.ok?"ส่งแล้ว เช็กใน Telegram":"ส่งไม่สำเร็จ: "+r.error;
  }catch(e){msg.textContent="เชื่อมต่อสคริปต์ไม่ได้";}
  setTimeout(()=>{msg.textContent="";},12000);
};
function kpi(cls,k,n,s){return '<div class="kpi '+cls+'"><div class="k">'+k+'</div><div class="n">'+n+'</div><div class="s">'+s+'</div></div>';}
function renderSummary(j){
  const today=j.today, ent=Object.entries(j.dates).filter(([d,x])=>d>=today&&x.available!=null);
  const open=ent.filter(([d,x])=>x.available>0);
  const seats=open.reduce((a,[d,x])=>a+x.available,0);
  const wd=Object.keys(j.watch).filter(d=>d>=today);
  const enough=wd.filter(d=>j.dates[d]&&j.dates[d].available>=j.people);
  let oldest=0;
  wd.forEach(d=>{const x=j.dates[d];const age=x&&x.ts?j.server_time-x.ts:Infinity;if(age>oldest)oldest=age;});
  const fresh=wd.length?(oldest===Infinity?"ยังไม่ครบ":ago(oldest)):"-";
  const freshLimit=wd.some(d=>j.watch[d]==="P0")?j.p0_sec:j.p1_sec;
  document.getElementById("kpis").innerHTML=
    kpi(open.length?"good":"","วันที่ยังว่าง",open.length+" วัน","รวม "+seats+" ที่ จาก "+ent.length+" วันที่เช็กแล้ว")+
    kpi(enough.length?"good":(wd.length?"bad":""),"วันที่เฝ้าที่ว่างพอ "+j.people+" คน",enough.length+" / "+wd.length,enough.length?enough.map(thDate).join(", "):"ยังไม่มี")+
    kpi(oldest>freshLimit*2?"mid":"","ข้อมูลวันที่เฝ้าเก่าสุด",fresh,"เป้าหมายไม่เกิน "+freshLimit+" วิ (ตามระดับสูงสุดที่เฝ้า)");
  const rows=[...new Set([...wd,...open.map(([d])=>d)])].sort();
  document.getElementById("rows").innerHTML=rows.length?rows.map(d=>{
    const x=j.dates[d]||{},w=j.watch[d],av=x.available;
    const cls=(av==null?"":av>=j.people?"ok":av>0?"some":"")+(w?" "+w.toLowerCase():"");
    let tg="";
    if(w&&av!=null)tg=av>=j.people?'<span class="tg enough">พอ</span>':'<span class="tg short">ขาด '+(j.people-av)+'</span>';
    const link=av>0?'<a href="'+j.booking_page+'/#d='+d+'&n='+j.people+'" target="doiluang-book" rel="noopener">จอง →</a>':"";
    return '<div class="r '+cls+'"><span class="dt">'+thDate(d)+'</span><span class="av">'+(av==null?"…":av+" / "+(x.capacity||"-"))+'</span>'+(w?'<span>'+w+'</span>':"")+tg+link+'<span class="tm">'+(x.updated||"")+'</span></div>';
  }).join(""):'<div class="hint">ยังไม่มีวันที่เฝ้าหรือวันที่ว่าง</div>';
}
async function toggle(ds){
  if(!isAdmin)return;
  await fetch(q("/toggle?date="+ds),{method:"POST"});
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
  isAdmin=!!j.admin;
  document.querySelector(".tools").style.display=isAdmin?"":"none";
  document.getElementById("ro").style.display=isAdmin?"none":"inline";
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
    const items=[];
    for(let i=0;i<first;i++)items.push(null);
    for(let d=1;d<=days;d++)items.push(d);
    if(y===ey&&m===em){const ed=Number(j.end_date.split("-")[2]);items.length=Math.min(items.length,(Math.floor((first+ed-1)/7)+1)*7);}
    let skipCells=0;
    if(y===ty&&m===tm){const fd=Number(from.split("-")[2]);skipCells=Math.floor((first+fd-1)/7)*7;}
    for(const d of items.slice(skipCells)){
      if(d===null){g.appendChild(document.createElement("div"));continue;}
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
      const xx=j.dates[ds];
      const short=(w&&xx&&xx.available!=null&&xx.available<j.people)?'<span class="sh">ขาด '+(j.people-xx.available)+'</span>':"";
      c.innerHTML='<span class="t1"><span class="d">'+d+'</span><span class="w">'+(w||"")+'</span></span><span class="v">'+v+'</span><span class="foot">'+short+'</span>';
      if(canBook&&!short){
        const a=document.createElement("a");a.className="book";a.textContent="จอง →";
        a.href=j.booking_page+"/#d="+ds+"&n="+j.people;a.target="doiluang-book";a.rel="noopener";
        a.onclick=e=>e.stopPropagation();
        c.querySelector(".foot").appendChild(a);
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
  renderSummary(j);
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
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"[{now()}] คำเตือน: ยังไม่ได้ตั้ง TELEGRAM_TOKEN / TELEGRAM_CHAT_ID (ดูไฟล์ .env) จะไม่มีแจ้งเตือน Telegram")
    if ON_CLOUD and (not ADMIN_KEY or ADMIN_KEY == "เปลี่ยนรหัสนี้"):
        print(f"[{now()}] คำเตือน: รันบน cloud แต่ยังไม่ได้ตั้ง ADMIN_KEY หน้าเว็บจะดูได้อย่างเดียว")
    srv = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://localhost:{PORT}"
    print(f"[{now()}] เปิดปฏิทินที่ {url}  (กด Ctrl+C เพื่อหยุด)")
    if ALLOW_PHONE:
        try:
            import socket
            sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sk.connect(("8.8.8.8", 80))  # ไม่ได้ส่งข้อมูลจริง แค่หา IP ของเครื่องในวง Wi-Fi
            ip = sk.getsockname()[0]
            sk.close()
            print(f"[{now()}] เปิดจากมือถือ (Wi-Fi เดียวกัน): http://{ip}:{PORT}")
        except Exception:
            print(f"[{now()}] หา IP เครื่องไม่ได้ ลองพิมพ์ ipconfig เพื่อดู IPv4 Address")
    if not ON_CLOUD:
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
