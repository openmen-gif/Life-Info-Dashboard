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

# ── 전문가별 기본 쿼리 & session_state 키 매핑 ────────────────────────
EXPERT_DEFAULTS = [
    {"name": "생활금융", "state_key": "expert_data_생활금융", "default_query": "재테크 저축 금리 생활금융 동향"},
    {"name": "건강", "state_key": "expert_data_건강", "default_query": "최신 헬스케어 메디컬 건강관리 동향"},
    {"name": "식생활", "state_key": "expert_data_식생활", "default_query": "글로벌 외식 국내 맛집 요리 트렌드"},
    {"name": "부동산", "state_key": "expert_data_부동산", "default_query": "국내 아파트 청약 전세 매매 부동산 동향"},
    {"name": "교육", "state_key": "expert_data_교육", "default_query": "글로벌 에듀테크 국내 입시 교육 트렌드"},
    {"name": "여행", "state_key": "expert_data_여행", "default_query": "국내 명소 여행지 호캉스 해외 관광 항공권 추천"},
    {"name": "생활법률", "state_key": "expert_data_생활법률", "default_query": "최신 생활 법률 대법원 판례 동향"},
    {"name": "주식 분석", "state_key": "expert_data_주식 분석", "default_query": "국내 코스피 코스닥 미국 증시 주식 시황 분석"},
    {"name": "쇼핑/소비", "state_key": "expert_data_쇼핑/소비", "default_query": "글로벌 국내 온라인 쇼핑 소비 트렌드"},
    {"name": "육아/보육", "state_key": "expert_data_육아/보육", "default_query": "저출산 육아용품 글로벌 보육 정책 동향"},
    {"name": "문화/예술", "state_key": "expert_data_문화/예술", "default_query": "전시 공연 글로벌 K-문화 예술 동향"},
    {"name": "반려동물", "state_key": "expert_data_반려동물", "default_query": "반려동물 사료 펫 헬스케어 트렌드"},
    {"name": "화훼/식물", "state_key": "expert_data_화훼/식물", "default_query": "플랜테리어 다육식물 화훼 트렌드"},
    {"name": "환율 분석", "state_key": "expert_data_환율유가", "default_query": "달러 엔화 글로벌 환율 경제 동향"},
    {"name": "관세/무역", "state_key": "expert_data_관세/무역", "default_query": "한국 수출입 무역 글로벌 관세 동향"},
    {"name": "사업/창업", "state_key": "expert_data_사업/창업", "default_query": "스타트업 창업 지원 비즈니스 매크로 동향"},
    {"name": "운송/물류", "state_key": "expert_data_운송/물류", "default_query": "국내외 물류 해운 항공 운송 트렌드"},
    {"name": "해외 분쟁/전쟁", "state_key": "expert_data_해외 분쟁/전쟁", "default_query": "우크라이나 중동 글로벌 분쟁 전쟁 동향"},
    {"name": "IT/테크", "state_key": "expert_data_IT/테크", "default_query": "AI 반도체 스마트폰 IT 기술 트렌드"},
    {"name": "취업/채용", "state_key": "expert_data_취업/채용", "default_query": "채용 트렌드 취업 시장 자격증 직업 전망"},
    {"name": "유가(국제)", "state_key": None, "default_query": "WTI 브렌트 두바이유 국제 유가 동향"},
    {"name": "환율(실시간)", "state_key": None, "default_query": "달러 원화 엔화 위안화 환율 실시간 동향"},
]

# 이전 페이지에서 검색한 쿼리 사용 현황 표시
st.markdown("#### 📋 각 페이지 검색 현황")
used_queries = []
for exp in EXPERT_DEFAULTS:
    prev = st.session_state.get(exp["state_key"]) if exp["state_key"] else None
    if prev and prev.get("query"):
        used_queries.append(f"✅ **{exp['name']}**: `{prev['query']}`")
    else:
        used_queries.append(f"⬜ **{exp['name']}**: _{exp['default_query']}_ (기본값)")

