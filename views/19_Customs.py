# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="관세/무역",
    icon="🚢",
    default_query="한국 수출입 무역 글로벌 관세 동향",
    youtube_sort="latest",
    tickers={
        "BDRY": "해운지수ETF(BDI)",
        "ZIM": "짐(해운)",
        "FDX": "페덱스(물류)",
    },
    auto_news_query="수출입 무역 관세 FTA 통관",
    external_links=[
        ("🚢 관세청", "https://www.customs.go.kr/"),
        ("📊 무역통계", "https://tradestat.customs.go.kr/"),
        ("📋 KITA 무역협회", "https://www.kita.net/"),
    ],
)
