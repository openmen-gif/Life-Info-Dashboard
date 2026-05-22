# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="재난·안전",
    icon="🚨",
    default_query="한국 기상특보 태풍 호우 산불 지진 재난 안전",
    auto_news_query="기상특보 태풍 호우 산불 지진 재난 안전",
    sub_topics=[
        ("🌀", "기상특보/태풍", "태풍 호우 폭우 폭설 한파 폭염 기상특보"),
        ("🔥", "산불/화재", "산불 산림 화재 대형화재 안전 대응"),
        ("🌋", "지진/지질", "지진 지질재해 화산 진도 한반도"),
        ("🚨", "사회 안전사고", "교통사고 산업재해 안전사고 인명피해"),
        ("📢", "재난 대비/대피", "재난 대피요령 안전 매뉴얼 행동지침"),
    ],
    external_links=[
        ("🚨 국민재난안전포털", "https://www.safekorea.go.kr/"),
        ("🌀 기상청 특보", "https://www.weather.go.kr/w/weather/warning/now-warning.do"),
        ("🔥 산림청 산불정보", "https://fd.forest.go.kr/ffas/"),
        ("🌋 지진정보 KMA", "https://www.weather.go.kr/w/eqk-vol/recent-eqk/kor.do"),
    ],
)
