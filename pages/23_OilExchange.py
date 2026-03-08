# -*- coding: utf-8 -*-
"""
유가 & 환율 실시간 모니터링 페이지
- 환율: open.er-api.com (무료, API 키 불필요)
- 유가: EIA / DuckDuckGo 뉴스 기반 컨텍스트
"""
import streamlit as st
import requests
import datetime
import pandas as pd
from utils.css_loader import apply_custom_css
from utils.data_fetcher import fetch_news_search

apply_custom_css()

# ── 상수 ──────────────────────────────────────────────────────────────────
FOREX_API = "https://open.er-api.com/v6/latest/USD"
TARGET_CURRENCIES = {
    "KRW": "한국 원 (KRW)",
    "EUR": "유럽 유로 (EUR)",
    "JPY": "일본 엔 (JPY)",
    "CNY": "중국 위안 (CNY)",
    "GBP": "영국 파운드 (GBP)",
    "SGD": "싱가포르 달러 (SGD)",
    "HKD": "홍콩 달러 (HKD)",
    "AUD": "호주 달러 (AUD)",
}
OIL_TICKERS = {
    "WTI (서부텍사스원유)": "WTI crude oil",
    "Brent (브렌트유)": "Brent crude oil price",
    "두바이유 (Dubai)": "Dubai crude oil price",
}

# ── 캐시 함수 ────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)  # 5분 캐시
def _fetch_forex():
    """USD 기준 환율 데이터 조회 (open.er-api.com – 무료, 키 없음)."""
    try:
        r = requests.get(FOREX_API, timeout=8)
        r.raise_for_status()
        data = r.json()
        return data.get("rates", {}), data.get("time_last_update_utc", "")
    except Exception as e:
        return {}, str(e)


@st.cache_data(ttl=600, show_spinner=False)
def _fetch_oil_news(query: str):
    return fetch_news_search(query, limit=4)


# ── 페이지 헤더 ───────────────────────────────────────────────────────────
st.title("⛽ 유가 & 환율 실시간 모니터링")
st.markdown("---")

if st.button("🔄 데이터 갱신", type="primary"):
    st.cache_data.clear()
    st.rerun()

st.caption(f"마지막 갱신: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (5분 자동 갱신)")

# ═════════════════════════════════════════════════════════
# 섹션 1: 실시간 환율
# ═════════════════════════════════════════════════════════
st.markdown("## 💱 실시간 환율 (USD 기준)")
with st.spinner("환율 데이터 로딩 중..."):
    rates, updated_at = _fetch_forex()

if rates:
    st.success(f"✅ 환율 업데이트: {updated_at}")

    # KRW/USD 강조 메트릭
    krw = rates.get("KRW", 0)
    eur = rates.get("EUR", 0)
    jpy = rates.get("JPY", 0)
    cny = rates.get("CNY", 0)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🇺🇸 USD → 🇰🇷 KRW", f"₩ {krw:,.2f}")
    col2.metric("🇪🇺 USD → EUR", f"€ {eur:.4f}")
    col3.metric("🇯🇵 USD → JPY", f"¥ {jpy:,.2f}")
    col4.metric("🇨🇳 USD → CNY", f"¥ {cny:.4f}")

    st.markdown("### 주요 통화 대 USD 환율 테이블")
    rows = []
    for code, label in TARGET_CURRENCIES.items():
        rate_val = rates.get(code, None)
        if rate_val:
            usd_per_unit = 1 / rate_val if rate_val != 0 else 0
            rows.append({
                "통화": label,
                "코드": code,
                "1 USD 기준": f"{rate_val:,.4f}",
                "1 단위 → USD": f"${usd_per_unit:.6f}",
            })
    df_rates = pd.DataFrame(rows)
    st.dataframe(df_rates, use_container_width=True, hide_index=True)

    # KRW 환율 바 차트 시각화
    st.markdown("### 주요 통화 1단위당 원화 환산")
    chart_data = {}
    for code in ["EUR", "JPY", "CNY", "GBP", "SGD", "AUD"]:
        r_val = rates.get(code, None)
        krw_val = rates.get("KRW", 1)
        if r_val and krw_val:
            chart_data[code] = krw_val / r_val
    if chart_data:
        df_chart = pd.DataFrame.from_dict({"통화": list(chart_data.keys()), "원화(KRW)": list(chart_data.values())})
        st.bar_chart(df_chart.set_index("통화"))
