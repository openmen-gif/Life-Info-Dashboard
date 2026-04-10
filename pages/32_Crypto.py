# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="암호화폐",
    icon="🪙",
    default_query="비트코인 이더리움 암호화폐 가상자산 시세 동향",
    tickers={
        "BTC-USD": "Bitcoin",
        "ETH-USD": "Ethereum",
        "SOL-USD": "Solana",
        "XRP-USD": "Ripple",
    },
    auto_news_query="비트코인 이더리움 암호화폐 가상자산 코인 시세",
    sub_topics=[
        ("🪙", "비트코인/이더리움", "비트코인 이더리움 시세 전망 분석"),
        ("📊", "알트코인/밈코인", "알트코인 밈코인 솔라나 리플 도지코인"),
        ("📋", "규제/정책", "가상자산 규제 과세 거래소 금융당국"),
        ("🔗", "블록체인/Web3", "블록체인 Web3 NFT DeFi 기술 동향"),
        ("💱", "거래소/투자", "업비트 빗썸 바이낸스 거래소 투자 전략"),
    ],
    external_links=[
        ("📊 업비트", "https://upbit.com/exchange"),
        ("🪙 코인마켓캡", "https://coinmarketcap.com/"),
        ("📈 코인게코", "https://www.coingecko.com/"),
    ],
)
