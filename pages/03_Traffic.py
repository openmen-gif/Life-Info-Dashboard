# -*- coding: utf-8 -*-
import streamlit as st
import plotly.graph_objects as go
from utils.css_loader import apply_custom_css
from utils.data_fetcher import fetch_traffic_status

apply_custom_css()

st.title("🚗 교통 정보")
st.markdown("---")

traffic = fetch_traffic_status()

# ── Status overview ──────────────────────────────────────────────────────
st.markdown("### 주요 고속도로 현황")

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

st.info("💡 실시간 교통 데이터 연동은 TOPIS API 또는 국토교통부 API 키 설정 후 사용 가능합니다.")
