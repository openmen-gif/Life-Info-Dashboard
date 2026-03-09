# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="반려동물",
    icon="🐾",
    default_query="반려동물 사료 펫 헬스케어 트렌드",
    tickers={
        "WOOF": "펫케어ETF",
        "IDXX": "아이덱스(동물진단)",
        "CHWY": "츄이(펫쇼핑)",
    },
    auto_news_query="반려동물 펫 산업 동물병원 사료",
    external_links=[
        ("🐾 동물보호관리시스템", "https://www.animal.go.kr/"),
        ("🏥 대한수의사회", "https://www.kvma.or.kr/"),
    ],
)
