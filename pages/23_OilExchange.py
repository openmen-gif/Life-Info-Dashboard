# -*- coding: utf-8 -*-
"""
유가 & 환율 실시간 모니터링 페이지
- 환율: open.er-api.com (무료, API 키 불필요)
- 유가: yfinance 선물 시세 (CL=F, BZ=F 등)
"""
import streamlit as st
import datetime
import pandas as pd
from utils.css_loader import apply_custom_css
from utils.data_fetcher import fetch_exchange_rates, fetch_stock_data, fetch_news_search, fetch_youtube_search
from utils.report_downloader import render_download_buttons

apply_custom_css()

# ── 상수 ──────────────────────────────────────────────────────────────────
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
OIL_FUTURES = {
    "CL=F": ("WTI 원유", "🛢️"),
    "BZ=F": ("브렌트유", "🛢️"),
    "HO=F": ("난방유", "🔥"),
    "NG=F": ("천연가스", "💨"),
}

# ── 페이지 헤더 ───────────────────────────────────────────────────────────
st.title("⛽ 유가 & 환율 실시간 모니터링")
st.markdown("---")

if st.button("🔄 데이터 갱신", type="primary"):
    st.cache_data.clear()
    st.rerun()

st.caption(f"마지막 갱신: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (5분 자동 캐시)")

# ═════════════════════════════════════════════════════════
# 섹션 1: 실시간 환율
# ═════════════════════════════════════════════════════════
st.markdown("## 💱 실시간 환율 (USD 기준)")
with st.spinner("환율 데이터 로딩 중..."):
    fx = fetch_exchange_rates()

if fx["ok"] and fx["rates"]:
    rates = fx["rates"]
    st.success(f"✅ 환율 업데이트: {fx['updated']}")

    # KRW/USD 강조 메트릭
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🇺🇸 USD → 🇰🇷 KRW", f"₩ {rates.get('KRW', 0):,.2f}")
    col2.metric("🇪🇺 USD → EUR", f"€ {rates.get('EUR', 0):.4f}")
    col3.metric("🇯🇵 USD → JPY", f"¥ {rates.get('JPY', 0):,.2f}")
    col4.metric("🇨🇳 USD → CNY", f"¥ {rates.get('CNY', 0):.4f}")

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
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # KRW 환율 바 차트 시각화
    st.markdown("### 주요 통화 1단위당 원화 환산")
    chart_data = {}
    for code in ["EUR", "JPY", "CNY", "GBP", "SGD", "AUD"]:
        r_val = rates.get(code, None)
        krw_val = rates.get("KRW", 1)
        if r_val and krw_val:
            chart_data[code] = round(krw_val / r_val, 2)
    if chart_data:
        df_chart = pd.DataFrame({"통화": list(chart_data.keys()), "원화(KRW)": list(chart_data.values())})
        st.bar_chart(df_chart.set_index("통화"))
else:
    st.error("환율 데이터를 가져오지 못했습니다. 네트워크를 확인하세요.")

st.markdown("---")

# ═════════════════════════════════════════════════════════
# 섹션 2: 유가 실시간 시세
# ═════════════════════════════════════════════════════════
st.markdown("## 🛢️ 국제 유가·에너지 실시간 시세")

# 메트릭 카드 (현재가 + 등락)
oil_cols = st.columns(len(OIL_FUTURES))
for col, (symbol, (name, icon)) in zip(oil_cols, OIL_FUTURES.items()):
    with col:
        d = fetch_stock_data(symbol, period="5d")
        if d.get("ok"):
            delta_str = f"{d['change']:+.2f} ({d['change_pct']:+.2f}%)"
            col.metric(f"{icon} {name}", f"${d['price']:,.2f}", delta=delta_str)
        else:
            col.metric(f"{icon} {name}", "N/A", help="데이터 로딩 실패")

# WTI / 브렌트 상세 차트
oil_period = st.selectbox("차트 기간", ["5d", "1mo", "3mo", "6mo", "1y"], index=1, key="oil_period")

oil_tabs = st.tabs(["WTI 원유", "브렌트유", "난방유", "천연가스"])
for tab, (symbol, (name, icon)) in zip(oil_tabs, OIL_FUTURES.items()):
    with tab:
        d = fetch_stock_data(symbol, period=oil_period)
        if d.get("ok") and d.get("history"):
            st.markdown(f"#### {icon} {name} 추이")
            df = pd.DataFrame(d["history"])
            st.line_chart(df.set_index("Date")["Close"])

            # 통계
            prices = [r["Close"] for r in d["history"]]
            if prices:
                avg_p = sum(prices) / len(prices)
                total_chg = prices[-1] - prices[0]
                total_pct = (total_chg / prices[0] * 100) if prices[0] else 0
                sc1, sc2, sc3, sc4, sc5 = st.columns(5)
                sc1.metric("현재", f"${prices[-1]:,.2f}")
                sc2.metric("최고", f"${max(prices):,.2f}")
                sc3.metric("최저", f"${min(prices):,.2f}")
                sc4.metric("평균", f"${avg_p:,.2f}")
                sc5.metric("기간 등락", f"{total_chg:+,.2f} ({total_pct:+.1f}%)")
        else:
            st.warning(f"{name} 데이터를 가져오지 못했습니다.")

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
        with st.expander(f"📰 {title}", expanded=False):
            if snippet:
                st.write(snippet)
            meta = st.columns([2, 2, 1])
            meta[0].caption(f"📰 {source}")
            meta[1].caption(f"🕒 {published}")
            if link:
                meta[2].link_button("원문 보기", link)
else:
    st.info("현재 분석 뉴스를 가져오지 못했습니다.")

st.markdown("---")

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

# ── 관련 YouTube 영상 ─────────────────────────────────────────────────────
st.markdown("## 🎬 유가·환율 관련 YouTube 영상")
from utils.expert_template import render_youtube_section
_yt_oil = render_youtube_section("유가 환율 경제 분석", sort="latest")

# ── 보고서 다운로드 ────────────────────────────────────────────────────────
st.markdown("---")
oil_dl_data = []
for symbol, (name, icon) in OIL_FUTURES.items():
    d = fetch_stock_data(symbol, period="5d")
    if d.get("ok"):
        oil_dl_data.append({"항목": name, "현재가": d["price"], "전일비": d["change"], "등락률": f"{d['change_pct']}%"})

fx_dl = fetch_exchange_rates()
fx_rows = []
if fx_dl.get("ok") and fx_dl.get("rates"):
    for code, label in TARGET_CURRENCIES.items():
        r_val = fx_dl["rates"].get(code)
        if r_val:
            fx_rows.append({"통화": label, "코드": code, "환율(1USD)": r_val})

oil_exchange_context = {
    "query": "유가 환율 실시간 모니터링",
    "news": analysis_news if analysis_news else [],
    "web": [],
    "youtube": _yt_oil,
    "df": oil_dl_data + fx_rows,
}
render_download_buttons(context=oil_exchange_context)
