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
    sub_topics=[
        ("🏖️", "국내여행", "국내 여행 명소 숙소 맛집 추천"),
        ("🌏", "해외여행", "해외여행 항공권 특가 비자 입국"),
        ("🏨", "숙소/호텔", "호텔 리조트 호캉스 에어비앤비 펜션"),
        ("✈️", "항공/교통", "항공권 LCC 특가 고속철도 렌터카"),
        ("🎒", "배낭/체험", "배낭여행 체험 액티비티 투어 축제"),
    ],
    auto_news_query="여행 관광 항공권 특가 해외여행",
    external_links=[
        ("✈️ 스카이스캐너", "https://www.skyscanner.co.kr/"),
        ("🌍 해외안전여행", "https://www.0404.go.kr/"),
        ("🏨 한국관광공사", "https://korean.visitkorea.or.kr/"),
    ],
)
