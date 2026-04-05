# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="식생활",
    icon="🍽️",
    default_query="글로벌 외식 국내 맛집 요리 트렌드",
    sub_topics=[
        ("🍜", "맛집/외식", "맛집 추천 외식 레스토랑 카페 트렌드"),
        ("🛒", "식료품/물가", "식료품 물가 장바구니 마트 가격"),
        ("🥗", "건강식/다이어트", "건강식 다이어트 식단 저칼로리 비건"),
        ("🍳", "요리/레시피", "요리 레시피 홈쿡 간편식 밀키트"),
        ("⚠️", "식품안전", "식품 안전 리콜 위생 식중독 유통기한"),
    ],
    tickers={
        "CORN": "옥수수ETF",
        "WEAT": "밀ETF",
        "SOYB": "대두ETF",
    },
    external_links=[
        ("🍚 식품안전나라", "https://www.foodsafetykorea.go.kr/"),
        ("📊 농산물유통정보", "https://www.kamis.or.kr/"),
        ("🛒 소비자물가 통계", "https://kostat.go.kr/"),
    ],
)
