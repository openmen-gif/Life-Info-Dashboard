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
    external_links=[
        ("🌷 화훼유통정보", "https://flower.at.or.kr/"),
        ("🌱 농촌진흥청", "https://www.rda.go.kr/"),
        ("🌿 국립수목원", "https://kna.forest.go.kr/"),
    ],
)
