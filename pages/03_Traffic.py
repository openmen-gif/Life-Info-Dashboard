# -*- coding: utf-8 -*-
"""교통 정보 — 카테고리별 교통 뉴스 + 경향 분석 + 외부 모니터링"""
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(
    title="교통",
    icon="🚗",
    default_query="고속도로 교통 정체 도로 상황 실시간",
    sub_topics=[
        ("🛣️", "고속도로", "고속도로 정체 교통량 통행료 휴게소"),
        ("🚇", "대중교통", "지하철 버스 노선 파업 운행 대중교통"),
        ("🚗", "도심교통", "서울 수도권 출퇴근 교통 혼잡 우회"),
        ("✈️", "항공/철도", "KTX SRT 항공편 지연 결항 철도"),
        ("🔧", "도로공사", "도로공사 통제 우회도로 개통 확장"),
    ],
    auto_news_query="고속도로 교통 정체 실시간 도로 상황",
    external_links=[
        ("🚗 ITS 교통정보", "https://www.its.go.kr/"),
        ("🛣️ 한국도로공사", "https://www.ex.co.kr/"),
        ("🗺️ 네이버 지도", "https://map.naver.com/"),
        ("🗺️ 카카오맵", "https://map.kakao.com/"),
        ("🚌 서울TOPIS", "https://topis.seoul.go.kr/"),
        ("📊 고속도로 교통량", "https://data.ex.co.kr/"),
    ],
)
