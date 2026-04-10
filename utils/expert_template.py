import streamlit as st
import datetime
import re
from collections import Counter
import pandas as pd
from utils.data_fetcher import fetch_web_search, fetch_news_search, fetch_youtube_search
from utils.report_downloader import render_download_buttons

# ── 감성 분석 키워드 사전 ─────────────────────────────────────────────────
_POSITIVE_WORDS = {
    "상승", "급등", "호재", "성장", "개선", "회복", "활황", "강세", "최고",
    "돌파", "증가", "확대", "호조", "긍정", "수혜", "기대", "추천", "인기",
    "혁신", "돌파구", "신기록", "랠리", "반등", "호황", "흑자", "대박",
}
_NEGATIVE_WORDS = {
    "하락", "급락", "악재", "위축", "감소", "둔화", "약세", "최저",
    "폭락", "축소", "부진", "우려", "경고", "위기", "리스크", "적자",
    "침체", "하방", "손실", "붕괴", "악화", "불안", "충격", "규제",
}


def _analyze_news_trends(news_list: list[dict]) -> dict:
    """뉴스 제목에서 키워드 빈도 + 감성 경향 분석."""
    if not news_list:
        return {}

    all_titles = " ".join(n.get("title", "") for n in news_list)
    # 한글 키워드 추출 (2글자 이상)
    words = re.findall(r"[가-힣]{2,}", all_titles)
    # 불용어 제거
    stopwords = {"것으로", "에서", "관련", "대한", "위한", "으로", "이번", "오늘", "내일",
                 "지난", "올해", "이후", "까지", "부터", "하는", "있는", "없는", "되는"}
    words = [w for w in words if w not in stopwords]
    word_freq = Counter(words).most_common(10)

    # 감성 분석
    pos_count = sum(1 for w in words if w in _POSITIVE_WORDS)
    neg_count = sum(1 for w in words if w in _NEGATIVE_WORDS)
    total_sentiment = pos_count + neg_count

    if total_sentiment == 0:
        sentiment = "중립"
        sentiment_score = 50
    else:
        sentiment_score = int(pos_count / total_sentiment * 100)
        if sentiment_score >= 60:
            sentiment = "긍정적"
        elif sentiment_score <= 40:
            sentiment = "부정적"
        else:
            sentiment = "혼조"

    # 출처 분포
    sources = [n.get("source", "기타") for n in news_list if n.get("source")]
    source_freq = Counter(sources).most_common(5)

    return {
        "word_freq": word_freq,
        "sentiment": sentiment,
        "sentiment_score": sentiment_score,
        "pos_count": pos_count,
        "neg_count": neg_count,
        "source_freq": source_freq,
        "total_articles": len(news_list),
    }


def _render_news_trends(news_list: list[dict], title: str):
    """뉴스 경향 분석 결과를 Streamlit 위젯으로 표시."""
    analysis = _analyze_news_trends(news_list)
    if not analysis:
        return

    st.markdown(f"#### 📊 {title} 뉴스 경향 분석")

    # 감성 + 기사 수
    c1, c2, c3 = st.columns(3)
    c1.metric("분석 기사 수", f"{analysis['total_articles']}건")

    sentiment_icon = {"긍정적": "🟢", "부정적": "🔴", "혼조": "🟡", "중립": "⚪"}
    c2.metric("전체 감성", f"{sentiment_icon.get(analysis['sentiment'], '⚪')} {analysis['sentiment']}")
    c3.metric("긍정/부정 비율", f"{analysis['pos_count']}:{analysis['neg_count']}")

    # 키워드 빈도 차트
    if analysis["word_freq"]:
        kw_df = pd.DataFrame(analysis["word_freq"], columns=["키워드", "빈도"])
        st.markdown("**핵심 키워드 빈도**")
        st.bar_chart(kw_df.set_index("키워드"))

    # 출처 분포
    if analysis["source_freq"]:
        src_text = " · ".join(f"{s}({c}건)" for s, c in analysis["source_freq"])
        st.caption(f"📰 주요 출처: {src_text}")


def _parse_view_count(vc) -> int:
    """Parse view count string to int for sorting."""
    if not vc:
        return 0
    s = str(vc).replace(",", "").replace("회", "").replace("views", "").strip()
    try:
        return int(s)
    except ValueError:
        return 0


