FROM python:3.11-slim

WORKDIR /app

# 의존성 먼저 설치 (캐시 최적화)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 복사
COPY . .

# DB 초기화
RUN python scripts/init_db.py

EXPOSE 8000

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "uvicorn app.api.main:create_app --factory --host 0.0.0.0 --port ${PORT:-8000}"]
