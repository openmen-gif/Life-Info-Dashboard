# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="건강",
    icon="🏥",
    default_query="최신 헬스케어 메디컬 건강관리 동향",
    tickers={
        "XLV": "헬스케어ETF",
        "PFE": "화이자",
        "JNJ": "존슨앤존슨",
    },
    auto_news_query="건강 의료 헬스케어 질병 예방",
    external_links=[
        ("🏥 질병관리청", "https://www.kdca.go.kr/"),
        ("💊 건강보험심사평가원", "https://www.hira.or.kr/"),
        ("📊 WHO 글로벌", "https://www.who.int/"),
    ],
)
