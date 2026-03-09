# -*- coding: utf-8 -*-
"""
주식 실시간 모니터링 페이지
- 국장: KOSPI / KOSDAQ (yfinance)
- 미장: S&P 500 / NASDAQ / DOW (yfinance)
- 주요 종목 실시간 시세
"""
import streamlit as st
import datetime
import pandas as pd
from utils.css_loader import apply_custom_css
from utils.data_fetcher import fetch_stock_data, fetch_news_search

apply_custom_css()

# ── 지수 & 종목 정의 ─────────────────────────────────────────────────────
KR_INDICES = {
    "^KS11": "KOSPI",
    "^KQ11": "KOSDAQ",
}
US_INDICES = {
    "^GSPC": "S&P 500",
    "^IXIC": "NASDAQ",
    "^DJI": "DOW Jones",
    "^RUT": "Russell 2000",
}
KR_STOCKS = {
    "005930.KS": "삼성전자",
    "000660.KS": "SK하이닉스",
    "373220.KS": "LG에너지솔루션",
    "005380.KS": "현대자동차",
    "035420.KS": "NAVER",
    "035720.KS": "카카오",
    "006400.KS": "삼성SDI",
    "051910.KS": "LG화학",
}
US_STOCKS = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Alphabet",
    "AMZN": "Amazon",
    "NVDA": "NVIDIA",
    "TSLA": "Tesla",
    "META": "Meta",
    "NFLX": "Netflix",
}

# ── 페이지 헤더 ───────────────────────────────────────────────────────────
st.title("📊 주식 실시간 모니터링")
st.markdown("---")

if st.button("🔄 데이터 갱신", type="primary"):
    st.cache_data.clear()
    st.rerun()

st.caption(f"마지막 갱신: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (5분 자동 캐시)")


# ═══════════════════════════════════════════════════════════════════════════
# 헬퍼 함수
# ═══════════════════════════════════════════════════════════════════════════
def _metric_color(val: float) -> str:
    if val > 0:
        return "🔴"
    elif val < 0:
        return "🔵"
    return "⚪"


def _render_index_row(indices: dict, flag: str):
    """지수 메트릭 카드를 한 줄로 표시."""
    cols = st.columns(len(indices))
    for col, (symbol, name) in zip(cols, indices.items()):
        d = fetch_stock_data(symbol, period="5d")
        with col:
            if d.get("ok"):
                color = _metric_color(d["change"])
                delta_str = f"{d['change']:+,.2f} ({d['change_pct']:+.2f}%)"
                st.metric(f"{flag} {name}", f"{d['price']:,.2f}", delta=delta_str)
            else:
                st.metric(f"{flag} {name}", "N/A", help="데이터 로딩 실패")


def _render_chart_with_stats(symbol: str, name: str, period: str):
    """지수/종목 차트 + 통계 요약."""
    d = fetch_stock_data(symbol, period=period)
    if not d.get("ok") or not d.get("history"):
        st.warning(f"{name} 차트 데이터를 가져오지 못했습니다.")
        return

    df = pd.DataFrame(d["history"])
    st.line_chart(df.set_index("Date")["Close"])

    prices = [r["Close"] for r in d["history"]]
    if prices:
        avg_price = sum(prices) / len(prices)
        total_change = prices[-1] - prices[0]
        total_pct = (total_change / prices[0] * 100) if prices[0] else 0
        sc1, sc2, sc3, sc4, sc5 = st.columns(5)
        sc1.metric("현재", f"{prices[-1]:,.2f}")
        sc2.metric("최고", f"{max(prices):,.2f}")
        sc3.metric("최저", f"{min(prices):,.2f}")
        sc4.metric("평균", f"{avg_price:,.2f}")
        sc5.metric("기간 등락", f"{total_change:+,.2f} ({total_pct:+.1f}%)")