def _show_empty_state(msg: str):
    """데이터 없음 상태 + 재시도 안내."""
    st.info(f"{msg} 상단 🔄 데이터 갱신 버튼을 눌러 다시 시도하세요.")


_PLATFORM_ICONS = {
    "YouTube": "▶️", "Naver TV": "🟢", "Kakao": "💬",
    "TikTok": "🎵", "X": "🐦", "Instagram": "📸",
    "Facebook": "👤", "Vimeo": "🎬",
}


def _render_paginated_videos(videos: list[dict], page_key: str, per_page: int = 4):
    """Shared helper: render paginated video grid with navigation."""
    import math
    total = len(videos)
    total_pages = max(1, math.ceil(total / per_page))
    if page_key not in st.session_state:
        st.session_state[page_key] = 0
    cp = st.session_state[page_key]
    s, e = cp * per_page, min((cp + 1) * per_page, total)

    cols = st.columns(2)
    for idx, v in enumerate(videos[s:e]):
        with cols[idx % 2]:
            _render_video_card(v, show_desc=True)

    if total_pages > 1:
        nav_cols = st.columns(total_pages + 2)
        with nav_cols[0]:
            if st.button("◀", key=f"{page_key}_prev", disabled=(cp == 0)):
                st.session_state[page_key] = cp - 1
                st.rerun()
        for p in range(total_pages):
            with nav_cols[p + 1]:
                label = f"**[{p+1}]**" if p == cp else f"{p+1}"
                if st.button(label, key=f"{page_key}_p{p}"):
                    st.session_state[page_key] = p
                    st.rerun()
        with nav_cols[total_pages + 1]:
            if st.button("▶", key=f"{page_key}_next", disabled=(cp >= total_pages - 1)):
                st.session_state[page_key] = cp + 1
                st.rerun()
        st.caption(f"페이지 {cp + 1} / {total_pages} (총 {total}건)")


def _render_video_card(v: dict, show_desc: bool = False):
    """Render a single video card (YouTube + other platforms)."""
    thumbnail = v.get("thumbnail", "")
    if thumbnail:
        st.image(thumbnail, use_container_width=True)
    st.markdown(f"**[{v['title']}]({v['url']})**")

    # Metadata line
    meta_parts = []
    platform = v.get("platform", "")
    if platform and platform != "YouTube":
        icon = _PLATFORM_ICONS.get(platform, "🎬")
        meta_parts.append(f"{icon} {platform}")
    if v.get("uploader"):
        meta_parts.append(f"📺 {v['uploader']}")
    if v.get("duration"):
        meta_parts.append(f"⏱ {v['duration']}")
    vc = _parse_view_count(v.get("view_count"))
    if vc > 0:
        if vc >= 10000:
            meta_parts.append(f"🔥 {vc:,}회")
        else:
            meta_parts.append(f"👁 {vc:,}회")
    if v.get("published"):
        meta_parts.append(f"📅 {v['published'][:10]}")
    if meta_parts:
        st.caption(" | ".join(meta_parts))

    # Description
    if show_desc and v.get("description"):
        st.markdown(
            f"<small style='color:#888'>{v['description'][:150]}</small>",
            unsafe_allow_html=True,
        )


def render_youtube_section(query: str, limit: int = 12, per_page: int = 4,
                           sort: str = "views") -> list[dict]:
    """Shared helper: render video grid with page navigation + sort toggle.

    Args:
        query: search query
        limit: total videos to fetch
        per_page: videos per page
        sort: default sort — "views" (조회수순) or "latest" (최신순)
    """
    _tl = "d" if sort == "latest" else None
    videos = fetch_youtube_search(query, limit=limit, timelimit=_tl)
    if not videos:
        _show_empty_state("관련 영상을 찾지 못했습니다.")
        return []

    # Sort toggle checkbox
    sort_key = f"sort_toggle_{query[:20]}"
    if sort == "latest":
        use_views = st.checkbox("조회수 많은 순으로 보기", key=sort_key, value=False)
        active_sort = "views" if use_views else "latest"
    else:
        use_latest = st.checkbox("최신순으로 보기", key=sort_key, value=False)
        active_sort = "latest" if use_latest else "views"

    if active_sort == "latest":
        videos_sorted = sorted(videos, key=lambda v: v.get("published", ""), reverse=True)
    else:
        videos_sorted = sorted(videos, key=lambda v: _parse_view_count(v.get("view_count")), reverse=True)

    # Summary metrics
    total = len(videos_sorted)
    top_views = _parse_view_count(videos_sorted[0].get("view_count")) if videos_sorted else 0
    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("검색 영상", f"{total}건")
    if active_sort == "latest":
        newest = videos_sorted[0].get("published", "")[:10] if videos_sorted else "N/A"
        mc2.metric("최신 영상", newest)
    else:
        mc2.metric("최고 조회수", f"{top_views:,}회" if top_views else "N/A")
    channels = set(v.get("uploader", "") for v in videos_sorted if v.get("uploader"))
    mc3.metric("채널 수", f"{len(channels)}개")

    # Pagination (공통 헬퍼 사용)
    page_key = f"yt_page_{query[:20]}"
    _render_paginated_videos(videos_sorted, page_key, per_page)

    return videos_sorted


