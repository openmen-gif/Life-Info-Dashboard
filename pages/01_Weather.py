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
    st.warning(
        "⚠️ 실시간 날씨 데이터를 가져오지 못해 임시 데이터를 표시합니다. "
        "인터넷 연결을 확인하거나, **[날씨 조회 및 갱신]** 버튼을 다시 눌러주세요. "
        "정밀 데이터가 필요하면 [무료 OpenWeatherMap API 키](https://openweathermap.org/api)를 발급받아 입력하세요."
    )

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
    st.markdown("### 🇰🇷 국내 실시간 기상 레이더 (Rainviewer)")
    st.info(
        "인터랙티브 강수 레이더 — 확대/축소·시간 재생 가능. "
        "기상청(KMA) 공식 레이더·위성·낙뢰는 아래 **바로가기**로 새 창에서 열립니다."
    )
    # 기상청 정적 합성 PNG(rdr_CMP_HSP_PUB_FQC.png)는 KMA 가 경로를 폐기해 이미지 대신
    # text/html 에러("서비스 이용에 불편을 드려 죄송합니다")를 반환하므로 제거했다.
    # 임베드 레이더는 Rainviewer(X-Frame-Options: ALLOWALL)로 대체하고, KMA 공식
    # 레이더는 하단 바로가기 링크(새 창)로 제공한다.

    # Rainviewer 인터랙티브 강수 레이더
    html_rv = f"""
    <span style="display:none" data-city="{weather['city']}-{lat}-{lon}-rv"></span>
    <iframe
        width="100%"
        height="560"
        src="https://www.rainviewer.com/map.html?loc={lat},{lon},8&oCS=1&oF=0&oAP=1&c=3&o=83&lm=1&layer=radar-1h&sm=1&sn=1"
        frameborder="0"
        style="border-radius:8px;">
    </iframe>
    """
    components.html(html_rv, height=580)

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
    st.markdown(f"### 🌊 Windfinder 바람·파도 예보 - {weather['city']}")

    # Windfinder spot slug 변환: KOR_CITY_MAP 영문화 → lowercase, 공백/하이픈 → underscore
    from utils.data_fetcher import KOR_CITY_MAP as _KCM
    _eng = _KCM.get(weather['city'].strip(), weather['city'].strip())
    _spot = _eng.lower().replace(' ', '_').replace('-', '_').replace('.', '')

    st.info(
        "Windfinder 공식 위젯으로 해당 위치의 정밀 **풍속·풍향·돌풍·파도** 예보를 표시합니다. "
        "Windfinder는 해변·항구 등 spot 단위로 운영되어 일부 도시만 등록되어 있습니다 "
        "(예: 서울·창원·뉴욕·시드니·런던·파리). 미등록 도시는 하단 외부 링크에서 직접 검색하세요."
    )

    html_wf = f"""
        <span style="display:none" data-city="{weather['city']}-{_spot}-wf"></span>
        <iframe width="100%" height="650"
            src="https://www.windfinder.com/widget/forecast/{_spot}"
            frameborder="0"
            style="border-radius:8px;">
        </iframe>
    """
    components.html(html_wf, height=670)

    # 외부 해상 기상 사이트 바로가기
    st.markdown("**해상·바람 정밀 분석 사이트 바로가기**")
    ext_cols = st.columns(3)
    with ext_cols[0]:
        st.link_button("🔍 Windfinder 검색",
                       f"https://www.windfinder.com/search?q={_eng}",
                       use_container_width=True)
    with ext_cols[1]:
        st.link_button("🌀 Windy 파도 차트",
                       f"https://www.windy.com/?waves,{lat},{lon},8",
                       use_container_width=True)
    with ext_cols[2]:
        st.link_button("⚓ 기상청 해양기상",
                       "https://www.weather.go.kr/w/weather/ocean.do",
                       use_container_width=True)

# ── 관련 영상 ─────────────────────────────────────────────────────
st.markdown("---")
import datetime as _dt
_today_w = _dt.datetime.now().strftime("%Y년 %m월 %d일")
st.markdown(f"## 🎬 {_today_w} 날씨·기상 영상")
from utils.expert_template import render_youtube_section
_yt_weather = render_youtube_section("오늘 날씨 일기예보", sort="latest")

# ── 보고서 다운로드 ────────────────────────────────────────────────────────
st.markdown("---")
weather_context = {
    "query": f"{weather.get('city', city_input)} 날씨 정보",
    "news": [],
    "web": [],
    "youtube": _yt_weather,
    "df": [{"도시": weather.get("city", city_input), "기온": weather["temp"],
            "체감온도": weather["feels_like"], "습도": weather["humidity"],
            "풍속": weather["wind_speed"], "상태": weather["desc"]}],
}
render_download_buttons(context=weather_context)
