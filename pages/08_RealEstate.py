# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="부동산",
    icon="🏠",
    default_query="국내 아파트 청약 전세 매매 부동산 동향",
    youtube_sort="latest",
    tickers={
        "VNQ": "미국REITs",
        "IYR": "부동산ETF",
        "XLRE": "부동산섹터",
    },
    sub_topics=[
        ("🏢", "아파트/매매", "아파트 매매 시세 실거래가 분양"),
        ("🏠", "전세/월세", "전세 월세 보증금 역전세 임대차"),
        ("📋", "청약/분양", "아파트 청약 분양 당첨 조건 일정"),
        ("📊", "시장전망", "부동산 시장 전망 가격 하락 상승 예측"),
        ("🏗️", "재건축/재개발", "재건축 재개발 정비사업 규제 투자"),
    ],
    auto_news_query="아파트 매매 전세 청약 부동산 시장",
    external_links=[
        ("🏠 국토부 실거래가", "https://rt.molit.go.kr/"),
        ("📊 한국부동산원", "https://www.reb.or.kr/"),
        ("🏢 네이버 부동산", "https://land.naver.com/"),
        ("📋 청약홈", "https://www.applyhome.co.kr/"),
    ],
)
