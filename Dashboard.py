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
pages = {
    "메인": [
        st.Page("pages/00_Home.py", title="홈", icon="🏠"),
    ],
    "생활정보": [
        st.Page("pages/01_Weather.py", title="날씨", icon="🌤️"),
        st.Page("pages/02_News.py", title="뉴스", icon="📰"),
        st.Page("pages/03_Traffic.py", title="교통", icon="🚗"),
        st.Page("pages/05_Finance.py", title="생활금융", icon="💰"),
        st.Page("pages/06_Health.py", title="건강", icon="🏥"),
        st.Page("pages/07_Food.py", title="식생활", icon="🍽️"),
        st.Page("pages/08_RealEstate.py", title="부동산", icon="🏠"),
        st.Page("pages/09_Education.py", title="교육", icon="📚"),
        st.Page("pages/10_Travel.py", title="여행", icon="✈️"),
        st.Page("pages/11_Legal.py", title="생활법률", icon="⚖️"),
        st.Page("pages/12_Stock.py", title="주식 분석", icon="📈"),
        st.Page("pages/13_Shopping.py", title="쇼핑/소비", icon="🛍️"),
        st.Page("pages/14_Parenting.py", title="육아/보육", icon="👶"),
        st.Page("pages/15_Culture.py", title="문화/예술", icon="🎭"),
        st.Page("pages/16_Pet.py", title="반려동물", icon="🐾"),
        st.Page("pages/17_Flower.py", title="화훼/식물", icon="🌷"),
        st.Page("pages/18_Exchange.py", title="환율/유가", icon="💱"),
        st.Page("pages/19_Customs.py", title="관세/무역", icon="🚢"),
        st.Page("pages/20_Business.py", title="사업/창업", icon="🏢"),
        st.Page("pages/21_Transport.py", title="운송/물류", icon="🚚"),
        st.Page("pages/22_GlobalWar.py", title="해외 분쟁/전쟁", icon="🌍"),
        st.Page("pages/25_Tech.py", title="IT/테크", icon="💻"),
        st.Page("pages/26_Jobs.py", title="취업/채용", icon="💼"),
        st.Page("pages/27_Sports.py", title="스포츠", icon="⚽"),
        st.Page("pages/28_Entertainment.py", title="연예/엔터", icon="🎬"),
        st.Page("pages/29_Car.py", title="자동차", icon="🚗"),
        st.Page("pages/30_Insurance.py", title="보험/연금", icon="🛡️"),
        st.Page("pages/31_Environment.py", title="환경/에너지", icon="🌱"),
        st.Page("pages/32_Crypto.py", title="암호화폐", icon="🪙"),
    ],
    "도구": [
        st.Page("pages/04_Data_Collector.py", title="데이터 수집", icon="📊"),
    ],
}

nav = st.navigation(pages)
nav.run()
