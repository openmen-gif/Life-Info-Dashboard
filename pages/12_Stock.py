# -*- coding: utf-8 -*-
"""주식 실시간 모니터링 – 국장(KOSPI/KOSDAQ) & 미장(S&P500/NASDAQ/DOW)"""
import streamlit as st
import pandas as pd
import datetime
from utils.css_loader import apply_custom_css
from utils.data_fetcher import fetch_stock_data, fetch_kr_index, fetch_news_search, fetch_web_search, fetch_youtube_search
from utils.report_downloader import render_download_buttons

apply_custom_css()

st.title("📈 주식 실시간 모니터링")
st.markdown("---")

# ── 갱신 버튼 ─────────────────────────────────────────────────────────────
col_r, col_t = st.columns([1, 3])
with col_r:
    if st.button("🔄 데이터 갱신", type="primary"):
        fetch_stock_data.clear()
        fetch_news_search.clear()
        fetch_web_search.clear()
        fetch_youtube_search.clear()
        st.rerun()
with col_t:
    st.caption(f"마지막 갱신: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (5분 자동 캐시)")

# ═══════════════════════════════════════════════════════════════════════════
# 지수 정의
# ═══════════════════════════════════════════════════════════════════════════
KR_INDICES = {
    "KOSPI": ("KOSPI", "🇰🇷"),
    "KOSDAQ": ("KOSDAQ", "🇰🇷"),
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
tab_kr, tab_us, tab_compare, tab_watchlist, tab_expert = st.tabs([
    "🇰🇷 국내 증시", "🇺🇸 미국 증시", "📊 국장 vs 미장", "⭐ 관심 종목", "📝 전문가 분석"
])


def _is_valid_num(v) -> bool:
    """NaN/None 체크."""
    import math
    if v is None:
        return False
    try:
        return not math.isnan(float(v))
    except (TypeError, ValueError):
        return False


def _render_index_metrics(indices: dict, use_naver: bool = False):
    """지수 메트릭 카드 렌더링. use_naver=True면 네이버 금융 API 사용."""
    cols = st.columns(len(indices))
    results = {}
    for col, (symbol, (name, flag)) in zip(cols, indices.items()):
        data = fetch_kr_index(symbol) if use_naver else fetch_stock_data(symbol, period="5d")
        results[symbol] = data
        with col:
            if data.get("ok") and _is_valid_num(data.get("price")):
                delta = f"{data['change']:+,.2f} ({data['change_pct']:+.2f}%)"
                col.metric(f"{flag} {name}", f"{data['price']:,.2f}", delta=delta)
            else:
                col.metric(f"{flag} {name}", "N/A", help="데이터 로딩 실패")
    return results


def _render_index_chart(symbol: str, name: str, period: str = "1mo"):
    """지수 차트 + 통계 (미국 지수용 — yfinance)."""
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


def _render_kr_index_chart(code: str, name: str, period: str = "1mo"):
    """국내 지수 차트 + 통계 (네이버 금융 API)."""
    data = fetch_kr_index(code, period=period)
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
    kr_data = _render_index_metrics(KR_INDICES, use_naver=True)

    period_kr = st.selectbox("차트 기간", ["5d", "1mo", "3mo", "6mo", "1y"], index=1, key="kr_period")

    st.markdown("### 📈 KOSPI 추이")
    _render_kr_index_chart("KOSPI", "KOSPI", period_kr)

    st.markdown("### 📈 KOSDAQ 추이")
    _render_kr_index_chart("KOSDAQ", "KOSDAQ", period_kr)

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
        ("069500.KS", "KOSPI", "^GSPC", "S&P 500"),
        ("229200.KS", "KOSDAQ", "^IXIC", "NASDAQ"),
    ]

    for kr_sym, kr_name, us_sym, us_name in compare_pairs:
        st.markdown(f"### {kr_name} vs {us_name}")
        us_d = fetch_stock_data(us_sym, period=period_cmp)
        kr_idx = fetch_kr_index(kr_name)  # 실제 지수값 (네이버 금융)

        c1, c2 = st.columns(2)
        with c1:
            if kr_idx.get("ok") and _is_valid_num(kr_idx.get("price")):
                delta = f"{kr_idx['change']:+,.2f} ({kr_idx['change_pct']:+.2f}%)"
                st.metric(f"🇰🇷 {kr_name}", f"{kr_idx['price']:,.2f}", delta=delta)
            else:
                st.metric(f"🇰🇷 {kr_name}", "N/A")
        with c2:
            if us_d.get("ok") and _is_valid_num(us_d.get("price")):
                delta = f"{us_d['change']:+,.2f} ({us_d['change_pct']:+.2f}%)"
                st.metric(f"🇺🇸 {us_name}", f"{us_d['price']:,.2f}", delta=delta)
            else:
                st.metric(f"🇺🇸 {us_name}", "N/A")

        # 정규화 차트 (ETF 기반, 시작점=100 기준)
        kr_d_chart = fetch_stock_data(kr_sym, period=period_cmp)
        if kr_d_chart.get("ok") and us_d.get("ok") and kr_d_chart.get("history") and us_d.get("history"):
            kr_prices = [r["Close"] for r in kr_d_chart["history"]]
            us_prices = [r["Close"] for r in us_d["history"]]
            min_len = min(len(kr_prices), len(us_prices))
            if min_len > 1:
                kr_norm = [p / kr_prices[0] * 100 for p in kr_prices[:min_len]]
                us_norm = [p / us_prices[0] * 100 for p in us_prices[:min_len]]
                dates = [r["Date"] for r in kr_d_chart["history"][:min_len]]
                df_cmp = pd.DataFrame({
                    "Date": dates,
                    kr_name: kr_norm,
                    us_name: us_norm,
                }).set_index("Date")
                st.line_chart(df_cmp)
                st.caption("※ 시작일 = 100 기준 정규화 비교 (ETF 기반 차트)")
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

