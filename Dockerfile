FROM python:3.11-slim

WORKDIR /app

# 시스템 패키지 (변경 빈도 낮음 → 레이어 캐시 활용)
COPY packages.txt .
RUN apt-get update \
    && xargs -a packages.txt apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 (변경 빈도 중간 → 별도 레이어)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 (변경 빈도 높음 → 마지막 레이어, 세분화)
COPY utils/ utils/
COPY pages/ pages/
COPY skill_md/ skill_md/
COPY Dashboard.py .
COPY .gitignore .

EXPOSE 7860

ENV STREAMLIT_SERVER_PORT=7860
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV LIFE_MODE=standalone

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:7860/_stcore/health || exit 1

CMD ["streamlit", "run", "Dashboard.py", \
     "--server.port=7860", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.enableCORS=false", \
     "--server.fileWatcherType=none"]
