# -*- coding: utf-8 -*-
"""주식 실시간 모니터링 – 국장(KOSPI/KOSDAQ) & 미장(S&P500/NASDAQ/DOW)"""
import streamlit as st
import pandas as pd
import datetime
from utils.css_loader import apply_custom_css
from utils.data_fetcher import fetch_stock_data, fetch_news_search, fetch_web_search, fetch_youtube_search
from utils.report_downloader import render_download_buttons

apply_custom_css()

st.title("📈 주식 실시간 모니터링")
st.markdown("---")

# ── 갱신 버튼 ─────────────────────────────────────────────────────────────
col_r, col_t = st.columns([1, 3])
with col_r:
    if st.button("🔄 데이터 갱신", type="primary"):
        st.cache_data.clear()
        st.rerun()
with col_t:
    st.caption(f"마지막 갱신: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (5분 자동 캐시)")

# ═══════════════════════════════════════════════════════════════════════════
# 지수 정의
# ═══════════════════════════════════════════════════════════════════════════
KR_INDICES = {
    "^KS11": ("KOSPI", "🇰🇷"),
    "^KQ11": ("KOSDAQ", "🇰🇷"),
}
US_INDICES = {
    "^GSPC": ("S&P 500", "🇺🇸"),
    "^IXIC": ("NASDAQ", "🇺🇸"),
    "^DJI": ("DOW", "🇺🇸"),
    "^RUT": ("Russell 2000", "🇺🇸"),
}
POPULAR_KR_STOCKS = {
    "005930.KS": "삼성전자",
    "000660.KS": "SK하이닉스",
    "373220.KS": "LG에너지솔루션",
    "005380.KS": "현대자동차",
    "035420.KS": "NAVER",
    "035720.KS": "카카오",
}
POPULAR_US_STOCKS = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Alphabet",
    "AMZN": "Amazon",
    "NVDA": "NVIDIA",
    "TSLA": "Tesla",
    "META": "Meta",
}

# ═══════════════════════════════════════════════════════════════════════════
# 탭 구성
# ═══════════════════════════════════════════════════════════════════════════
tab_kr, tab_us, tab_compare, tab_expert = st.tabs([
    "🇰🇷 국내 증시", "🇺🇸 미국 증시", "📊 국장 vs 미장", "📝 전문가 분석"
])


def _render_index_metrics(indices: dict):
    """지수 메트릭 카드 렌더링."""
    cols = st.columns(len(indices))
    results = {}
    for col, (symbol, (name, flag)) in zip(cols, indices.items()):
        data = fetch_stock_data(symbol, period="5d")
        results[symbol] = data
        with col:
            if data.get("ok"):
                delta = f"{data['change']:+,.2f} ({data['change_pct']:+.2f}%)"
                col.metric(f"{flag} {name}", f"{data['price']:,.2f}", delta=delta)
            else:
                col.metric(f"{flag} {name}", "N/A", help="데이터 로딩 실패")
    return results


def _render_index_chart(symbol: str, name: str, period: str = "1mo"):
    """지수 차트 + 통계."""
    data = fetch_stock_data(symbol, period=period)
    if data.get("ok") and data.get("history"):
        df = pd.DataFrame(data["history"])
        st.line_chart(df.set_index("Date")["Close"])

        prices = [r["Close"] for r in data["history"]]
        sc1, sc2, sc3, sc4 = st.columns(4)
        sc1.metric("최고", f"{max(prices):,.2f}")
        sc2.metric("최저", f"{min(prices):,.2f}")
        sc3.metric("평균", f"{sum(prices)/len(prices):,.2f}")
        change_total = prices[-1] - prices[0]
        sc4.metric("기간 변동", f"{change_total:+,.2f}")
    else:
        st.warning(f"{name} 차트 데이터를 가져오지 못했습니다.")


def _render_stock_table(stocks: dict):
    """개별 종목 테이블."""
    rows = []
    for symbol, name in stocks.items():
        data = fetch_stock_data(symbol, period="5d")
        if data.get("ok"):
            rows.append({
                "종목": name,
                "코드": symbol,
                "현재가": f"{data['price']:,.2f}",
                "전일비": f"{data['change']:+,.2f}",
                "등락률": f"{data['change_pct']:+.2f}%",
                "고가": f"{data['high']:,.2f}",
                "저가": f"{data['low']:,.2f}",
            })
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("종목 데이터를 가져오지 못했습니다.")


