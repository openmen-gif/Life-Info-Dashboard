# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.data_fetcher import fetch_weather
from utils.report_downloader import render_download_buttons
import streamlit.components.v1 as components

apply_custom_css()

st.title("🌤️ 날씨 정보 및 기상 레이더")
st.markdown("---")

# ── Settings ─────────────────────────────────────────────────────────────
col_set1, col_set2, col_set3 = st.columns([2, 1, 1])
with col_set1:
    city_input = st.text_input("도시명", value="서울", placeholder="서울, 부산, 인천, Seoul, Busan...")
with col_set2:
    api_key = st.text_input("OpenWeatherMap API Key", type="password", placeholder="선택사항")
with col_set3:
    st.write("") # Vertical alignment spacing
    st.write("")
    update_btn = st.button("날씨 조회 및 갱신", use_container_width=True)

# State Management for city changes
if "last_city" not in st.session_state:
    st.session_state["last_city"] = ""

# Fetch if button clicked OR city text input changed OR init
should_fetch = False
if "weather_data" not in st.session_state:
    should_fetch = True
if update_btn:
    should_fetch = True
if city_input != st.session_state["last_city"]:
    should_fetch = True

if should_fetch:
    st.session_state["weather_data"] = fetch_weather(city=city_input, api_key=api_key if api_key else None)
    st.session_state["last_city"] = city_input

weather = st.session_state["weather_data"]

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

# ── Multi-city comparison & Radar Tabs ───────────────────────────────────
lat = weather.get("lat", 36.5)
lon = weather.get("lon", 127.5)

tab1, tab2, tab3, tab4 = st.tabs(["📊 주요 도시 요약", "🇰🇷 국내 기상 레이더", "🌀 Windy (해당 지역 레이더)", "🌊 Windfinder (해당 지역 맵)"])

with tab1:
    st.markdown("### 주요 도시 비교")
    cities = ["Seoul", "Busan", "Daegu", "Incheon", "Gwangju", "Daejeon"]
    cols = st.columns(len(cities))
    for i, c in enumerate(cities):
        w = fetch_weather(city=c, api_key=api_key if api_key else None)
        with cols[i]:
            st.metric(c, f"{w['temp']}°C", f"{w['desc']}")

with tab2:
    st.markdown("### 🇰🇷 국내 실시간 기상 레이더")
    st.info(
        "한국 전역의 실시간 **강수/레이더** 영상입니다. "
        "지도를 마우스로 확대·이동할 수 있으며, 우측 하단 메뉴에서 레이어(바람·온도·강수 등)를 변경하세요."
    )
    # Windy radar: use searched city coords (zoom 9 = city-level view)
    html_kr_radar = f"""
    <span style="display:none" data-city="{weather['city']}-{lat}-{lon}-kr-radar-v3"></span>
    <iframe
        width="100%"
        height="620"
        src="https://embed.windy.com/embed.html?type=map&location=coordinates&metricRain=mm&metricTemp=%C2%B0C&metricWind=m/s&zoom=9&overlay=radar&product=radar&level=surface&lat={lat}&lon={lon}"
        frameborder="0"
        style="border-radius:8px;">
    </iframe>
    """
    components.html(html_kr_radar, height=640)

    # KMA official radar shortcut
    st.markdown("**기상청 공식 바로가기**")
    kma_cols = st.columns(3)
    with kma_cols[0]:
        st.link_button("🌧️ 기상청 강수 레이더", "https://www.weather.go.kr/w/weather/radar/radar.do", use_container_width=True)
    with kma_cols[1]:
        st.link_button("🌀 기상청 위성 영상", "https://www.weather.go.kr/w/weather/satellite/gk2a.do", use_container_width=True)
    with kma_cols[2]:
        st.link_button("⚡ 기상청 낙뢰 현황", "https://www.weather.go.kr/w/weather/radar/lgt.do", use_container_width=True)

with tab3:
    st.markdown(f"### 🌀 Windy 기상 레이더 - {weather['city']}")
    st.info("실시간 구름 흐름, 비/눈 예측, 바람 방향 등 해당 지역 기상 상황을 동적으로 확인할 수 있습니다. 지도를 마우스로 움직이고 확대/축소해 보세요.")
    # Unique key via hidden span forces Streamlit to re-render iframe when city/coords change
    html_windy = f"""
        <span style="display:none" data-city="{weather['city']}-{lat}-{lon}"></span>
        <iframe width="100%" height="600"
            src="https://embed.windy.com/embed.html?type=map&location=coordinates&metricRain=mm&metricTemp=%C2%B0C&metricWind=m/s&zoom=8&overlay=wind&product=ecmwf&level=surface&lat={lat}&lon={lon}"
            frameborder="0"></iframe>
    """
    components.html(html_windy, height=620)

with tab4:
    st.markdown(f"### 🌊 Windfinder 바람/파도 범위 - {weather['city']}")
    st.info("정밀한 풍속, 조류, 파도 높이 등의 관측에 특화된 지도입니다. 우측 상단의 메뉴를 통해 보고자 하는 필터를 변경할 수 있습니다.")
    html_windfinder = f"""
        <span style="display:none" data-city="{weather['city']}-{lat}-{lon}"></span>
        <iframe width="100%" height="600"
            src="https://ko.windfinder.com/weather-maps/forecast/wind/sea_of_japan#{8}/{lat}/{lon}"
            frameborder="0"></iframe>
    """
    components.html(html_windfinder, height=620)

# ── 보고서 다운로드 ────────────────────────────────────────────────────────
st.markdown("---")
weather_context = {
    "query": f"{weather.get('city', city_input)} 날씨 정보",
    "news": [],
    "web": [],
    "df": [{"도시": weather.get("city", city_input), "기온": weather["temp"],
            "체감온도": weather["feels_like"], "습도": weather["humidity"],
            "풍속": weather["wind_speed"], "상태": weather["desc"]}],
}
render_download_buttons(context=weather_context)