def _render_stock_table(stocks: dict):
    """종목 테이블."""
    rows = []
    for symbol, name in stocks.items():
        d = fetch_stock_data(symbol, period="5d")
        if d.get("ok"):
            rows.append({
                "종목": name,
                "코드": symbol.replace(".KS", ""),
                "현재가": f"{d['price']:,.2f}",
                "전일비": f"{d['change']:+,.2f}",
                "등락률": f"{d['change_pct']:+.2f}%",
                "고가(5일)": f"{d['high']:,.2f}",
                "저가(5일)": f"{d['low']:,.2f}",
                "거래량": f"{d['volume']:,}",
            })
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("종목 데이터를 가져오지 못했습니다.")


# ═══════════════════════════════════════════════════════════════════════════
# 섹션 1: 국내 증시 (국장)
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("## 🇰🇷 국내 증시 실시간 (KOSPI · KOSDAQ)")
_render_index_row(KR_INDICES, "🇰🇷")

kr_period = st.selectbox("국내 차트 기간", ["5d", "1mo", "3mo", "6mo", "1y"], index=1, key="kr_mon_period")

kr_tabs = st.tabs(list(KR_INDICES.values()))
for tab, (symbol, name) in zip(kr_tabs, KR_INDICES.items()):
    with tab:
        st.markdown(f"#### 📈 {name} 추이")
        _render_chart_with_stats(symbol, name, kr_period)

st.markdown("### 🏢 주요 국내 종목 시세")
with st.spinner("국내 종목 로딩 중..."):
    _render_stock_table(KR_STOCKS)

# 국장 뉴스
st.markdown("### 📰 국내 증시 뉴스")
kr_news = fetch_news_search("코스피 코스닥 국내 증시 시황", limit=5)
if kr_news:
    for n in kr_news[:4]:
        title = n.get("title", "")
        link = n.get("link", "")
        source = n.get("source", "")
        published = n.get("published", "")
        with st.expander(f"📰 {title}", expanded=False):
            snippet = n.get("snippet", "")
            if snippet:
                st.write(snippet)
            meta = st.columns([2, 2, 1])
            meta[0].caption(f"📰 {source}")
            meta[1].caption(f"🕒 {published}")
            if link:
                meta[2].link_button("원문 보기", link)
else:
    st.warning("뉴스를 가져오지 못했습니다.")

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════
# 섹션 2: 미국 증시 (미장)
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("## 🇺🇸 미국 증시 실시간 (S&P 500 · NASDAQ · DOW)")
_render_index_row(US_INDICES, "🇺🇸")

us_period = st.selectbox("미국 차트 기간", ["5d", "1mo", "3mo", "6mo", "1y"], index=1, key="us_mon_period")

us_tabs = st.tabs(list(US_INDICES.values()))
for tab, (symbol, name) in zip(us_tabs, US_INDICES.items()):
    with tab:
        st.markdown(f"#### 📈 {name} 추이")
        _render_chart_with_stats(symbol, name, us_period)

st.markdown("### 🏢 주요 미국 종목 시세")
with st.spinner("미국 종목 로딩 중..."):
    _render_stock_table(US_STOCKS)

# 미장 뉴스
st.markdown("### 📰 미국 증시 뉴스")
us_news = fetch_news_search("나스닥 S&P500 다우존스 미국 증시", limit=5)
if us_news:
    for n in us_news[:4]:
        title = n.get("title", "")
        link = n.get("link", "")
        source = n.get("source", "")
        published = n.get("published", "")
        with st.expander(f"📰 {title}", expanded=False):
            snippet = n.get("snippet", "")
            if snippet:
                st.write(snippet)
            meta = st.columns([2, 2, 1])
            meta[0].caption(f"📰 {source}")
            meta[1].caption(f"🕒 {published}")
            if link:
                meta[2].link_button("원문 보기", link)
else:
    st.warning("뉴스를 가져오지 못했습니다.")

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════
# 섹션 3: 국장 vs 미장 비교
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("## 📊 국장 vs 미장 비교")

cmp_period = st.selectbox("비교 기간", ["5d", "1mo", "3mo", "6mo", "1y"], index=1, key="cmp_mon_period")

