# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="생활법률",
    icon="⚖️",
    default_query="최신 생활 법률 대법원 판례 동향",
    youtube_sort="latest",
    auto_news_query="법률 판례 대법원 생활법률 개정",
    external_links=[
        ("⚖️ 대한법률구조공단", "https://www.klac.or.kr/"),
        ("📜 국가법령정보센터", "https://www.law.go.kr/"),
        ("🏛️ 대법원 판례검색", "https://glaw.scourt.go.kr/"),
    ],
)
