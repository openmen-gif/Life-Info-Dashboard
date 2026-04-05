# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="취업/채용",
    icon="💼",
    default_query="채용 트렌드 취업 시장 자격증 직업 전망",
    youtube_sort="latest",
    sub_topics=[
        ("📋", "채용공고", "대기업 공채 채용공고 신입 경력 공개채용"),
        ("💡", "취업전략", "자기소개서 면접 취업 준비 합격 팁"),
        ("📜", "자격증", "자격증 시험 일정 국가자격 IT자격증 취득"),
        ("📊", "직업전망", "유망직업 직업전망 연봉 산업별 고용 동향"),
        ("🏢", "이직/커리어", "이직 경력개발 연봉협상 커리어 전환"),
    ],
    auto_news_query="채용 취업 고용 시장 구인 자격증",
    external_links=[
        ("💼 사람인", "https://www.saramin.co.kr/"),
        ("📋 잡코리아", "https://www.jobkorea.co.kr/"),
        ("🏛️ 워크넷", "https://www.work.go.kr/"),
        ("📊 고용노동부", "https://www.moel.go.kr/"),
    ],
)
