# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

# ── 공공요금 빠른 조회 그리드 ─────────────────────────────────────────────
st.markdown("## 💡 공공요금 빠른 조회")
st.caption("각 기관 사이트에서 요금 조회·납부·인상 발표를 직접 확인하세요.")

_pc1, _pc2, _pc3, _pc4 = st.columns(4)
with _pc1:
    st.link_button("⚡ 한국전력 (요금조회)", "https://cyber.kepco.co.kr/ckepco/front/jsp/CY/E/E/CYEEHP000.jsp", use_container_width=True)
with _pc2:
    st.link_button("🔥 도시가스코리아", "https://www.citygas.or.kr/", use_container_width=True)
with _pc3:
    st.link_button("💧 K-water (수도)", "https://www.kwater.or.kr/", use_container_width=True)
with _pc4:
    st.link_button("📡 스마트초이스 (통신)", "https://www.smartchoice.or.kr/", use_container_width=True)

_pc5, _pc6, _pc7, _pc8 = st.columns(4)
with _pc5:
    st.link_button("🏠 K-apt 관리비", "https://www.k-apt.go.kr/", use_container_width=True)
with _pc6:
    st.link_button("🚇 교통카드/대중교통", "https://www.tmoney.co.kr/", use_container_width=True)
with _pc7:
    st.link_button("📊 공공데이터포털 (요금)", "https://www.data.go.kr/", use_container_width=True)
with _pc8:
    st.link_button("🏛️ 산업통상자원부", "https://www.motie.go.kr/", use_container_width=True)

st.info("💡 **요금 절감 팁**: 한전 에너지캐시백 · 가스공사 절약요금제 · 알뜰폰 요금제 · 아파트 관리비 비교는 위 링크에서 확인하세요.")

st.markdown("---")

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