else:
    st.error("환율 데이터를 가져오지 못했습니다. 네트워크를 확인하세요.")

st.markdown("---")

# ═════════════════════════════════════════════════════════
# 섹션 2: 유가 모니터링
# ═════════════════════════════════════════════════════════
st.markdown("## 🛢️ 국제 유가 동향 (WTI · 브렌트 · 두바이)")
st.info(
    "국제 유가는 실시간 API 없이는 상업 금융 데이터를 직접 수신하기 어렵습니다. "
    "대신, 최신 유가 뉴스를 수집하여 현황을 분석합니다. "
    "정확한 호가가 필요하시면 [인베스팅닷컴](https://kr.investing.com/commodities/crude-oil)을 참고하세요."
)

oil_tabs = st.tabs(list(OIL_TICKERS.keys()))
for tab, (oil_name, oil_query) in zip(oil_tabs, OIL_TICKERS.items()):
    with tab:
        st.markdown(f"#### 📰 {oil_name} 최신 뉴스")
        with st.spinner(f"{oil_name} 뉴스 로딩 중..."):
            oil_news = _fetch_oil_news(oil_query)
        if oil_news:
            for n in oil_news:
                title = n.get("title", "")
                link = n.get("link", "")
                source = n.get("source", "")
                published = n.get("published", "")
                snippet = n.get("snippet", "")
                with st.expander(f"📰 {title}", expanded=False):
                    if snippet:
                        st.write(snippet)
                    meta_cols = st.columns([2, 2, 1])
                    meta_cols[0].caption(f"📰 {source}")
                    meta_cols[1].caption(f"🕒 {published}")
                    if link:
                        meta_cols[2].link_button("원문 보기", link)
        else:
            st.warning("현재 뉴스를 가져오지 못했습니다.")

st.markdown("---")

# ═════════════════════════════════════════════════════════
# 섹션 3: 유가 & 환율 영향 분석 뉴스
# ═════════════════════════════════════════════════════════
st.markdown("## 📊 유가·환율 연동 경제 분석")
st.markdown("유가 변동과 환율 변화가 한국 경제에 미치는 영향 관련 뉴스입니다.")

with st.spinner("분석 뉴스 로딩 중..."):
    analysis_news = fetch_news_search("유가 환율 한국 경제 영향 분석", limit=5)

if analysis_news:
    for n in analysis_news:
        title = n.get("title", "")
        link = n.get("link", "")
        source = n.get("source", "")
        published = n.get("published", "")
        snippet = n.get("snippet", "")
        st.markdown(f"**[{title}]({link})**")
        if snippet:
            st.caption(snippet[:160] + "..." if len(snippet) > 160 else snippet)
        st.caption(f"📰 {source}  |  🕒 {published}")
        st.markdown("---")
else:
    st.info("현재 분석 뉴스를 가져오지 못했습니다.")

# ═════════════════════════════════════════════════════════
# 섹션 4: 빠른 링크 모니터링
# ═════════════════════════════════════════════════════════
st.markdown("## 🔗 실시간 유가/환율 외부 모니터링")
link_cols = st.columns(3)
with link_cols[0]:
    st.link_button("🛢️ 인베스팅 - 원유 차트", "https://kr.investing.com/commodities/crude-oil", use_container_width=True)
    st.link_button("🛢️ WTI 실시간 호가", "https://kr.investing.com/commodities/crude-oil-streaming-chart", use_container_width=True)
with link_cols[1]:
    st.link_button("💱 네이버 환율", "https://search.naver.com/search.naver?query=환율", use_container_width=True)
    st.link_button("💱 하나은행 환율", "https://www.hanabank.com/cms/ib20/ib20_HBBMAIN0001.do", use_container_width=True)
with link_cols[2]:
    st.link_button("📊 한국은행 환율 통계", "https://www.bok.or.kr/portal/singl/baseRate/selBasicRate.do?menuNo=200643", use_container_width=True)
    st.link_button("📊 EIA 유가 통계", "https://www.eia.gov/petroleum/", use_container_width=True)
