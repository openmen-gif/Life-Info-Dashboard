# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="스포츠",
    icon="⚽",
    default_query="KBO MLB EPL NBA 스포츠 경기 결과 분석",
    auto_news_query="프로야구 축구 농구 스포츠 경기 결과",
    sub_topics=[
        ("⚾", "야구", "KBO MLB 프로야구 경기 결과 순위"),
        ("⚽", "축구", "K리그 EPL 해외축구 경기 결과"),
        ("🏀", "농구/배구", "KBL NBA 프로농구 배구 경기"),
        ("🏌️", "골프/테니스", "PGA LPGA 골프 테니스 대회"),
        ("🏋️", "격투기/기타", "UFC 격투기 e스포츠 올림픽"),
    ],
    external_links=[
        ("⚾ KBO 공식", "https://www.koreabaseball.com/"),
        ("⚽ K리그", "https://www.kleague.com/"),
        ("📊 ESPN", "https://www.espn.com/"),
    ],
)