# ── 탭 4: 관심 종목 ──────────────────────────────────────────────────────
with tab_watchlist:
    st.markdown("## ⭐ 나의 관심 종목")
    st.caption("종목 코드를 추가하면 실시간 시세와 전문가 분석을 확인할 수 있습니다.")

    # 세션 관리
    if "watchlist" not in st.session_state:
        st.session_state.watchlist = ["005930.KS", "NVDA", "TSLA"]

    # 종목 추가 UI
    col_add1, col_add2, col_add3 = st.columns([2, 2, 1])
    with col_add1:
        new_symbol = st.text_input("종목 코드 입력", placeholder="예: 005930.KS, AAPL, TSLA", key="wl_new_sym")
    with col_add2:
        st.markdown("")
        st.markdown("")
        st.caption("국내: 종목번호.KS (예: 005930.KS)\n미국: 티커 (예: AAPL)")
    with col_add3:
        st.markdown("")
        st.markdown("")
        if st.button("➕ 추가", use_container_width=True, key="wl_add_btn"):
            sym = new_symbol.strip().upper()
            if sym and sym not in st.session_state.watchlist:
                st.session_state.watchlist.append(sym)
                st.rerun()

    # 관심 종목 삭제 UI
    if st.session_state.watchlist:
        remove_sym = st.multiselect("삭제할 종목 선택", st.session_state.watchlist, key="wl_remove")
        if st.button("🗑️ 선택 종목 삭제", key="wl_remove_btn"):
            st.session_state.watchlist = [s for s in st.session_state.watchlist if s not in remove_sym]
            st.rerun()

    st.markdown("---")

    # 관심 종목 시세 표시
    if st.session_state.watchlist:
        st.markdown("### 📊 실시간 시세")
        wl_cols = st.columns(min(len(st.session_state.watchlist), 4))
        for i, sym in enumerate(st.session_state.watchlist):
            with wl_cols[i % len(wl_cols)]:
                d = fetch_stock_data(sym, period="5d")
                if d.get("ok") and _is_valid_num(d.get("price")):
                    is_kr = sym.endswith((".KS", ".KQ"))
                    price_fmt = f"{d['price']:,.0f}" if is_kr else f"${d['price']:,.2f}"
                    delta = f"{d['change']:+,.2f} ({d['change_pct']:+.2f}%)"
                    st.metric(sym, price_fmt, delta=delta)
                else:
                    st.metric(sym, "N/A", help="데이터 로딩 실패")

        # 관심 종목 차트
        st.markdown("### 📈 관심 종목 차트")
        wl_period = st.selectbox("차트 기간", ["5d", "1mo", "3mo", "6mo", "1y"], index=1, key="wl_period")
        for sym in st.session_state.watchlist:
            d = fetch_stock_data(sym, period=wl_period)
            if d.get("ok") and d.get("history"):
                st.markdown(f"**{sym}**")
                df = pd.DataFrame(d["history"])
                st.line_chart(df.set_index("Date")["Close"])

        # 관심 종목 관련 뉴스
        st.markdown("---")
        st.markdown("### 📰 관심 종목 관련 뉴스")
        wl_query = " ".join(st.session_state.watchlist[:5])
        wl_news = fetch_news_search(f"주식 {wl_query} 시황", limit=5)
        if wl_news:
            for n in wl_news[:4]:
                st.markdown(
                    f"- **[{n['title']}]({n['link']})**  \n"
                    f"  <small>{n.get('source', '')} | {n.get('published', '')}</small>",
                    unsafe_allow_html=True,
                )
        else:
            st.info("관련 뉴스를 가져오지 못했습니다.")
    else:
        st.info("관심 종목을 추가해 주세요.")

