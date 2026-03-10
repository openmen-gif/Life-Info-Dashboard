# -*- coding: utf-8 -*-
"""교통 정보 — 실시간 교통 바로가기 + 교통 뉴스 + 관련 영상"""
import streamlit as st
import streamlit.components.v1 as components
from utils.css_loader import apply_custom_css
from utils.data_fetcher import fetch_news_search
from utils.report_downloader import render_download_buttons

apply_custom_css()

st.title("🚗 교통 정보")
st.markdown("---")

# ── 실시간 교통 지도 바로가기 (메인) ──────────────────────────────────
st.markdown("### 🗺️ 실시간 교통 지도")
st.info("아래 버튼을 눌러 실시간 교통 상황을 확인하세요. 새 탭에서 열립니다.")

c1, c2 = st.columns(2)
with c1:
    st.link_button("🗺️ 네이버 지도 (실시간 교통)", "https://map.naver.com/p?c=15.00,0,0,0,dh&mapMode=0&trafficMode=1", use_container_width=True)
    st.link_button("🗺️ 카카오맵", "https://map.kakao.com/", use_container_width=True)
    st.link_button("🚗 ITS 실시간 교통정보", "https://www.its.go.kr/", use_container_width=True)
with c2:
    st.link_button("🛣️ 한국도로공사 실시간", "https://www.ex.co.kr/", use_container_width=True)
    st.link_button("🚌 서울TOPIS", "https://topis.seoul.go.kr/", use_container_width=True)
    st.link_button("📊 고속도로 교통량", "https://data.ex.co.kr/", use_container_width=True)

# ── 전국 도로 지도 (임베딩 가능) ──────────────────────────────────────
st.markdown("---")
st.markdown("### 🌐 전국 도로 지도")
tab_osm, tab_google = st.tabs(["OpenStreetMap", "Google Maps"])
with tab_osm:
    components.html(
        '<iframe src="https://www.openstreetmap.org/export/embed.html?bbox=124.5%2C33.0%2C131.0%2C38.8&layer=transportmap" '
        'width="100%" height="500" frameborder="0" style="border-radius:8px;"></iframe>',
        height=520,
    )
with tab_google:
    components.html(
        '<iframe src="https://www.google.com/maps/embed?pb=!1m14!1m12!1m3!1d3000000!2d127.5!3d36.5!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!5e0!3m2!1sko!2skr!4v1" '
        'width="100%" height="500" frameborder="0" style="border-radius:8px;" allowfullscreen loading="lazy"></iframe>',
        height=520,
    )

# ── 추가 바로가기 ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🔗 추가 교통 정보")
c1, c2, c3 = st.columns(3)
with c1:
    st.link_button("🚇 서울교통공사", "https://www.seoulmetro.co.kr/", use_container_width=True)
with c2:
    st.link_button("✈️ 인천공항", "https://www.airport.kr/", use_container_width=True)
with c3:
    st.link_button("🚄 코레일(KTX)", "https://www.letskorail.com/", use_container_width=True)

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
