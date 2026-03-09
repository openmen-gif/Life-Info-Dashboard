# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="사업/창업",
    icon="🏢",
    default_query="스타트업 창업 지원 비즈니스 매크로 동향",
    tickers={
        "IPO": "IPO ETF",
        "ARKK": "ARK혁신ETF",
        "XLK": "기술섹터ETF",
    },
    auto_news_query="스타트업 창업 지원 벤처 투자",
    external_links=[
        ("🏢 중소벤처기업부", "https://www.mss.go.kr/"),
        ("📋 K-스타트업", "https://www.k-startup.go.kr/"),
        ("💰 중소기업진흥공단", "https://www.kosmes.or.kr/"),
    ],
)