# ── 탭 5: 전문가 분석 ────────────────────────────────────────────────────
with tab_expert:
    st.markdown("## 📝 주식 전문가 분석")

    query = st.text_input("🔍 주식 관련 검색어 입력", value="국내 코스피 코스닥 미국 증시 주식 시황 분석")
    state_key = "expert_data_주식 분석"

    if st.button("데이터 분석 및 리포트 갱신", type="primary", use_container_width=True):
        with st.spinner("최신 트렌드 및 뉴스 수집 중..."):
            web_results = fetch_web_search(query, limit=5)
            news_results = fetch_news_search(query, limit=5)
            youtube_results = fetch_youtube_search(query, limit=12, timelimit="w")

            dates = pd.date_range(end=datetime.datetime.today(), periods=7).strftime('%m-%d').tolist()

            # 실시간 KOSPI 데이터 기반 트렌드
            kospi = fetch_stock_data("069500.KS", period="5d")
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

        # ── 시장 심리 분석 ────────────────────────────────────────────
        st.markdown("### 🧠 시장 심리 분석")
        if data["news"]:
            import re
            from collections import Counter

            pos_words = {
                "상승", "급등", "호재", "성장", "개선", "회복", "활황", "강세",
                "최고", "돌파", "증가", "확대", "호조", "긍정", "기대", "랠리",
                "반등", "호황", "흑자", "신고가", "매수", "수혜",
            }
            neg_words = {
                "하락", "급락", "악재", "위축", "감소", "둔화", "약세", "최저",
                "폭락", "축소", "부진", "우려", "경고", "위기", "리스크", "적자",
                "침체", "하방", "손실", "붕괴", "매도", "조정",
            }
            all_titles = " ".join(n.get("title", "") for n in data["news"])
            words = re.findall(r"[가-힣]{2,}", all_titles)

            pos_count = sum(1 for w in words if w in pos_words)
            neg_count = sum(1 for w in words if w in neg_words)
            total_s = pos_count + neg_count

            if total_s == 0:
                sentiment = "중립"
                sentiment_score = 50
            else:
                sentiment_score = int(pos_count / total_s * 100)
                if sentiment_score >= 60:
                    sentiment = "긍정적 (매수 심리 우세)"
                elif sentiment_score <= 40:
                    sentiment = "부정적 (매도 심리 우세)"
                else:
                    sentiment = "혼조 (관망세)"

            sentiment_icon = {"긍정적 (매수 심리 우세)": "🟢", "부정적 (매도 심리 우세)": "🔴",
                              "혼조 (관망세)": "🟡", "중립": "⚪"}
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("분석 기사 수", f"{len(data['news'])}건")
            m2.metric("시장 심리", f"{sentiment_icon.get(sentiment, '⚪')} {sentiment}")
            m3.metric("긍정/부정 비율", f"{pos_count}:{neg_count}")
            m4.metric("심리 지수", f"{sentiment_score}/100")

            # 핵심 키워드 빈도
            stopwords = {"것으로", "에서", "관련", "대한", "위한", "으로", "이번",
                         "오늘", "내일", "지난", "올해", "이후", "까지", "부터",
                         "하는", "있는", "없는", "되는"}
            filtered = [w for w in words if w not in stopwords]
            word_freq = Counter(filtered).most_common(10)
            if word_freq:
                st.markdown("**핵심 키워드 빈도**")
                kw_df = pd.DataFrame(word_freq, columns=["키워드", "빈도"])
                st.bar_chart(kw_df.set_index("키워드"))

        st.markdown("---")

        st.markdown("### 📰 핵심 관련 뉴스")
        if data["news"]:
            for n in data["news"][:5]:
                st.markdown(
                    f"- **[{n['title']}]({n['link']})**  \n"
                    f"  <small>{n.get('source', '')} | {n.get('published', '')}</small>",
                    unsafe_allow_html=True,
                )
        else:
            st.info("관련 뉴스를 찾지 못했습니다.")

        st.markdown("---")

        # ── 투자 분석 프레임워크 ──────────────────────────────────────
        st.markdown("### 🎯 투자 분석 프레임워크")
        fw1, fw2 = st.columns(2)
        with fw1:
            st.markdown("#### 📊 기본적 분석 체크포인트")
            st.markdown("""
- **거시경제**: 금리, 환율, 유가 변동 추이
- **기업실적**: 분기 실적 발표 및 가이던스
- **밸류에이션**: PER, PBR, ROE 비교
- **수급 동향**: 외국인/기관 매매 동향
- **정책 이벤트**: 통화정책, 재정정책 변화
            """)
        with fw2:
            st.markdown("#### 📈 기술적 분석 체크포인트")
            st.markdown("""
- **추세**: 이동평균선(5/20/60/120일) 배열
- **모멘텀**: RSI, MACD, 스토캐스틱
- **거래량**: 거래량 이동평균 대비 수준
- **지지/저항**: 주요 가격대 및 심리적 가격선
- **패턴**: 캔들 패턴, 차트 패턴 확인
            """)

        st.markdown("#### ⚠️ 리스크 요인 점검")
        r1, r2, r3 = st.columns(3)
        with r1:
            st.markdown("**글로벌 리스크**")
            st.markdown("- 미국 금리 정책 변화\n- 지정학적 리스크\n- 글로벌 공급망 이슈")
        with r2:
            st.markdown("**국내 리스크**")
            st.markdown("- 원/달러 환율 변동\n- 가계부채 수준\n- 부동산 시장 연동")
        with r3:
            st.markdown("**섹터 리스크**")
            st.markdown("- 반도체 사이클 변동\n- AI/테크 밸류에이션\n- 규제 환경 변화")

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
        st.markdown("### 🎬 관련 영상")
        from utils.expert_template import _render_paginated_videos
        if data.get("youtube"):
            videos = sorted(data["youtube"], key=lambda v: v.get("published", ""), reverse=True)
            _render_paginated_videos(videos, "yt_stock_expert")
        else:
            st.info("관련 영상을 찾지 못했습니다.")

        st.markdown("---")

        st.warning(
            "⚠️ 본 분석은 공개된 뉴스·데이터 기반 자동 수집 결과이며 투자 권유가 아닙니다. "
            "투자 결정은 본인 판단과 책임하에 이루어져야 합니다."
        )

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

# ── 관련 영상 ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## 🎬 주식·증시 관련 영상")
from utils.expert_template import render_youtube_section
_yt_stock12 = render_youtube_section("주식 시황 분석 코스피 나스닥 증시", sort="latest")

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
