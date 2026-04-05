# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page
import streamlit.components.v1 as components

apply_custom_css()

render_expert_page(title="해외 분쟁/전쟁", icon="🌍", default_query="우크라이나 중동 글로벌 분쟁 전쟁 동향", youtube_sort="latest")

st.markdown("---")
st.markdown("### 🗺️ 글로벌 분쟁 실시간 모니터링 맵 (ArcGIS)")
st.info(
    "전 세계 분쟁·갈등 지역을 ArcGIS 대시보드로 실시간 시각화합니다. "
    "지도를 마우스로 확대·이동하여 특정 지역의 분쟁 현황을 상세히 확인하세요."
)

components.html(
    """
    <iframe
        src="https://experience.arcgis.com/experience/ebe374c40c1a4231a06075155b0e8cb9"
        width="100%"
        height="780"
        frameborder="0"
        allowfullscreen
        style="border-radius:8px;">
    </iframe>
    """,
    height=800,
)
