# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="자동차",
    icon="🚗",
    default_query="신차 출시 중고차 시세 자동차 보험 동향",
    auto_news_query="자동차 신차 전기차 중고차 시세",
    # [주석] 글로벌 자동차 시장을 모니터링하는 대표 ETF 및 개별 제조사 시세를 연동합니다.
    tickers={
        "CARZ": "글로벌자동차",  # First Trust NASDAQ Global Auto Index Fund
        "TSLA": "테슬라",
        "7203.T": "토요타",
    },
    sub_topics=[
        ("🚙", "신차/출시", "신차 출시 자동차 리뷰 시승"),
        ("🔋", "전기차/수소차", "전기차 수소차 충전 보조금 테슬라"),
        ("💰", "중고차/시세", "중고차 시세 매매 감가 시장"),
        ("🔧", "정비/보험", "자동차 정비 보험료 사고 수리"),
        ("🛣️", "교통정책", "자동차세 통행료 주차 교통 정책"),
    ],
    external_links=[
        ("🚗 엔카", "https://www.encar.com/"),
        ("🚙 KB차차차", "https://www.kbchachacha.com/"),
        ("📊 자동차등록현황", "https://stat.molit.go.kr/"),
    ],
)
