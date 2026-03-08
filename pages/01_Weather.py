# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.data_fetcher import fetch_weather

apply_custom_css()

st.title("🌤️ 날씨 정보")
st.markdown("---")

# ── Settings ─────────────────────────────────────────────────────────────
col_set1, col_set2 = st.columns([2, 1])
with col_set1:
    city = st.text_input("도시명 (영문)", value="Seoul", placeholder="Seoul, Busan, Incheon...")
with col_set2:
    api_key = st.text_input("OpenWeatherMap API Key", type="password", placeholder="선택사항")

weather = fetch_weather(city=city, api_key=api_key if api_key else None)

# ── Current Weather ──────────────────────────────────────────────────────
st.markdown("### 현재 날씨")
c1, c2, c3, c4 = st.columns(4)
c1.metric("🌡️ 기온", f"{weather['temp']}°C")
c2.metric("🤔 체감온도", f"{weather['feels_like']}°C")
c3.metric("💧 습도", f"{weather['humidity']}%")
c4.metric("💨 풍속", f"{weather['wind_speed']} m/s")

st.markdown(f"**상태**: {weather['desc']}")
st.caption(f"마지막 업데이트: {weather['updated']}")

if weather.get("_sample"):
    st.warning("⚠️ OpenWeatherMap API 키가 없어 샘플 데이터를 표시합니다. "
               "[무료 API 키 발급](https://openweathermap.org/api)")

st.markdown("---")

# ── Multi-city comparison ────────────────────────────────────────────────
st.markdown("### 주요 도시 비교")
cities = ["Seoul", "Busan", "Daegu", "Incheon", "Gwangju", "Daejeon"]
cols = st.columns(len(cities))
for i, c in enumerate(cities):
    w = fetch_weather(city=c, api_key=api_key if api_key else None)
    with cols[i]:
        st.metric(c, f"{w['temp']}°C", f"{w['desc']}")
