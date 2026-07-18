# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css

st.set_page_config(
    page_title="Life Info Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed",
)
apply_custom_css()

# ── Navigation ───────────────────────────────────────────────────────────
# 사이드바 그룹화 — 38개 페이지를 의미별로 9개 그룹으로 분류해 가독성 확보
pages = {
    "메인": [
        st.Page("views/00_Home.py", title="홈", icon="🏠"),
    ],
    "🌤️ 일상·생활": [
        st.Page("views/01_Weather.py", title="날씨", icon="🌤️"),
        st.Page("views/02_News.py", title="뉴스", icon="📰"),
        st.Page("views/03_Traffic.py", title="교통", icon="🚗"),
        st.Page("views/07_Food.py", title="식생활", icon="🍽️"),
        st.Page("views/13_Shopping.py", title="쇼핑/소비", icon="🛍️"),
        st.Page("views/10_Travel.py", title="여행", icon="✈️"),
    ],
    "💰 금융·투자": [
        st.Page("views/05_Finance.py", title="생활금융", icon="💰"),
        st.Page("views/12_Stock.py", title="주식 분석", icon="📈"),
        st.Page("views/18_Exchange.py", title="환율/유가", icon="💱"),
        st.Page("views/32_Crypto.py", title="암호화폐", icon="🪙"),
    ],
    "🚨 안전·재난·정책": [
        st.Page("views/33_Safety.py", title="재난·안전", icon="🚨"),
        st.Page("views/36_CyberSecurity.py", title="사이버 보안", icon="🛡️"),
        st.Page("views/34_PublicUtility.py", title="공공요금", icon="💡"),
        st.Page("views/35_Policy.py", title="정부 정책", icon="🏛️"),
        st.Page("views/31_Environment.py", title="환경/에너지", icon="🌱"),
        st.Page("views/11_Legal.py", title="생활법률", icon="⚖️"),
    ],
    "🏠 부동산·자동차": [
        st.Page("views/08_RealEstate.py", title="부동산", icon="🏠"),
        st.Page("views/29_Car.py", title="자동차", icon="🚗"),
    ],
    "🏥 건강·가족": [
        st.Page("views/06_Health.py", title="건강", icon="🏥"),
        st.Page("views/30_Insurance.py", title="보험/연금", icon="🛡️"),
        st.Page("views/14_Parenting.py", title="육아/보육", icon="👶"),
        st.Page("views/09_Education.py", title="교육", icon="📚"),
        st.Page("views/37_Demography.py", title="인구·결혼", icon="👰"),
        st.Page("views/38_Silver.py", title="실버산업", icon="👴"),
    ],
    "🏢 비즈니스": [
        st.Page("views/20_Business.py", title="사업/창업", icon="🏢"),
        st.Page("views/19_Customs.py", title="관세/무역", icon="🚢"),
        st.Page("views/21_Transport.py", title="운송/물류", icon="🚚"),
        st.Page("views/25_Tech.py", title="IT/테크", icon="💻"),
        st.Page("views/26_Jobs.py", title="취업/채용", icon="💼"),
    ],
    "🎬 문화·여가": [
        st.Page("views/15_Culture.py", title="문화/예술", icon="🎭"),
        st.Page("views/28_Entertainment.py", title="연예/엔터", icon="🎬"),
        st.Page("views/27_Sports.py", title="스포츠", icon="⚽"),
        st.Page("views/16_Pet.py", title="반려동물", icon="🐾"),
        st.Page("views/17_Flower.py", title="화훼/식물", icon="🌷"),
    ],
    "🌍 글로벌": [
        st.Page("views/22_GlobalWar.py", title="해외 분쟁/전쟁", icon="🌍"),
    ],
    "🛠️ 도구": [
        st.Page("views/04_Data_Collector.py", title="데이터 수집", icon="📊"),
    ],
}

nav = st.navigation(pages)
nav.run()
