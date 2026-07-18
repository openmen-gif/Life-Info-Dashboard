# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="인구·결혼",
    icon="👰",
    default_query="결혼 저출산 인구 청년 신혼부부 정책",
    auto_news_query="결혼 저출산 인구 청년 신혼부부",
    sub_topics=[
        ("💍", "결혼/신혼", "결혼 신혼부부 결혼식 혼수 웨딩 트렌드"),
        ("👶", "저출산/출생", "저출산 출생률 출생아 인구 정책"),
        ("📊", "인구 통계/이동", "인구통계 인구이동 청년 수도권 집중"),
        ("🏠", "신혼/주거 지원", "신혼부부 주거 지원 청년주택 디딤돌"),
        ("👨‍👩‍👧", "가족/육아 정책", "가족정책 육아휴직 부모급여 양육수당"),
    ],
    external_links=[
        ("📊 통계청 인구통계", "https://kostat.go.kr/"),
        ("💍 결혼정보 통계", "https://kosis.kr/"),
        ("👶 저출산고령사회위원회", "https://www.betterfuture.go.kr/"),
    ],
)
