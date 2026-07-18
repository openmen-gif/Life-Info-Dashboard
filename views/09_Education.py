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
    # [주석] 글로벌 교육 산업 및 에듀테크 시장 동향을 모니터링하는 대표 시세 지표를 연동합니다.
    tickers={
        "EDU": "글로벌교육",  # New Oriental Education & Technology Group Inc. (EDU)
        "TAL": "에듀테크",    # TAL Education Group (TAL)
    },
    external_links=[
        ("📚 교육부", "https://www.moe.go.kr/"),
        ("🎓 대입정보포털", "https://www.adiga.kr/"),
        ("📊 한국교육과정평가원", "https://www.kice.re.kr/"),
    ],
)
