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
traffic = fetch_traffic_status()
render_traffic_summary(traffic, limit=4)

_tc1, _tc2, _tc3 = st.columns(3)
with _tc1:
    st.link_button("🗺️ 네이버 지도 (교통)", "https://map.naver.com/p?c=15.00,0,0,0,dh&mapMode=0&trafficMode=1", use_container_width=True)
with _tc2:
    st.link_button("🗺️ 카카오맵", "https://map.kakao.com/", use_container_width=True)
with _tc3:
    st.link_button("🚗 ITS 실시간 교통", "https://www.its.go.kr/", use_container_width=True)

st.markdown("---")
render_download_buttons()

# ── 관련 영상 ─────────────────────────────────────────────────────
st.markdown("---")
_today_str = datetime.datetime.now().strftime("%Y년 %m월 %d일")
st.markdown(f"## 🎬 {_today_str} 생활정보 영상")
from utils.expert_template import render_youtube_section
_yt_home = render_youtube_section("오늘 뉴스 시사 경제", sort="latest")

st.markdown("---")
st.markdown("## 📚 전체 카테고리")
st.caption("사이드바에서 원하는 페이지를 선택하세요.")

_categories = [
    ("🌤️ 날씨·교통", ["날씨", "뉴스", "교통"]),
    ("💰 금융·투자", ["생활금융", "주식 분석", "환율 분석", "유가&환율", "암호화폐"]),
    ("🏥 생활·건강", ["건강", "식생활", "보험/연금", "생활법률", "육아/보육"]),
    ("🏠 부동산·자동차", ["부동산", "자동차", "교육"]),
    ("🛍️ 소비·문화", ["쇼핑/소비", "문화/예술", "여행", "연예/엔터", "스포츠"]),
    ("🐾 취미·라이프", ["반려동물", "화훼/식물", "환경/에너지"]),
    ("🏢 비즈니스", ["사업/창업", "관세/무역", "운송/물류", "IT/테크", "취업/채용"]),
    ("🌍 글로벌", ["해외 분쟁/전쟁"]),
]

_cat_cols = st.columns(4)
for i, (cat_title, pages) in enumerate(_categories):
    with _cat_cols[i % 4]:
        page_list = " · ".join(pages)
        st.markdown(
            f"**{cat_title}**\n\n"
            f"<small style='color:#9CA3AF'>{page_list}</small>",
            unsafe_allow_html=True,
        )
        st.markdown("")
