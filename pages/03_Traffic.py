# -*- coding: utf-8 -*-
"""교통 정보 — 실시간 교통 지도 + 교통 뉴스 + 관련 영상"""
import streamlit as st
import streamlit.components.v1 as components
from utils.css_loader import apply_custom_css
from utils.data_fetcher import fetch_news_search
from utils.report_downloader import render_download_buttons

apply_custom_css()

st.title("🚗 교통 정보")
st.markdown("---")

# ── 실시간 교통 지도 (메인) ────────────────────────────────────────────
st.markdown("### 🗺️ 실시간 교통 지도")
st.info("지도에서 실시간 도로 소통 상황을 직접 확인하세요. 초록=원활, 주황=서행, 빨강=정체")

tab_naver, tab_kakao, tab_its = st.tabs(["🗺️ 네이버 지도", "🗺️ 카카오맵", "🚗 ITS 국가교통정보"])

with tab_naver:
    components.html(
        '<iframe src="https://map.naver.com/p?c=15.00,0,0,0,dh&mapMode=0&trafficMode=1" '
        'width="100%" height="550" frameborder="0" style="border-radius:8px;"></iframe>',
        height=570,
    )

with tab_kakao:
    components.html(
        '<iframe src="https://map.kakao.com/?map_type=TYPE_MAP&map_attribute=ROADVIEW&urlLevel=10&urlX=497065&urlY=1105314" '
        'width="100%" height="550" frameborder="0" style="border-radius:8px;"></iframe>',
        height=570,
    )

with tab_its:
    components.html(
        '<iframe src="https://www.its.go.kr/" '
        'width="100%" height="550" frameborder="0" style="border-radius:8px;"></iframe>',
        height=570,
    )

# ── 바로가기 ───────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🔗 교통 정보 바로가기")
c1, c2, c3 = st.columns(3)
with c1:
    st.link_button("🛣️ 한국도로공사", "https://www.ex.co.kr/", use_container_width=True)
    st.link_button("🚌 서울TOPIS", "https://topis.seoul.go.kr/", use_container_width=True)
with c2:
    st.link_button("📊 고속도로 교통량", "https://data.ex.co.kr/", use_container_width=True)
    st.link_button("🗺️ 네이버 지도", "https://map.naver.com/", use_container_width=True)
with c3:
    st.link_button("🗺️ 카카오맵", "https://map.kakao.com/", use_container_width=True)
    st.link_button("🚇 서울교통공사", "https://www.seoulmetro.co.kr/", use_container_width=True)

# ── 교통 뉴스 ──────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📰 교통 관련 뉴스")
_traffic_news = fetch_news_search("교통 도로 고속도로 상황", limit=8)
if _traffic_news:
    for i, item in enumerate(_traffic_news):
        src = f" ({item['source']})" if item.get("source") else ""
        st.markdown(f"**{i+1}.** [{item['title']}]({item['link']}){src}")
        if item.get("snippet"):
            st.caption(item["snippet"])
else:
    st.info("교통 뉴스를 불러올 수 없습니다.")

# ── 관련 영상 ──────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🎬 교통 관련 최신 영상")
from utils.expert_template import render_youtube_section
_yt_traffic = render_youtube_section("교통 도로 고속도로", sort="latest")

# ── 보고서 다운로드 ────────────────────────────────────────────────────
st.markdown("---")
_context = {
    "query": "교통 정보",
    "news": _traffic_news,
    "web": [],
    "youtube": _yt_traffic,
    "df": [],
}
render_download_buttons(context=_context)
