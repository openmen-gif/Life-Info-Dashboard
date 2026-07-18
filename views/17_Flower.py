# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="화훼/식물",
    icon="🌷",
    default_query="플랜테리어 다육식물 화훼 트렌드",
    auto_news_query="화훼 식물 플랜테리어 꽃 화분",
    # [주석] 화훼/식물의 원예 및 임업 분야를 대표하는 글로벌 지표(ETF)들을 tickers로 연동시킵니다.
    tickers={
        "WOOD": "글로벌식물/임업",
        "DBA": "농산물원자재",
        "MOO": "글로벌농업",
    },
    external_links=[
        ("🌷 화훼유통정보", "https://flower.at.or.kr/"),
        ("🌱 농촌진흥청", "https://www.rda.go.kr/"),
        ("🌿 국립수목원", "https://kna.forest.go.kr/"),
    ],
)
