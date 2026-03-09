# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="식생활",
    icon="🍽️",
    default_query="글로벌 외식 국내 맛집 요리 트렌드",
    tickers={
        "CORN": "옥수수ETF",
        "WEAT": "밀ETF",
        "SOYB": "대두ETF",
    },
    auto_news_query="외식 물가 식품 안전 먹거리",
    external_links=[
        ("🍚 식품안전나라", "https://www.foodsafetykorea.go.kr/"),
        ("📊 농산물유통정보", "https://www.kamis.or.kr/"),
        ("🛒 소비자물가 통계", "https://kostat.go.kr/"),
    ],
)
