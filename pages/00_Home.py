# -*- coding: utf-8 -*-
import streamlit as st
import datetime
from utils.css_loader import apply_custom_css
from utils.data_fetcher import fetch_weather, fetch_news, fetch_traffic_status
from utils.ui_components import render_weather_card, render_news_summary, render_traffic_summary
from utils.report_downloader import render_download_buttons

apply_custom_css()

st.title("🏠 생활정보 대시보드")
st.caption(f"📅 {datetime.datetime.now().strftime('%Y년 %m월 %d일 %A')}")
st.markdown("---")

# ── Quick Summary Row ────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

# Weather summary
with col1:
    weather = fetch_weather()
    render_weather_card(weather)

# News summary
with col2:
    news = fetch_news("종합", limit=5)
    render_news_summary(news, limit=5)

# Traffic summary
with col3:
    traffic = fetch_traffic_status()
    render_traffic_summary(traffic, limit=5)

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
