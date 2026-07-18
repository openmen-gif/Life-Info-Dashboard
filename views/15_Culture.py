# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="문화/예술",
    icon="🎭",
    default_query="전시 공연 글로벌 K-문화 예술 동향",
    auto_news_query="공연 전시 K-POP 문화예술 영화",
    external_links=[
        ("🎭 인터파크 티켓", "https://tickets.interpark.com/"),
        ("🎬 CGV 영화", "https://www.cgv.co.kr/"),
        ("📊 문화체육관광부", "https://www.mcst.go.kr/"),
    ],
)
