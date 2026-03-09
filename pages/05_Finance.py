# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="생활금융",
    icon="💰",
    default_query="재테크 저축 금리 생활금융 동향",
    tickers={
        "GC=F": "금(Gold)",
        "^TNX": "미국10년국채",
        "BTC-USD": "비트코인",
        "ETH-USD": "이더리움",
    },
    auto_news_query="금리 재테크 저축 생활금융",
    external_links=[
        ("📊 한국은행 기준금리", "https://www.bok.or.kr/portal/singl/baseRate/list.do?dataSeCd=01&menuNo=200643"),
        ("💰 네이버 금융", "https://finance.naver.com/"),
        ("📈 인베스팅 금 시세", "https://kr.investing.com/commodities/gold"),
    ],
)
