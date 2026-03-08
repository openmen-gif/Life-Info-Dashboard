# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css

st.set_page_config(
    page_title="Life Info Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
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
    ],
    "도구": [
        st.Page("pages/04_Data_Collector.py", title="데이터 수집", icon="📊"),
    ],
}

nav = st.navigation(pages)
nav.run()
