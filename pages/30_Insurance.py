# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="보험/연금",
    icon="🛡️",
    default_query="보험 연금 국민연금 건강보험 실손보험 동향",
    auto_news_query="국민연금 건강보험 실손보험 보험료 연금",
    sub_topics=[
        ("🏥", "건강/실손보험", "실손보험 건강보험 의료보험 보험료"),
        ("👴", "국민연금/퇴직연금", "국민연금 퇴직연금 개인연금 수령액"),
        ("🚗", "자동차/화재보험", "자동차보험 화재보험 보험료 비교"),
        ("💰", "저축/투자보험", "저축보험 변액보험 연금저축 절세"),
        ("📋", "보험 정책/제도", "보험 제도 변경 금융감독원 소비자 보호"),
    ],
    external_links=[
        ("🛡️ 보험다모아", "https://www.e-insmarket.or.kr/"),
        ("📊 국민연금공단", "https://www.nps.or.kr/"),
        ("🏥 건강보험공단", "https://www.nhis.or.kr/"),
    ],
)
