# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="실버산업",
    icon="👴",
    default_query="고령화 노인 실버산업 시니어 케어 정책",
    auto_news_query="고령화 노인 실버산업 시니어 요양",
    sub_topics=[
        ("👴", "노인 복지/연금", "노인 복지 기초연금 노령연금 어르신"),
        ("🏥", "요양/돌봄", "요양원 요양병원 노인장기요양 돌봄 서비스"),
        ("💼", "시니어 일자리", "노인 일자리 시니어 채용 정년 연장"),
        ("🏠", "고령자 주거", "실버타운 고령자 주거 노인주택 시니어하우징"),
        ("🩺", "건강관리/치매", "치매 건강관리 노인건강 인지건강 예방"),
    ],
    external_links=[
        ("👴 보건복지부", "https://www.mohw.go.kr/"),
        ("🏥 국민건강보험 장기요양", "https://www.longtermcare.or.kr/"),
        ("📊 노인복지 통계", "https://kosis.kr/"),
    ],
)
