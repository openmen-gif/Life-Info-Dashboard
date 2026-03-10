# -*- coding: utf-8 -*-
"""교통 정보 — 실시간 교통 + 버스 위치 + 교통 뉴스 + 관련 영상"""
import streamlit as st
import streamlit.components.v1 as components
from utils.css_loader import apply_custom_css
from utils.data_fetcher import fetch_news_search
from utils.report_downloader import render_download_buttons

apply_custom_css()

st.title("🚗 교통 정보")
st.markdown("---")

# ── 실시간 교통 지도 바로가기 ─────────────────────────────────────────
st.markdown("### 🗺️ 실시간 교통 지도")
st.info("버튼을 눌러 실시간 교통 상황을 확인하세요. (새 탭)")

c1, c2, c3 = st.columns(3)
with c1:
    st.link_button("🗺️ 네이버 지도 (교통)", "https://map.naver.com/p?c=15.00,0,0,0,dh&mapMode=0&trafficMode=1", use_container_width=True)
with c2:
    st.link_button("🗺️ 카카오맵", "https://map.kakao.com/", use_container_width=True)
with c3:
    st.link_button("🚗 ITS 실시간 교통", "https://www.its.go.kr/", use_container_width=True)

# ── Google Maps 한국 교통 ────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🌐 전국 교통 지도")
components.html(
    '<iframe src="https://www.google.com/maps/embed?pb=!1m14!1m12!1m3!1d1600000!2d127.0!3d36.5!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!5e0!3m2!1sko!2skr!4v1" '
    'width="100%" height="480" frameborder="0" style="border-radius:8px;" allowfullscreen loading="lazy"></iframe>',
    height=500,
)

# ── 버스 실시간 위치 ──────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🚌 버스 실시간 위치 조회")
st.info("버스 번호를 입력하면 해당 버스의 실시간 위치와 정류장 정보를 확인할 수 있습니다.")

bus_col1, bus_col2 = st.columns([2, 1])
with bus_col1:
    bus_number = st.text_input("버스 번호 입력", placeholder="예: 146, 360, 9703, M6405...")
with bus_col2:
    st.write("")
    st.write("")
    bus_region = st.selectbox("지역", ["서울", "경기", "인천", "부산", "대구", "대전", "광주"])

_BUS_SEARCH_URLS = {
    "서울": "https://bus.go.kr/app/#viewpage/1000001/main.nearbusinfo/1/title=Home%20%EB%B2%84%EC%8A%A4%EC%A0%95%EB%B3%B4",
    "경기": "https://www.gbis.go.kr/",
    "인천": "https://bus.incheon.go.kr/",
    "부산": "https://bus.busan.go.kr/",
    "대구": "https://businfo.daegu.go.kr/",
    "대전": "https://bus.daejeon.go.kr/",
    "광주": "https://bus.gjcity.go.kr/",
}

if bus_number:
    base_url = _BUS_SEARCH_URLS.get(bus_region, _BUS_SEARCH_URLS["서울"])
    search_url = f"{base_url}{bus_number}"
    st.link_button(
        f"🔍 {bus_region} {bus_number}번 버스 실시간 위치 확인",
        search_url,
        use_container_width=True,
    )

# 버스 정보 바로가기
st.markdown("**버스 정보 서비스**")
bc1, bc2, bc3 = st.columns(3)
with bc1:
    st.link_button("🚌 서울버스 (bus.go.kr)", "https://bus.go.kr/", use_container_width=True)
    st.link_button("🚌 경기버스 (GBIS)", "https://www.gbis.go.kr/", use_container_width=True)
with bc2:
    st.link_button("🚌 인천버스", "https://bus.incheon.go.kr/", use_container_width=True)
    st.link_button("🚌 부산버스", "https://bus.busan.go.kr/", use_container_width=True)
with bc3:
    st.link_button("🚇 서울교통공사", "https://www.seoulmetro.co.kr/", use_container_width=True)
    st.link_button("🚄 코레일(KTX)", "https://www.letskorail.com/", use_container_width=True)

# ── 고속도로/도로 정보 ────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🛣️ 고속도로/도로 정보")
hc1, hc2, hc3 = st.columns(3)
with hc1:
    st.link_button("🛣️ 한국도로공사", "https://www.ex.co.kr/", use_container_width=True)
with hc2:
    st.link_button("📊 고속도로 교통량", "https://data.ex.co.kr/", use_container_width=True)
with hc3:
    st.link_button("✈️ 인천공항", "https://www.airport.kr/", use_container_width=True)

# ── 교통 뉴스 ──────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📰 교통 관련 뉴스")
_traffic_news = fetch_news_search("교통 도로 고속도로 상황", limit=8)
if _traffic_news:
    for i, item in enumerate(_traffic_news):
        src = f" ({item['source']})" if item.get("source") else ""
        st.markdown(f"**{i+1}.** [{item['title']}]({item['link']}){src}")
        if item.get("snippet"):
            st.caption(item["snippet"])
else:
    st.info("교통 뉴스를 불러올 수 없습니다.")

# ── 관련 영상 ──────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🎬 교통 관련 최신 영상")
from utils.expert_template import render_youtube_section
_yt_traffic = render_youtube_section("교통 도로 고속도로", sort="latest")

# ── 보고서 다운로드 ────────────────────────────────────────────────────
st.markdown("---")
_context = {
    "query": "교통 정보",
    "news": _traffic_news,
    "web": [],
    "youtube": _yt_traffic,
    "df": [],
}
render_download_buttons(context=_context)
