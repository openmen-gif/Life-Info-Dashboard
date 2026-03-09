# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="건강",
    icon="🏥",
    default_query="최신 헬스케어 메디컬 건강관리 동향",
    sub_topics=[
        ("🦠", "감염병/예방", "감염병 코로나 독감 예방접종 방역"),
        ("💪", "운동/다이어트", "운동 다이어트 헬스 피트니스 체중관리"),
        ("🧠", "정신건강", "정신건강 우울증 스트레스 수면 심리상담"),
        ("💊", "의약품/영양제", "의약품 영양제 비타민 건강기능식품"),
        ("👴", "노인/만성질환", "노인 건강 만성질환 당뇨 고혈압 치매"),
    ],
    tickers={
        "XLV": "헬스케어ETF",
        "PFE": "화이자",
        "JNJ": "존슨앤존슨",
    },
    external_links=[
        ("🏥 질병관리청", "https://www.kdca.go.kr/"),
        ("💊 건강보험심사평가원", "https://www.hira.or.kr/"),
        ("📊 WHO 글로벌", "https://www.who.int/"),
    ],
)
