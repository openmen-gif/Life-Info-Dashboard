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
    sub_topics=[
        ("💳", "카드/결제", "신용카드 혜택 간편결제 핀테크 페이"),
        ("🏦", "예금/적금/금리", "예금 적금 금리 이자 은행 저축"),
        ("📈", "투자/재테크", "재테크 투자 주식 펀드 ETF 초보"),
        ("🏠", "대출/보험", "주택대출 신용대출 보험 가입 비교"),
        ("💰", "암호화폐", "비트코인 이더리움 암호화폐 코인 시세"),
    ],
    auto_news_query="금리 재테크 저축 생활금융",
    external_links=[
        ("📊 한국은행 기준금리", "https://www.bok.or.kr/portal/singl/baseRate/list.do?dataSeCd=01&menuNo=200643"),
        ("💰 네이버 금융", "https://finance.naver.com/"),
        ("📈 인베스팅 금 시세", "https://kr.investing.com/commodities/gold"),
    ],
)
