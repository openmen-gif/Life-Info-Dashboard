FROM python:3.11-slim

WORKDIR /app

COPY packages.txt .
RUN apt-get update \
    && xargs -a packages.txt apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

ENV STREAMLIT_SERVER_PORT=7860
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV LIFE_MODE=standalone
# Build trigger: 2026-03-08T19:54 (fresh cache bust)

CMD ["streamlit", "run", "Dashboard.py", \
     "--server.port=7860", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
