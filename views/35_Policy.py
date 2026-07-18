# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="정부정책",
    icon="🏛️",
    default_query="정부 지원금 복지 청년 정책 세금 연말정산",
    auto_news_query="정부 지원금 복지 청년 정책 세금",
    sub_topics=[
        ("💰", "복지/지원금", "복지 지원금 기초생활 차상위 저소득 정책"),
        ("👶", "청년/주거 정책", "청년 지원 청년주택 청년도약계좌 청년정책"),
        ("👵", "노인/장애인 복지", "노인 복지 기초연금 장애인 지원 정책"),
        ("📋", "세금/연말정산", "세금 연말정산 종합소득세 절세 부가세"),
        ("🏛️", "국정/입법 동향", "국회 법안 입법 정부 정책 발표"),
    ],
    external_links=[
        ("💰 정부24", "https://www.gov.kr/"),
        ("📋 복지로", "https://www.bokjiro.go.kr/"),
        ("📊 국세청", "https://www.nts.go.kr/"),
        ("🏛️ 국회 의안정보", "https://likms.assembly.go.kr/bill/main.do"),
    ],
)
