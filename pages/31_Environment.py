# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="환경/에너지",
    icon="🌱",
    default_query="미세먼지 탄소중립 신재생에너지 환경 동향",
    auto_news_query="미세먼지 대기질 기후변화 탄소중립 환경",
    sub_topics=[
        ("😷", "미세먼지/대기질", "미세먼지 초미세먼지 대기질 황사 예보"),
        ("🌡️", "기후변화/재해", "기후변화 폭염 폭우 가뭄 자연재해"),
        ("♻️", "재활용/폐기물", "재활용 분리수거 폐기물 플라스틱 감축"),
        ("⚡", "신재생에너지", "태양광 풍력 수소에너지 ESG 탄소중립"),
        ("🌊", "수질/생태계", "수질오염 해양오염 생태계 보존 멸종위기"),
    ],
    external_links=[
        ("😷 에어코리아", "https://www.airkorea.or.kr/"),
        ("🌡️ 기후정보포털", "https://www.climate.go.kr/"),
        ("🌱 환경부", "https://www.me.go.kr/"),
    ],
)
