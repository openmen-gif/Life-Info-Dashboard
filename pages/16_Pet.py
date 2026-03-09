# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="반려동물",
    icon="🐾",
    default_query="반려동물 사료 펫 헬스케어 트렌드",
    sub_topics=[
        ("🐕", "강아지", "강아지 품종 훈련 산책 사료 추천"),
        ("🐈", "고양이", "고양이 품종 성격 사료 건강 캣타워"),
        ("🏥", "동물병원/건강", "반려동물 건강 예방접종 동물병원 비용"),
        ("🛒", "펫 용품/사료", "반려동물 사료 간식 용품 펫푸드 추천"),
        ("📋", "입양/보호", "유기동물 입양 반려동물 등록 동물보호"),
    ],
    tickers={
        "WOOF": "펫케어ETF",
        "IDXX": "아이덱스(동물진단)",
        "CHWY": "츄이(펫쇼핑)",
    },
    external_links=[
        ("🐾 동물보호관리시스템", "https://www.animal.go.kr/"),
        ("🏥 대한수의사회", "https://www.kvma.or.kr/"),
        ("📋 반려동물등록", "https://www.animal.go.kr/front/awtis/record/recordList.do"),
    ],
)
