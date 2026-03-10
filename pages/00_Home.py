# -*- coding: utf-8 -*-
import streamlit as st
import datetime
import streamlit.components.v1 as components
from utils.css_loader import apply_custom_css
from utils.data_fetcher import fetch_weather, fetch_news
from utils.ui_components import render_weather_card, render_news_summary
from utils.report_downloader import render_download_buttons

apply_custom_css()

st.title("🏠 생활정보 대시보드")
st.caption(f"📅 {datetime.datetime.now().strftime('%Y년 %m월 %d일 %A')}")
st.markdown("---")

# ── Quick Summary Row ────────────────────────────────────────────────────
col1, col2 = st.columns(2)

# Weather summary
with col1:
    weather = fetch_weather()
    render_weather_card(weather)

# News summary
with col2:
    news = fetch_news("종합", limit=5)
    render_news_summary(news, limit=5)

# ── 실시간 교통 ──────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🚗 실시간 교통 지도")
_traffic_tab1, _traffic_tab2 = st.tabs(["🗺️ 네이버 지도", "🗺️ 카카오맵"])
with _traffic_tab1:
    components.html(
        '<iframe src="https://map.naver.com/p?c=15.00,0,0,0,dh&mapMode=0&trafficMode=1" '
        'width="100%" height="450" frameborder="0" style="border-radius:8px;"></iframe>',
        height=470,
    )
with _traffic_tab2:
    components.html(
        '<iframe src="https://map.kakao.com/?map_type=TYPE_MAP&map_attribute=ROADVIEW&urlLevel=10&urlX=497065&urlY=1105314" '
        'width="100%" height="450" frameborder="0" style="border-radius:8px;"></iframe>',
        height=470,
    )
_tc1, _tc2, _tc3 = st.columns(3)
with _tc1:
    st.link_button("🚗 ITS 실시간 교통", "https://www.its.go.kr/", use_container_width=True)
with _tc2:
    st.link_button("🛣️ 한국도로공사", "https://www.ex.co.kr/", use_container_width=True)
with _tc3:
    st.link_button("🚌 서울TOPIS", "https://topis.seoul.go.kr/", use_container_width=True)

st.markdown("---")
render_download_buttons()

# ── 관련 영상 ─────────────────────────────────────────────────────
st.markdown("---")
_today_str = datetime.datetime.now().strftime("%Y년 %m월 %d일")
st.markdown(f"## 🎬 {_today_str} 생활정보 영상")
from utils.expert_template import render_youtube_section
_yt_home = render_youtube_section("오늘 뉴스 시사 경제", sort="latest")

st.markdown("---")
st.info("💡 왼쪽 사이드바에서 **날씨**, **뉴스**, **교통** 상세 페이지를 확인하세요.")
