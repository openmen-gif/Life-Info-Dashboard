# -*- coding: utf-8 -*-
import streamlit as st
import datetime
import json
import os
from utils.css_loader import apply_custom_css
from utils.data_fetcher import fetch_weather, fetch_news, fetch_traffic_status

apply_custom_css()

st.title("📊 데이터 수집기")
st.markdown("---")

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "collected_data"))
os.makedirs(DATA_DIR, exist_ok=True)

st.markdown("### 수집 대상 선택")
col1, col2 = st.columns(2)

with col1:
    collect_weather = st.checkbox("🌤️ 날씨 데이터", value=True)
    collect_news = st.checkbox("📰 뉴스 데이터", value=True)
    collect_traffic = st.checkbox("🚗 교통 데이터", value=True)

with col2:
    weather_city = st.text_input("날씨 도시", value="Seoul")
    news_category = st.selectbox("뉴스 카테고리", ["종합", "IT/과학", "경제", "생활"])

st.markdown("---")

if st.button("📥 데이터 수집 실행", type="primary", use_container_width=True):
    collected = {}
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    with st.spinner("데이터 수집 중..."):
        if collect_weather:
            collected["weather"] = fetch_weather(city=weather_city)
            st.success(f"✅ 날씨 데이터 수집 완료 — {weather_city}")

        if collect_news:
            collected["news"] = fetch_news(category=news_category, limit=20)
            st.success(f"✅ 뉴스 데이터 수집 완료 — {news_category} ({len(collected['news'])}건)")

        if collect_traffic:
            collected["traffic"] = fetch_traffic_status()
            st.success(f"✅ 교통 데이터 수집 완료 — {len(collected['traffic'])}개 노선")

    # Save
    collected["_meta"] = {
        "timestamp": timestamp,
        "collected_at": datetime.datetime.now().isoformat(),
    }
    out_path = os.path.join(DATA_DIR, f"life_data_{timestamp}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(collected, f, ensure_ascii=False, indent=2)

    st.success(f"💾 저장 완료: `{out_path}`")

    # Download button
    st.download_button(
        label="📥 JSON 다운로드",
        data=json.dumps(collected, ensure_ascii=False, indent=2),
        file_name=f"life_data_{timestamp}.json",
        mime="application/json",
    )

# ── Collected data history ───────────────────────────────────────────────
st.markdown("---")
st.markdown("### 수집 이력")
if os.path.exists(DATA_DIR):
    files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith(".json")], reverse=True)
    if files:
        for f in files[:10]:
            st.text(f"📄 {f}")
    else:
        st.info("아직 수집된 데이터가 없습니다.")
