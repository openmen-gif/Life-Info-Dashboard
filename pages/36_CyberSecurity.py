# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="사이버보안",
    icon="🛡️",
    default_query="보이스피싱 스미싱 신종 사기 개인정보 유출 해킹",
    auto_news_query="보이스피싱 스미싱 사기 개인정보 유출 해킹",
    sub_topics=[
        ("📞", "보이스피싱/스미싱", "보이스피싱 스미싱 메신저피싱 신종수법"),
        ("🔐", "개인정보 유출", "개인정보 유출 해킹 데이터 유출 사고"),
        ("💻", "랜섬웨어/해킹", "랜섬웨어 해킹 사이버 공격 침해 사고"),
        ("📲", "스마트폰/앱 보안", "스마트폰 앱 보안 악성앱 모바일 보안"),
        ("🏦", "금융사기/계좌탈취", "금융사기 계좌탈취 카드 부정사용 피싱"),
    ],
    external_links=[
        ("🛡️ KISA 인터넷진흥원", "https://www.kisa.or.kr/"),
        ("📞 보이스피싱 신고 (112)", "https://www.police.go.kr/"),
        ("🔐 개인정보 침해신고", "https://privacy.kisa.or.kr/"),
        ("💻 보호나라", "https://www.boho.or.kr/"),
    ],
)
