# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="공공요금",
    icon="💡",
    default_query="전기료 가스비 수도 공공요금 한전 도시가스 인상",
    auto_news_query="전기료 가스비 공공요금 한전 도시가스 인상",
    sub_topics=[
        ("⚡", "전기료/한전", "전기요금 한전 누진제 전력 인상"),
        ("🔥", "도시가스/난방", "도시가스 LNG 난방비 가스요금 인상"),
        ("💧", "수도/상하수도", "수도요금 상수도 하수도 공공요금"),
        ("📡", "통신/요금제", "통신요금 5G LTE 알뜰폰 통신비"),
        ("🏠", "관리비/공동주택", "아파트 관리비 공동주택 관리 동향"),
    ],
    external_links=[
        ("⚡ 한국전력", "https://home.kepco.co.kr/"),
        ("🔥 한국가스공사", "https://www.kogas.or.kr/"),
        ("💧 K-water", "https://www.kwater.or.kr/"),
        ("📡 통신요금 비교", "https://www.smartchoice.or.kr/"),
    ],
)
