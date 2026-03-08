# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.data_fetcher import fetch_news, NEWS_FEEDS

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