# ── 탭 1: 국내 증시 ──────────────────────────────────────────────────────
with tab_kr:
    st.markdown("## 🇰🇷 국내 증시 실시간 현황")
    kr_data = _render_index_metrics(KR_INDICES)

    period_kr = st.selectbox("차트 기간", ["5d", "1mo", "3mo", "6mo", "1y"], index=1, key="kr_period")

    st.markdown("### 📈 KOSPI 추이")
    _render_index_chart("^KS11", "KOSPI", period_kr)

    st.markdown("### 📈 KOSDAQ 추이")
    _render_index_chart("^KQ11", "KOSDAQ", period_kr)

    st.markdown("### 🏢 주요 국내 종목")
    with st.spinner("종목 데이터 로딩 중..."):
        _render_stock_table(POPULAR_KR_STOCKS)

    st.markdown("### 📰 국내 증시 뉴스")
    kr_news = fetch_news_search("코스피 코스닥 국내 증시 시황", limit=5)
    if kr_news:
        for n in kr_news[:4]:
            st.markdown(
                f"- **[{n['title']}]({n['link']})**  \n"
                f"  <small>{n.get('source', '')} | {n.get('published', '')}</small>",
                unsafe_allow_html=True,
            )
    else:
        st.info("뉴스를 가져오지 못했습니다.")

# ── 탭 2: 미국 증시 ──────────────────────────────────────────────────────
with tab_us:
    st.markdown("## 🇺🇸 미국 증시 실시간 현황")
    us_data = _render_index_metrics(US_INDICES)

    period_us = st.selectbox("차트 기간", ["5d", "1mo", "3mo", "6mo", "1y"], index=1, key="us_period")

    st.markdown("### 📈 S&P 500 추이")
    _render_index_chart("^GSPC", "S&P 500", period_us)

    st.markdown("### 📈 NASDAQ 추이")
    _render_index_chart("^IXIC", "NASDAQ", period_us)

    st.markdown("### 🏢 주요 미국 종목")
    with st.spinner("종목 데이터 로딩 중..."):
        _render_stock_table(POPULAR_US_STOCKS)

    st.markdown("### 📰 미국 증시 뉴스")
    us_news = fetch_news_search("나스닥 S&P500 다우존스 미국 증시", limit=5)
    if us_news:
        for n in us_news[:4]:
            st.markdown(
                f"- **[{n['title']}]({n['link']})**  \n"
                f"  <small>{n.get('source', '')} | {n.get('published', '')}</small>",
                unsafe_allow_html=True,
            )
    else:
        st.info("뉴스를 가져오지 못했습니다.")

# ── 탭 3: 국장 vs 미장 비교 ──────────────────────────────────────────────
with tab_compare:
    st.markdown("## 📊 국장 vs 미장 비교")

    period_cmp = st.selectbox("비교 기간", ["5d", "1mo", "3mo", "6mo", "1y"], index=1, key="cmp_period")

    compare_pairs = [
        ("^KS11", "KOSPI", "^GSPC", "S&P 500"),
        ("^KQ11", "KOSDAQ", "^IXIC", "NASDAQ"),
    ]

    for kr_sym, kr_name, us_sym, us_name in compare_pairs:
        st.markdown(f"### {kr_name} vs {us_name}")
        kr_d = fetch_stock_data(kr_sym, period=period_cmp)
        us_d = fetch_stock_data(us_sym, period=period_cmp)

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

        # 정규화 차트 (시작점=100 기준)
        if kr_d.get("ok") and us_d.get("ok") and kr_d.get("history") and us_d.get("history"):
            kr_prices = [r["Close"] for r in kr_d["history"]]
            us_prices = [r["Close"] for r in us_d["history"]]
            min_len = min(len(kr_prices), len(us_prices))
            if min_len > 1:
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

    # 통합 비교 테이블
    st.markdown("### 📋 주요 지수 종합 비교")
    all_indices = {**KR_INDICES, **US_INDICES}
    comp_rows = []
    for symbol, (name, flag) in all_indices.items():
        d = fetch_stock_data(symbol, period="5d")
        if d.get("ok"):
            comp_rows.append({
                "지수": f"{flag} {name}",
                "현재": f"{d['price']:,.2f}",
                "전일비": f"{d['change']:+,.2f}",
                "등락률": f"{d['change_pct']:+.2f}%",
                "고가": f"{d['high']:,.2f}",
                "저가": f"{d['low']:,.2f}",
            })
    if comp_rows:
        st.dataframe(pd.DataFrame(comp_rows), use_container_width=True, hide_index=True)