compare_pairs = [
    ("^KS11", "KOSPI", "^GSPC", "S&P 500"),
    ("^KQ11", "KOSDAQ", "^IXIC", "NASDAQ"),
]

for kr_sym, kr_name, us_sym, us_name in compare_pairs:
    st.markdown(f"### {kr_name} vs {us_name}")
    kr_d = fetch_stock_data(kr_sym, period=cmp_period)
    us_d = fetch_stock_data(us_sym, period=cmp_period)

    c1, c2 = st.columns(2)
    with c1:
        if kr_d.get("ok"):
            delta = f"{kr_d['change']:+,.2f} ({kr_d['change_pct']:+.2f}%)"
            st.metric(f"🇰🇷 {kr_name}", f"{kr_d['price']:,.2f}", delta=delta)
        else:
            st.metric(f"🇰🇷 {kr_name}", "N/A")
    with c2:
        if us_d.get("ok"):
            delta = f"{us_d['change']:+,.2f} ({us_d['change_pct']:+.2f}%)"
            st.metric(f"🇺🇸 {us_name}", f"{us_d['price']:,.2f}", delta=delta)
        else:
            st.metric(f"🇺🇸 {us_name}", "N/A")

    # 정규화 비교 차트 (시작점 = 100)
    if (kr_d.get("ok") and us_d.get("ok")
            and kr_d.get("history") and us_d.get("history")):
        kr_prices = [r["Close"] for r in kr_d["history"]]
        us_prices = [r["Close"] for r in us_d["history"]]
        min_len = min(len(kr_prices), len(us_prices))
        if min_len > 1 and kr_prices[0] and us_prices[0]:
            kr_norm = [p / kr_prices[0] * 100 for p in kr_prices[:min_len]]
            us_norm = [p / us_prices[0] * 100 for p in us_prices[:min_len]]
            dates = [r["Date"] for r in kr_d["history"][:min_len]]
            df_cmp = pd.DataFrame({
                "Date": dates,
                kr_name: kr_norm,
                us_name: us_norm,
            }).set_index("Date")
            st.line_chart(df_cmp)
            st.caption("※ 시작일 = 100 기준 정규화 비교")
    st.markdown("---")

# 종합 비교 테이블
st.markdown("### 📋 주요 지수 종합")
all_idx = {**KR_INDICES, **US_INDICES}
comp_rows = []
for symbol, name in all_idx.items():
    flag = "🇰🇷" if symbol.startswith("^K") else "🇺🇸"
    d = fetch_stock_data(symbol, period="5d")
    if d.get("ok"):
        comp_rows.append({
            "지수": f"{flag} {name}",
            "현재": f"{d['price']:,.2f}",
            "전일비": f"{d['change']:+,.2f}",
            "등락률": f"{d['change_pct']:+.2f}%",
            "5일 고가": f"{d['high']:,.2f}",
            "5일 저가": f"{d['low']:,.2f}",
        })
if comp_rows:
    st.dataframe(pd.DataFrame(comp_rows), use_container_width=True, hide_index=True)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════
# 섹션 4: 외부 모니터링 링크
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("## 🔗 실시간 증시 외부 모니터링")
link_cols = st.columns(3)
with link_cols[0]:
    st.link_button("📊 네이버 증권", "https://finance.naver.com/", use_container_width=True)
    st.link_button("📊 KRX 정보", "http://data.krx.co.kr/", use_container_width=True)
with link_cols[1]:
    st.link_button("🇺🇸 Yahoo Finance", "https://finance.yahoo.com/", use_container_width=True)
    st.link_button("🇺🇸 CNBC Markets", "https://www.cnbc.com/markets/", use_container_width=True)
with link_cols[2]:
    st.link_button("📈 인베스팅닷컴", "https://kr.investing.com/indices/", use_container_width=True)
    st.link_button("📈 TradingView", "https://www.tradingview.com/", use_container_width=True)
