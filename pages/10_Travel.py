# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="여행",
    icon="✈️",
    default_query="국내 명소 여행지 호캉스 해외 관광 항공권 추천",
    tickers={
        "JETS": "항공산업ETF",
        "MAR": "메리어트호텔",
        "BKNG": "부킹홀딩스",
    },
    auto_news_query="여행 관광 항공권 특가 해외여행",
    external_links=[
        ("✈️ 스카이스캐너", "https://www.skyscanner.co.kr/"),
        ("🌍 해외안전여행", "https://www.0404.go.kr/"),
        ("🏨 한국관광공사", "https://korean.visitkorea.or.kr/"),
    ],
)