def render_expert_page(
    title: str,
    icon: str,
    default_query: str,
    tickers: dict | None = None,
    external_links: list | None = None,
    auto_news_query: str | None = None,
    sub_topics: list | None = None,
    youtube_sort: str = "views",
):
    """
    Render a standard expert page with search, statistics, reporting,
    and optional real-time monitoring widgets.

    Args:
        tickers: {symbol: display_name} for yfinance real-time metrics
        external_links: [(label, url), ...] for reference links
        youtube_sort: "views" (조회수순) or "latest" (최신순)
        auto_news_query: auto-load news on page open (no button needed)
        sub_topics: [(tab_icon, tab_name, search_query), ...] for categorized news tabs
    """
    st.title(f"{icon} {title} 전문가")

    # ── 페이지 설명 + 갱신 컨트롤 ─────────────────────────────────────────
    _desc_map = {
        "생활금융": "재테크·저축·금리·투자 트렌드를 실시간으로 확인하세요.",
        "건강": "헬스케어·의약품·운동·정신건강 최신 동향을 제공합니다.",
        "식생활": "외식·맛집·요리·식품 트렌드와 가격 동향을 분석합니다.",
        "부동산": "아파트·청약·전세·매매 시장 동향을 실시간 모니터링합니다.",
        "교육": "입시·에듀테크·교육 정책 최신 동향을 확인하세요.",
        "여행": "국내외 여행지·항공권·호텔 트렌드를 제공합니다.",
        "생활법률": "생활 속 법률·판례·규정 변경 사항을 확인하세요.",
        "쇼핑/소비": "온라인 쇼핑·소비 트렌드·할인 정보를 분석합니다.",
        "육아/보육": "육아·보육 정책·용품 트렌드를 확인하세요.",
        "문화/예술": "전시·공연·K-문화 최신 동향을 제공합니다.",
        "반려동물": "반려동물·사료·펫 헬스케어 트렌드를 분석합니다.",
        "화훼/식물": "플랜테리어·다육식물·화훼 트렌드를 확인하세요.",
        "환율유가": "달러·엔화·유가 실시간 동향을 모니터링합니다.",
        "관세/무역": "수출입·관세·무역 동향을 분석합니다.",
        "사업/창업": "스타트업·창업 지원·비즈니스 트렌드를 확인하세요.",
        "운송/물류": "물류·해운·항공 운송 동향을 분석합니다.",
        "해외 분쟁/전쟁": "글로벌 분쟁·안보 상황을 실시간 확인합니다.",
        "IT/테크": "AI·반도체·클라우드·IT 기술 최신 동향을 제공합니다.",
        "취업/채용": "채용·취업 시장·자격증·직업 전망을 분석합니다.",
    }
    desc = _desc_map.get(title, f"{title} 관련 최신 동향을 AI 전문가가 분석합니다.")
    st.caption(desc)

    col_r, col_t = st.columns([1, 3])
    with col_r:
        if st.button("🔄 데이터 갱신", type="primary", key=f"refresh_{title}"):
            from utils.data_fetcher import fetch_news_search, fetch_web_search, fetch_youtube_search
            fetch_news_search.clear()
            fetch_web_search.clear()
            fetch_youtube_search.clear()
            if tickers:
                from utils.data_fetcher import fetch_stock_data as _fsd
                _fsd.clear()
            st.rerun()
    with col_t:
        st.caption(f"마지막 갱신: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (자동 캐시 적용)")

    st.markdown("---")

    # ── 실시간 모니터링 (tickers) ─────────────────────────────────────────
    if tickers:
        from utils.data_fetcher import fetch_stock_data

        st.markdown(f"### 📊 {title} 실시간 지표")
        cols = st.columns(min(len(tickers), 4))
        ticker_items = list(tickers.items())
        for i, (symbol, name) in enumerate(ticker_items):
            with cols[i % len(cols)]:
                d = fetch_stock_data(symbol, period="5d")
                if d.get("ok"):
                    price_fmt = f"${d['price']:,.2f}" if not symbol.endswith((".KS", ".KQ")) else f"{d['price']:,.0f}"
                    delta = f"{d['change']:+,.2f} ({d['change_pct']:+.2f}%)"
                    st.metric(name, price_fmt, delta=delta)
                else:
                    st.metric(name, "N/A")

        # 첫 번째 ticker 차트
        first_sym = ticker_items[0][0]
        d = fetch_stock_data(first_sym, period="1mo")
        if d.get("ok") and d.get("history"):
            df_chart = pd.DataFrame(d["history"])
            st.line_chart(df_chart.set_index("Date")["Close"])
            prices = [r["Close"] for r in d["history"]]
            if prices:
                sc1, sc2, sc3 = st.columns(3)
                sc1.metric("최고", f"{max(prices):,.2f}")
                sc2.metric("최저", f"{min(prices):,.2f}")
                sc3.metric("평균", f"{sum(prices)/len(prices):,.2f}")
        st.markdown("---")

    # ── 카테고리별 뉴스 탭 (sub_topics) ──────────────────────────────────
    if sub_topics:
        st.markdown(f"### 📂 {title} 카테고리별 최신 동향")
        tab_labels = [f"{t[0]} {t[1]}" for t in sub_topics]
        tabs = st.tabs(tab_labels)
        for tab, (tab_icon, tab_name, tab_query) in zip(tabs, sub_topics):
            with tab:
                news = fetch_news_search(tab_query, limit=5)
                if news:
                    for n in news[:4]:
                        st.markdown(
                            f"- **[{n['title']}]({n['link']})**  \n"
                            f"  <small>{n.get('source', '')} | {n.get('published', '')}</small>",
                            unsafe_allow_html=True,
                        )
                    # 카테고리별 경향 분석
                    _render_news_trends(news, tab_name)
                else:
                    _show_empty_state(f"{tab_name} 관련 뉴스를 가져오지 못했습니다.")
        st.markdown("---")

    # ── 자동 뉴스 로딩 + 경향 분석 ──────────────────────────────────────
    if auto_news_query:
        st.markdown(f"### 📰 {title} 최신 뉴스")
        auto_news = fetch_news_search(auto_news_query, limit=8)
        if auto_news:
            for n in auto_news[:5]:
                st.markdown(
                    f"- **[{n['title']}]({n['link']})**  \n"
                    f"  <small>{n.get('source', '')} | {n.get('published', '')}</small>",
                    unsafe_allow_html=True,
                )
            # 뉴스 경향 분석
            _render_news_trends(auto_news, title)
        else:
            _show_empty_state(f"{title} 관련 뉴스를 가져오지 못했습니다.")
        st.markdown("---")

    # ── 전문가 검색 & 분석 ────────────────────────────────────────────────
    st.markdown(f"### 🔍 {title} 전문가 분석")
    query = st.text_input(f"🔍 {title} 관련 검색어 입력", value=default_query)

    col1, col2 = st.columns([2, 1])

    with col1:
        analyze_btn = st.button("데이터 분석 및 리포트 갱신", type="primary", use_container_width=True)

    state_key = f"expert_data_{title}"

    if analyze_btn:
        with st.spinner("최신 트렌드 및 뉴스 수집 중..."):
            web_results = fetch_web_search(query, limit=5)
            news_results = fetch_news_search(query, limit=8)
            _yt_tl = "d" if youtube_sort == "latest" else None
            youtube_results = fetch_youtube_search(query, limit=12, timelimit=_yt_tl)

            from utils.data_fetcher import fetch_stock_data as _fsd

            # Determine best ticker for real trend data
            _proxy_map = {
                "주식": "^KS11", "코스피": "^KS11", "코스닥": "^KQ11",
                "환율": "KRW=X", "관세": "^KS11", "무역": "^KS11",
                "금융": "^KS11", "부동산": "^KS11", "유가": "CL=F",
                "운송": "BZ=F", "사업": "^KS11",
            }

            target_sym = None
            if tickers:
                target_sym = list(tickers.keys())[0]
            else:
                for kw, sym in _proxy_map.items():
                    if kw in title or kw in query:
                        target_sym = sym
                        break
                if not target_sym:
                    target_sym = "^KS11"  # Default: KOSPI

            td = _fsd(target_sym, period="7d")
            if td.get("ok") and td.get("history"):
                hist = td["history"][-7:]
                dates = [r.get("Date", "") for r in hist]
                values = [r["Close"] for r in hist]
            else:
                # Fallback: use 5d data
                td2 = _fsd("^KS11", period="5d")
                if td2.get("ok") and td2.get("history"):
                    hist = td2["history"]
                    dates = [r.get("Date", "") for r in hist]
                    values = [r["Close"] for r in hist]
                else:
                    dates = pd.date_range(end=datetime.datetime.today(), periods=7).strftime('%m-%d').tolist()
                    values = [0] * len(dates)

            df = pd.DataFrame({"Date": dates, "Trend": values})

            st.session_state[state_key] = {
                "query": query,
                "web": web_results,
                "news": news_results,
                "youtube": youtube_results,
                "df": df,
                "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

    data = st.session_state.get(state_key)

    if data:
        st.success(f"최근 분석 완료: {data['updated_at']}")

        st.markdown(f"### 📈 최근 7일 '{data['query']}' 관심도 트렌드")
        chart_data = data["df"].set_index("Date")
        st.bar_chart(chart_data)

        st.markdown("### 📰 핵심 관련 뉴스")
        if data["news"]:
            for n in data["news"][:5]:
                st.markdown(
                    f"- **[{n['title']}]({n['link']})**  \n"
                    f"  <small>{n.get('source', '')} | {n.get('published', '')}</small>",
                    unsafe_allow_html=True,
                )
            # 검색 결과 경향 분석
            _render_news_trends(data["news"], data["query"])
        else:
            _show_empty_state("관련 뉴스를 찾지 못했습니다.")

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
            _show_empty_state("관련 웹 검색 결과를 찾지 못했습니다.")

        st.markdown("---")
        st.markdown(f"### 🎬 관련 영상")
        if data.get("youtube"):
            if youtube_sort == "latest":
                videos = sorted(data["youtube"], key=lambda v: v.get("published", ""), reverse=True)
            else:
                videos = sorted(data["youtube"], key=lambda v: _parse_view_count(v.get("view_count")), reverse=True)
            _render_paginated_videos(videos, f"yt_ep_{title}")
        else:
            _show_empty_state("관련 영상을 찾지 못했습니다.")

        st.markdown("---")

        trend_records = []
        if isinstance(data.get("df"), pd.DataFrame) and not data["df"].empty:
            trend_records = data["df"].to_dict('records')

        data_context = {
            "query": data["query"],
            "news": data["news"],
            "web": data["web"],
            "youtube": data.get("youtube", []),
            "df": trend_records
        }

        render_download_buttons(context=data_context)
    else:
        st.info("상단 버튼을 눌러 데이터를 수집하고 인사이트를 확인하세요.")

    # ── 관련 YouTube 영상 (항상 표시) ─────────────────────────────────────
    st.markdown("---")
    _sort_label = "최신" if youtube_sort == "latest" else "인기"
    st.markdown(f"## 🎬 {title} 관련 {_sort_label} 영상")
    render_youtube_section(f"{title} {default_query.split()[0]} 분석 동향", sort=youtube_sort)

    # ── 외부 참고 링크 ────────────────────────────────────────────────────
    if external_links:
        st.markdown("---")
        st.markdown(f"### 🔗 {title} 외부 모니터링")
        cols = st.columns(min(len(external_links), 3))
        for i, (label, url) in enumerate(external_links):
            with cols[i % len(cols)]:
                st.link_button(label, url, use_container_width=True)
