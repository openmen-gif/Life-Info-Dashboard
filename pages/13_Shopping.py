# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="쇼핑/소비",
    icon="🛍️",
    default_query="글로벌 국내 온라인 쇼핑 소비 트렌드",
    tickers={
        "AMZN": "아마존",
        "CPNG": "쿠팡",
        "EBAY": "이베이",
    },
    auto_news_query="온라인 쇼핑 소비자 물가 할인",
    external_links=[
        ("🛒 소비자물가지수", "https://kostat.go.kr/"),
        ("📊 한국소비자원", "https://www.kca.go.kr/"),
        ("🛍️ 네이버 쇼핑", "https://shopping.naver.com/"),
    ],
)
