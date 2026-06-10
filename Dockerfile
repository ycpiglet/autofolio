FROM python:3.11-slim

WORKDIR /app

# 의존성 먼저 설치 (캐시 최적화)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 복사
COPY . .

# DB 초기화
RUN python scripts/init_db.py

EXPOSE 8501

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["streamlit", "run", "app/ui/autofolio_app.py", \
            "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
