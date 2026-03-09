# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="운송/물류",
    icon="🚚",
    default_query="국내외 물류 해운 항공 운송 트렌드",
    tickers={
        "UPS": "UPS(물류)",
        "FDX": "페덱스",
        "BDRY": "해운지수ETF",
        "DAL": "델타항공",
    },
    auto_news_query="물류 해운 항공 운송 택배 트렌드",
    external_links=[
        ("🚚 물류신문", "https://www.klnews.co.kr/"),
        ("🚢 해양수산부", "https://www.mof.go.kr/"),
        ("✈️ 한국공항공사", "https://www.airport.co.kr/"),
    ],
)
