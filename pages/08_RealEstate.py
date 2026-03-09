# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="부동산",
    icon="🏠",
    default_query="국내 아파트 청약 전세 매매 부동산 동향",
    tickers={
        "VNQ": "미국REITs",
        "IYR": "부동산ETF",
        "XLRE": "부동산섹터",
    },
    auto_news_query="아파트 매매 전세 청약 부동산 시장",
    external_links=[
        ("🏠 국토부 실거래가", "https://rt.molit.go.kr/"),
        ("📊 한국부동산원", "https://www.reb.or.kr/"),
        ("🏢 네이버 부동산", "https://land.naver.com/"),
        ("📋 청약홈", "https://www.applyhome.co.kr/"),
    ],
)
