# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="연예/엔터",
    icon="🎬",
    default_query="K-POP 드라마 영화 연예 엔터테인먼트 동향",
    auto_news_query="K-POP 아이돌 드라마 영화 예능 연예",
    sub_topics=[
        ("🎤", "K-POP/음악", "K-POP 아이돌 음원 차트 컴백"),
        ("📺", "드라마/예능", "드라마 예능 방송 시청률 화제"),
        ("🎬", "영화", "영화 박스오피스 개봉 리뷰"),
        ("🌟", "연예인/이슈", "연예인 스타 이슈 화제"),
        ("🎮", "게임/웹툰", "게임 웹툰 웹소설 콘텐츠 트렌드"),
    ],
    external_links=[
        ("🎵 멜론 차트", "https://www.melon.com/chart/"),
        ("🎬 네이버 영화", "https://movie.naver.com/"),
        ("📺 TV 편성표", "https://search.naver.com/search.naver?query=TV+편성표"),
    ],
)
