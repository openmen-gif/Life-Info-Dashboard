# -*- coding: utf-8 -*-
import streamlit as st
import datetime
import json
import os
from utils.css_loader import apply_custom_css
from utils.data_fetcher import fetch_weather, fetch_news, fetch_traffic_status, fetch_web_search, fetch_news_search
from utils.report_downloader import render_download_buttons
import pandas as pd

apply_custom_css()

st.title("📊 데이터 수집기")
st.markdown("---")

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "collected_data"))
os.makedirs(DATA_DIR, exist_ok=True)

st.markdown("### 수집 대상 선택")
col1, col2 = st.columns(2)

with col1:
    collect_weather = st.checkbox("🌤️ 날씨 데이터", value=True)
    collect_news = st.checkbox("📰 뉴스 데이터", value=True)
    collect_traffic = st.checkbox("🚗 교통 데이터", value=True)

with col2:
    weather_city = st.text_input("날씨 도시(한글/영문)", value="서울")
    news_category = st.selectbox("뉴스 카테고리", ["종합", "IT/과학", "경제", "생활"])

st.markdown("---")

if st.button("📥 데이터 수집 실행", type="primary", use_container_width=True):
    collected = {}
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    with st.spinner("데이터 수집 중..."):
        if collect_weather:
            collected["weather"] = fetch_weather(city=weather_city)
            st.success(f"✅ 날씨 데이터 수집 완료 — {weather_city}")

        if collect_news:
            collected["news"] = fetch_news(category=news_category, limit=20)
            st.success(f"✅ 뉴스 데이터 수집 완료 — {news_category} ({len(collected['news'])}건)")

        if collect_traffic:
            collected["traffic"] = fetch_traffic_status()
            st.success(f"✅ 교통 데이터 수집 완료 — {len(collected['traffic'])}개 노선")

    # Save
    collected["_meta"] = {
        "timestamp": timestamp,
        "collected_at": datetime.datetime.now().isoformat(),
    }
    out_path = os.path.join(DATA_DIR, f"life_data_{timestamp}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(collected, f, ensure_ascii=False, indent=2)

    st.session_state["saved_general_data"] = collected
    st.session_state["saved_general_path"] = out_path
    st.session_state["saved_general_time"] = timestamp

if "saved_general_data" in st.session_state:
    st.success(f"💾 저장 완료: `{st.session_state['saved_general_path']}`")

    st.download_button(
        label="📥 JSON 다운로드",
        data=json.dumps(st.session_state["saved_general_data"], ensure_ascii=False, indent=2),
        file_name=f"life_data_{st.session_state['saved_general_time']}.json",
        mime="application/json",
    )
    
    # Render common report download buttons
    st.markdown("---")
    render_download_buttons()

# ── Collected data history ───────────────────────────────────────────────
st.markdown("---")
st.markdown("### 수집 이력")
if os.path.exists(DATA_DIR):
    files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith(".json")], reverse=True)
    if files:
        for f in files[:10]:
            st.text(f"📄 {f}")
    else:
        st.info("아직 수집된 데이터가 없습니다.")

st.markdown("---")
st.markdown("## 👑 전 분야 파노라마 분석 (마스터 리포트)")
st.info("16개 모든 생활정보 전문가의 최신 데이터를 한 번에 수집하여 방대한 목차가 포함된 단일 마스터 리포트를 생성합니다.")

if st.button("전 분야 마스터 리포트 생성 시작", type="primary", use_container_width=True):
    experts = [
        {"name": "생활금융", "query": "재테크 저축 금리 생활금융 동향"},
        {"name": "건강", "query": "최신 헬스케어 메디컬 건강관리 동향"},
        {"name": "식생활", "query": "글로벌 외식 국내 맛집 요리 트렌드"},
        {"name": "부동산(국내)", "query": "국내 아파트 청약 전세 매매 부동산 동향"},
        {"name": "부동산(해외)", "query": "해외 상업용 부동산 리츠 투자 동향"},
        {"name": "교육", "query": "글로벌 에듀테크 국내 입시 교육 트렌드"},
        {"name": "여행(국내)", "query": "국내 명소 여행지 호캉스 추천"},
        {"name": "여행(해외)", "query": "해외 여행 관광지 항공권 트렌드"},
        {"name": "생활법률", "query": "최신 생활 법률 대법원 판례 동향"},
        {"name": "주식(국내)", "query": "국내 코스피 코스닥 주식 시황 분석"},
        {"name": "주식(미국/해외)", "query": "미국 증시 S&P 나스닥 해외 주식 분석"},
        {"name": "쇼핑/소비", "query": "글로벌 국내 온라인 쇼핑 소비 트렌드"},
        {"name": "육아/보육", "query": "저출산 육아용품 글로벌 보육 정책 동향"},
        {"name": "문화/예술", "query": "전시 공연 글로벌 K-문화 예술 동향"},
        {"name": "반려동물", "query": "반려동물 사료 펫 헬스케어 트렌드"},
        {"name": "화훼/식물", "query": "플랜테리어 다육식물 화훼 트렌드"},
        {"name": "환율 분석", "query": "달러 엔화 글로벌 환율 경제 동향"},
        {"name": "관세/무역", "query": "한국 수출입 무역 글로벌 관세 동향"},
        {"name": "사업/창업", "query": "스타트업 창업 지원 비즈니스 매크로 동향"},
        {"name": "운송/물류", "query": "국내외 물류 해운 항공 운송 트렌드"},
        {"name": "해외 분쟁/전쟁", "query": "우크라이나 중동 글로벌 분쟁 전쟁 동향"},
        {"name": "유가(국제)", "query": "WTI 브렌트 두바이유 국제 유가 동향"},
        {"name": "환율(실시간)", "query": "달러 원화 엔화 위안화 환율 실시간 동향"}
    ]
    
    master_context_list = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, expert in enumerate(experts):
        status_text.text(f"수집 중: [{expert['name']}] 전문가 데이터 로딩... ({i+1}/{len(experts)})")
        
        web_res = fetch_web_search(expert["query"], limit=5)
        news_res = fetch_news_search(expert["query"], limit=5)
        
        # Scenario matrix for master report trend arrays
        dates = pd.date_range(end=datetime.datetime.today(), periods=7).strftime('%m-%d').tolist()
        
        if "주식" in expert["name"] or "코스피" in expert["query"]:
            values = [6020, 6080, 5010, 4950, 5100, 5150, 5200]
        elif "환율" in expert["name"]:
            values = [1350, 1345, 1420, 1450, 1435, 1440, 1445]
        elif "관세" in expert["name"] or "무역" in expert["name"]:
            values = [100, 95, 80, 75, 78, 70, 68]
        else:
            base_val = hash(expert["query"]) % 50 + 20
            values = [base_val + (hash(expert["query"] + d) % 30) for d in dates]
            
        df_records = [{"Date": d, "Trend": v} for d, v in zip(dates, values)]
        
        ctx = {
            "expert": expert["name"],
            "query": expert["query"],
            "news": news_res,
            "web": web_res,
            "df": df_records
        }
        master_context_list.append(ctx)
        progress_bar.progress((i + 1) / len(experts))
        
    st.session_state["master_report_data"] = master_context_list

if "master_report_data" in st.session_state:
    st.success("✅ 전 분야 데이터 수집 완료! 아래에서 마스터 리포트를 다운로드하세요.")
    
    # Render Master report dl
    st.markdown("### 📥 마스터 리포트 다운로드")
    render_download_buttons(context=st.session_state["master_report_data"])
