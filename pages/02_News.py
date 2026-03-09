# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.data_fetcher import fetch_news, NEWS_FEEDS
from utils.report_downloader import render_download_buttons

apply_custom_css()

st.title("📰 뉴스")
st.markdown("---")

# ── Category tabs ────────────────────────────────────────────────────────
categories = list(NEWS_FEEDS.keys())
tabs = st.tabs(categories)

for tab, cat in zip(tabs, categories):
    with tab:
        limit = st.slider(f"표시 개수", 5, 30, 15, key=f"news_limit_{cat}")
        news = fetch_news(cat, limit=limit)

        if not news:
            st.info(f"{cat} 뉴스를 불러올 수 없습니다.")
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

# ── 보고서 다운로드 ────────────────────────────────────────────────────────
st.markdown("---")
# 모든 탭의 뉴스를 수집하여 다운로드 컨텍스트 생성
all_news_items = []
for cat in categories:
    cat_news = fetch_news(cat, limit=10)
    if cat_news:
        all_news_items.extend(cat_news[:5])

news_context = {
    "query": "종합 뉴스 리포트",
    "news": all_news_items,
    "web": [],
    "df": [{"카테고리": cat, "기사수": len(fetch_news(cat, limit=10) or [])} for cat in categories],
}
render_download_buttons(context=news_context)
