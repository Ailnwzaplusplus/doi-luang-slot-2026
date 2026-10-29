FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY calendar_doiluang.py watch_dates.json ./

# ผู้ให้บริการส่วนใหญ่กำหนด PORT มาเอง (Hugging Face Spaces ใช้ 7860)
ENV PORT=7860 PYTHONUNBUFFERED=1
EXPOSE 7860

CMD ["python", "calendar_doiluang.py"]
