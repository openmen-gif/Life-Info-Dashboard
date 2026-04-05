# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="교육",
    icon="📚",
    default_query="글로벌 에듀테크 국내 입시 교육 트렌드",
    youtube_sort="latest",
    auto_news_query="교육 입시 에듀테크 수능 대학",
    external_links=[
        ("📚 교육부", "https://www.moe.go.kr/"),
        ("🎓 대입정보포털", "https://www.adiga.kr/"),
        ("📊 한국교육과정평가원", "https://www.kice.re.kr/"),
    ],
)