# ── 탭 4: 전문가 분석 ────────────────────────────────────────────────────
with tab_expert:
    st.markdown("## 📝 주식 전문가 분석")

    query = st.text_input("🔍 주식 관련 검색어 입력", value="국내 코스피 코스닥 미국 증시 주식 시황 분석")
    state_key = "expert_data_주식 분석"

    if st.button("데이터 분석 및 리포트 갱신", type="primary", use_container_width=True):
        with st.spinner("최신 트렌드 및 뉴스 수집 중..."):
            web_results = fetch_web_search(query, limit=5)
            news_results = fetch_news_search(query, limit=5)
            youtube_results = fetch_youtube_search(query, limit=12)

            dates = pd.date_range(end=datetime.datetime.today(), periods=7).strftime('%m-%d').tolist()

            # 실시간 KOSPI 데이터 기반 트렌드
            kospi = fetch_stock_data("^KS11", period="5d")
            if kospi.get("ok") and kospi.get("history"):
                values = [r["Close"] for r in kospi["history"][-7:]]
                # 날짜 수 맞추기
                while len(values) < 7:
                    values.insert(0, values[0] if values else 2500)
                values = values[:7]
            else:
                values = [6020, 6080, 5010, 4950, 5100, 5150, 5200]

            df = pd.DataFrame({"Date": dates, "Trend": values})

            st.session_state[state_key] = {
                "query": query,
                "web": web_results,
                "news": news_results,
                "youtube": youtube_results,
                "df": df,
                "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

    data = st.session_state.get(state_key)
    if data:
        st.success(f"최근 분석 완료: {data['updated_at']}")

        st.markdown(f"### 📈 최근 '{data['query']}' 트렌드")
        st.bar_chart(data["df"].set_index("Date"))

        st.markdown("### 📰 핵심 관련 뉴스")
        if data["news"]:
            for n in data["news"][:3]:
                st.markdown(
                    f"- **[{n['title']}]({n['link']})**  \n"
                    f"  <small>{n.get('source', '')} | {n.get('published', '')}</small>",
                    unsafe_allow_html=True,
                )
        else:
            st.info("관련 뉴스를 찾지 못했습니다.")

        st.markdown("---")
        st.markdown("### 🌐 웹 검색 결과 요약")
        if data["web"]:
            for w in data["web"][:3]:
                st.markdown(
                    f"- **[{w['title']}]({w['link']})**  \n"
                    f"  <small>{w.get('snippet', '')}</small>",
                    unsafe_allow_html=True,
                )
        else:
            st.info("관련 웹 검색 결과를 찾지 못했습니다.")

        st.markdown("---")
        st.markdown("### 🎬 관련 YouTube 영상")
        from utils.expert_template import _render_video_card, _parse_view_count
        import math as _math
        if data.get("youtube"):
            videos = sorted(data["youtube"], key=lambda v: _parse_view_count(v.get("view_count")), reverse=True)
            _per_page = 4
            _total_pages = max(1, _math.ceil(len(videos) / _per_page))
            _pk = "yt_stock_expert"
            if _pk not in st.session_state:
                st.session_state[_pk] = 0
            _cp = st.session_state[_pk]
            _s, _e = _cp * _per_page, min((_cp + 1) * _per_page, len(videos))
            cols = st.columns(2)
            for idx, v in enumerate(videos[_s:_e]):
                with cols[idx % 2]:
                    _render_video_card(v, show_desc=True)
            if _total_pages > 1:
                nav_cols = st.columns(_total_pages + 2)
                with nav_cols[0]:
                    if st.button("◀", key=f"{_pk}_prev", disabled=(_cp == 0)):
                        st.session_state[_pk] = _cp - 1
                        st.rerun()
                for _p in range(_total_pages):
                    with nav_cols[_p + 1]:
                        _lbl = f"**[{_p+1}]**" if _p == _cp else f"{_p+1}"
                        if st.button(_lbl, key=f"{_pk}_p{_p}"):
                            st.session_state[_pk] = _p
                            st.rerun()
                with nav_cols[_total_pages + 1]:
                    if st.button("▶", key=f"{_pk}_next", disabled=(_cp >= _total_pages - 1)):
                        st.session_state[_pk] = _cp + 1
                        st.rerun()
                st.caption(f"페이지 {_cp + 1} / {_total_pages} (총 {len(videos)}건)")
        else:
            st.info("관련 YouTube 영상을 찾지 못했습니다.")

        st.markdown("---")
        trend_records = []
        if isinstance(data.get("df"), pd.DataFrame) and not data["df"].empty:
            trend_records = data["df"].to_dict("records")

        data_context = {
            "query": data["query"],
            "news": data["news"],
            "web": data["web"],
            "youtube": data.get("youtube", []),
            "df": trend_records,
        }
        render_download_buttons(context=data_context)
    else:
        st.info("상단 버튼을 눌러 데이터를 수집하고 인사이트를 확인하세요.")

# ── 관련 YouTube 영상 ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## 🎬 주식·증시 관련 YouTube 영상")
from utils.expert_template import render_youtube_section
_yt_stock12 = render_youtube_section("주식 시황 분석 코스피 나스닥 증시")

# ── 외부 참고 링크 ────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🔗 외부 증시 모니터링")
lk1, lk2, lk3 = st.columns(3)
with lk1:
    st.link_button("📊 네이버 증권", "https://finance.naver.com/", use_container_width=True)
    st.link_button("📊 KRX 정보", "http://data.krx.co.kr/", use_container_width=True)
with lk2:
    st.link_button("🇺🇸 Yahoo Finance", "https://finance.yahoo.com/", use_container_width=True)
    st.link_button("🇺🇸 CNBC Markets", "https://www.cnbc.com/markets/", use_container_width=True)
with lk3:
    st.link_button("📈 인베스팅닷컴", "https://kr.investing.com/indices/", use_container_width=True)
    st.link_button("📈 TradingView", "https://www.tradingview.com/", use_container_width=True)
