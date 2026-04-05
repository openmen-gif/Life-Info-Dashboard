# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="IT/테크",
    icon="💻",
    default_query="AI 반도체 스마트폰 IT 기술 트렌드",
    youtube_sort="latest",
    tickers={
        "SOXX": "반도체ETF",
        "QQQ": "나스닥100ETF",
        "ARKK": "혁신기술ETF",
    },
    sub_topics=[
        ("🤖", "AI/인공지능", "AI 인공지능 ChatGPT 생성형AI LLM 트렌드"),
        ("🔬", "반도체", "반도체 삼성전자 SK하이닉스 TSMC 엔비디아 파운드리"),
        ("📱", "스마트폰/가전", "스마트폰 갤럭시 아이폰 출시 가전 CES"),
        ("☁️", "클라우드/SaaS", "클라우드 AWS Azure 구글클라우드 SaaS"),
        ("🔒", "사이버보안", "사이버보안 해킹 랜섬웨어 개인정보 보호"),
    ],
    auto_news_query="AI 반도체 IT 기술 스마트폰 소프트웨어",
    external_links=[
        ("💻 ZDNet Korea", "https://zdnet.co.kr/"),
        ("📱 더버지(The Verge)", "https://www.theverge.com/"),
        ("🔬 전자신문", "https://www.etnews.com/"),
    ],
)
