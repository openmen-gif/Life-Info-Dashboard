# -*- coding: utf-8 -*-
"""교통 정보 — 실시간 교통 뉴스 + 외부 모니터링 링크"""
import streamlit as st
import plotly.graph_objects as go
from utils.css_loader import apply_custom_css
from utils.data_fetcher import fetch_traffic_status, fetch_news_search

apply_custom_css()

st.title("🚗 교통 정보")
st.markdown("---")

# ── 실시간 교통 뉴스 ─────────────────────────────────────────────────────
st.markdown("### 📰 실시간 교통 뉴스")
traffic_news = fetch_news_search("고속도로 교통 정체 도로 상황", limit=5)
if traffic_news:
    for n in traffic_news[:5]:
        st.markdown(
            f"- **[{n['title']}]({n['link']})**  \n"
            f"  <small>{n.get('source', '')} | {n.get('published', '')}</small>",
            unsafe_allow_html=True,
        )
else:
    st.info("교통 관련 뉴스를 가져오지 못했습니다.")

st.markdown("---")

# ── 주요 고속도로 현황 (기본 데이터) ──────────────────────────────────────
traffic = fetch_traffic_status()

st.markdown("### 주요 고속도로 현황")
st.caption("※ 실시간 데이터는 ITS(its.go.kr) 또는 한국도로공사(data.ex.co.kr) API 키 등록 후 연동 가능합니다.")

color_map = {"green": "#4CAF50", "orange": "#FF9800", "red": "#F44336"}
status_emoji = {"green": "🟢 원활", "orange": "🟡 서행", "red": "🔴 정체"}

for t in traffic:
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(f"**{t['route']}**")
    with col2:
        st.markdown(status_emoji.get(t["color"], "⚪"))
    with col3:
        st.metric("속도", f"{t['speed_kmh']} km/h")

st.markdown("---")

# ── Speed chart ──────────────────────────────────────────────────────────
st.markdown("### 구간별 평균 속도")
route_names = [t["route"].split("(")[0].strip() for t in traffic]
speeds = [t["speed_kmh"] for t in traffic]
colors = [color_map.get(t["color"], "#888") for t in traffic]

fig = go.Figure(go.Bar(
    x=speeds,
    y=route_names,
    orientation='h',
    marker_color=colors,
    text=[f"{s} km/h" for s in speeds],
    textposition='auto',
))
fig.update_layout(
    xaxis_title="평균 속도 (km/h)",
    yaxis=dict(autorange="reversed"),
    height=350,
    margin=dict(l=10, r=10, t=10, b=10),
    template="plotly_dark",
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ── 실시간 교통 외부 모니터링 ─────────────────────────────────────────────
st.markdown("### 🔗 실시간 교통 외부 모니터링")
lk1, lk2, lk3 = st.columns(3)
with lk1:
    st.link_button("🚗 ITS 교통정보", "https://www.its.go.kr/", use_container_width=True)
    st.link_button("🛣️ 한국도로공사", "https://www.ex.co.kr/", use_container_width=True)
with lk2:
    st.link_button("🗺️ 네이버 지도", "https://map.naver.com/", use_container_width=True)
    st.link_button("🗺️ 카카오맵", "https://map.kakao.com/", use_container_width=True)
with lk3:
    st.link_button("🚌 서울TOPIS", "https://topis.seoul.go.kr/", use_container_width=True)
    st.link_button("📊 고속도로 교통량", "https://data.ex.co.kr/", use_container_width=True)