with st.expander("검색어 상세 보기", expanded=False):
    for q in used_queries:
        st.markdown(q, unsafe_allow_html=True)

st.caption(f"✅ 사용자 검색어 {sum(1 for e in EXPERT_DEFAULTS if st.session_state.get(e['state_key']))}개 / ⬜ 기본값 {sum(1 for e in EXPERT_DEFAULTS if not st.session_state.get(e['state_key']))}개")

def _collect_single_expert(expert: dict, session_data: dict | None) -> dict:
    """단일 전문가 데이터 수집 (병렬 실행용)."""
    if session_data and session_data.get("query"):
        query = session_data["query"]
        news_res = session_data.get("news") or fetch_news_search(query, limit=5)
        web_res = session_data.get("web") or fetch_web_search(query, limit=5)
        if session_data.get("df") is not None:
            df_data = session_data["df"]
            df_records = df_data.to_dict("records") if isinstance(df_data, pd.DataFrame) else df_data
        else:
            dates = pd.date_range(end=datetime.datetime.today(), periods=7).strftime('%m-%d').tolist()
            base_val = hash(query) % 50 + 20
            df_records = [{"Date": d, "Trend": base_val + (hash(query + d) % 30)} for d in dates]
    else:
        query = expert["default_query"]
        web_res = fetch_web_search(query, limit=5)
        news_res = fetch_news_search(query, limit=5)
        dates = pd.date_range(end=datetime.datetime.today(), periods=7).strftime('%m-%d').tolist()
        if "주식" in expert["name"] or "코스피" in query:
            values = [6020, 6080, 5010, 4950, 5100, 5150, 5200]
        elif "환율" in expert["name"]:
            values = [1350, 1345, 1420, 1450, 1435, 1440, 1445]
        elif "관세" in expert["name"] or "무역" in expert["name"]:
            values = [100, 95, 80, 75, 78, 70, 68]
        else:
            base_val = hash(query) % 50 + 20
            values = [base_val + (hash(query + d) % 30) for d in dates]
        df_records = [{"Date": d, "Trend": v} for d, v in zip(dates, values)]

    return {"expert": expert["name"], "query": query, "news": news_res, "web": web_res, "df": df_records}


if st.button("전 분야 마스터 리포트 생성 시작", type="primary", use_container_width=True):
    st.session_state.pop("master_report_data", None)  # 이전 결과 초기화
    from concurrent.futures import ThreadPoolExecutor, as_completed

    progress_bar = st.progress(0)
    status_text = st.empty()
    status_text.text("전 분야 병렬 수집 시작...")

    # 세션 데이터를 미리 추출 (스레드 안전)
    expert_sessions = []
    for exp in EXPERT_DEFAULTS:
        prev = st.session_state.get(exp["state_key"]) if exp["state_key"] else None
        expert_sessions.append((exp, prev))

    master_context_list = [None] * len(EXPERT_DEFAULTS)

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(_collect_single_expert, exp, sess): i
            for i, (exp, sess) in enumerate(expert_sessions)
        }
        done_count = 0
        for future in as_completed(futures):
            idx = futures[future]
            master_context_list[idx] = future.result()
            done_count += 1
            status_text.text(f"수집 완료: [{EXPERT_DEFAULTS[idx]['name']}] ({done_count}/{len(EXPERT_DEFAULTS)})")
            progress_bar.progress(done_count / len(EXPERT_DEFAULTS))

    st.session_state["master_report_data"] = master_context_list

if "master_report_data" in st.session_state:
    st.success("✅ 전 분야 데이터 수집 완료! 아래에서 마스터 리포트를 다운로드하세요.")
    
    # Render Master report dl
    st.markdown("### 📥 마스터 리포트 다운로드")
    render_download_buttons(context=st.session_state["master_report_data"])
