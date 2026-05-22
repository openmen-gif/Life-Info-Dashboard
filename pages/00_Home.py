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
st.markdown("## 📚 전체 카테고리 (38개 페이지)")
st.caption("카테고리 안의 항목을 클릭하면 해당 페이지로 이동합니다. 사이드바에서도 그룹별로 탐색 가능합니다.")

# (카테고리 제목, [(페이지 파일, 표시 라벨, 아이콘), ...])
_categories = [
    ("🚨 안전·재난·정책", [
        ("pages/33_Safety.py", "재난·안전", "🚨"),
        ("pages/36_CyberSecurity.py", "사이버 보안", "🛡️"),
        ("pages/34_PublicUtility.py", "공공요금", "💡"),
        ("pages/35_Policy.py", "정부 정책", "🏛️"),
        ("pages/31_Environment.py", "환경/에너지", "🌱"),
        ("pages/11_Legal.py", "생활법률", "⚖️"),
    ]),
    ("🌤️ 일상·생활", [
        ("pages/01_Weather.py", "날씨", "🌤️"),
        ("pages/02_News.py", "뉴스", "📰"),
        ("pages/03_Traffic.py", "교통", "🚗"),
        ("pages/07_Food.py", "식생활", "🍽️"),
        ("pages/13_Shopping.py", "쇼핑/소비", "🛍️"),
        ("pages/10_Travel.py", "여행", "✈️"),
    ]),
    ("🏥 건강·가족", [
        ("pages/06_Health.py", "건강", "🏥"),
        ("pages/30_Insurance.py", "보험/연금", "🛡️"),
        ("pages/14_Parenting.py", "육아/보육", "👶"),
        ("pages/09_Education.py", "교육", "📚"),
        ("pages/37_Demography.py", "인구·결혼", "👰"),
        ("pages/38_Silver.py", "실버산업", "👴"),
    ]),
    ("🏠 부동산·자동차", [
        ("pages/08_RealEstate.py", "부동산", "🏠"),
        ("pages/29_Car.py", "자동차", "🚗"),
    ]),
    ("💰 금융·투자", [
        ("pages/05_Finance.py", "생활금융", "💰"),
        ("pages/12_Stock.py", "주식 분석", "📈"),
        ("pages/18_Exchange.py", "환율/유가", "💱"),
        ("pages/32_Crypto.py", "암호화폐", "🪙"),
    ]),
    ("🏢 비즈니스", [
        ("pages/20_Business.py", "사업/창업", "🏢"),
        ("pages/19_Customs.py", "관세/무역", "🚢"),
        ("pages/21_Transport.py", "운송/물류", "🚚"),
        ("pages/25_Tech.py", "IT/테크", "💻"),
        ("pages/26_Jobs.py", "취업/채용", "💼"),
    ]),
    ("🎬 문화·여가", [
        ("pages/15_Culture.py", "문화/예술", "🎭"),
        ("pages/28_Entertainment.py", "연예/엔터", "🎬"),
        ("pages/27_Sports.py", "스포츠", "⚽"),
        ("pages/16_Pet.py", "반려동물", "🐾"),
        ("pages/17_Flower.py", "화훼/식물", "🌷"),
    ]),
    ("🌍 글로벌", [
        ("pages/22_GlobalWar.py", "해외 분쟁/전쟁", "🌍"),
    ]),
    ("🛠️ 도구", [
        ("pages/04_Data_Collector.py", "데이터 수집 (마스터 리포트)", "📊"),
    ]),
]

_cat_cols = st.columns(3)
for i, (cat_title, page_items) in enumerate(_categories):
    with _cat_cols[i % 3]:
        with st.container(border=True):
            st.markdown(f"**{cat_title}**")
            for page_path, label, icon in page_items:
                try:
                    st.page_link(page_path, label=label, icon=icon)
                except Exception:
                    # page_link 실패(미등록 페이지 등) 시 텍스트 표시로 폴백
                    st.markdown(f"<small style='color:#9CA3AF'>{icon} {label}</small>", unsafe_allow_html=True)
