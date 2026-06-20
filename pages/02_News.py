# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.data_fetcher import fetch_news, NEWS_FEEDS
from utils.report_downloader import render_download_buttons

apply_custom_css()

st.title("📰 뉴스")
st.markdown("---")

# ── Category tabs (지연 로드: 첫 탭만 자동, 나머지는 버튼) ──────────────────
# st.tabs 는 모든 탭 본문을 콜드 로드에서 실행하므로, 전 카테고리를 한꺼번에 fetch 하면
# HF 클라우드 IP 의 RSS 요청이 버스트로 몰려 레이트리밋된다. 요청을 사용자 상호작용에
# 분산시켜 첫 탭만 자동 로드하고 나머지는 클릭 시 로드한다.
categories = list(NEWS_FEEDS.keys())
st.caption("첫 카테고리는 자동, 나머지는 '뉴스 불러오기'로 로드됩니다 (클라우드 속도 최적화).")
tabs = st.tabs(categories)
_news_cache = {}  # 다운로드 컨텍스트 재활용(중복 fetch 방지)

for _ti, (tab, cat) in enumerate(zip(tabs, categories)):
    with tab:
        limit = st.slider("표시 개수", 5, 30, 15, key=f"news_limit_{cat}")
        _lazy = f"_news_load_{cat}"
        _do = (_ti == 0) or st.session_state.get(_lazy)
        if not _do:
            if st.button(f"📰 {cat} 뉴스 불러오기", key=f"btn_{_lazy}", use_container_width=True):
                st.session_state[_lazy] = True
                _do = True
        if not _do:
            st.caption("👆 위 버튼을 눌러 이 카테고리 뉴스를 불러오세요.")
            continue

        with st.spinner(f"{cat} 뉴스 로드 중..."):
            news = fetch_news(cat, limit=limit)
        _news_cache[cat] = news

        if not news:
            st.warning(
                f"⚠️ **{cat} 뉴스를 불러오지 못했습니다.** "
                "클라우드(HF) IP 레이트리밋일 수 있어요 — 잠시 후 새로고침하면 보통 복구됩니다."
            )
            continue

        for i, item in enumerate(news):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"**{i+1}.** [{item['title']}]({item['link']})")
                meta = []
                if item.get("source"):
                    meta.append(item["source"])
                if item.get("published"):
                    meta.append(item["published"])
                if meta:
                    st.caption(" | ".join(meta))
            with col2:
                st.link_button("읽기", item["link"], use_container_width=True)

# ── 관련 영상 (지연 로드) ─────────────────────────────────────────────────
st.markdown("---")
import datetime as _dt
_today_n = _dt.datetime.now().strftime("%Y년 %m월 %d일")
st.markdown(f"## 🎬 {_today_n} 최신 뉴스 영상")
_yt_news = []
if st.session_state.get("_news_yt") or st.button("🎬 뉴스 영상 불러오기", use_container_width=True):
    st.session_state["_news_yt"] = True
    from utils.expert_template import render_youtube_section
    _yt_news = render_youtube_section("오늘 뉴스 시사 이슈 분석 속보", sort="latest")

# ── 보고서 다운로드 (지연 로드) ────────────────────────────────────────────
st.markdown("---")
if st.session_state.get("_news_dl") or st.button("📥 통합 뉴스 보고서 생성/다운로드", use_container_width=True):
    st.session_state["_news_dl"] = True
    # 탭에서 이미 받아둔 뉴스를 재활용, 없으면 보충 fetch
    all_news_items = []
    cat_counts = []
    for cat in categories:
        cat_news = _news_cache.get(cat)
        if cat_news is None:
            cat_news = fetch_news(cat, limit=10)
        cat_counts.append({"카테고리": cat, "기사수": len(cat_news or [])})
        if cat_news:
            all_news_items.extend(cat_news[:5])
    news_context = {
        "query": "종합 뉴스 리포트",
        "news": all_news_items,
        "web": [],
        "youtube": _yt_news,
        "df": cat_counts,
    }
    render_download_buttons(context=news_context)
