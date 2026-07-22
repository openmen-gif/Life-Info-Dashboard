# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
from utils.charts import render_trend_with_stats
from utils.config import HAS_MOLIT
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page
from utils.realestate_fetcher import LAWD_CODES, fetch_apt_trade_history, list_apt_names

apply_custom_css()


def _fmt_manwon(v: float) -> str:
    """만원 단위 숫자 -> '16억 6,000만원' 형식(1억 미만은 '9,500만원'만).

    공용 차트 컴포넌트의 '만원 166,000'식 접두 표기는 한국어로 어색하고 길어
    카드에서 잘리므로, 실거래가 특화 축약 표기를 따로 쓴다."""
    v = int(round(v))
    sign = "-" if v < 0 else ""
    v = abs(v)
    eok, man = divmod(v, 10000)
    if eok:
        return f"{sign}{eok}억" + (f" {man:,}만원" if man else "")
    return f"{sign}{v:,}만원"


def _render_price_lookup():
    """아파트 단지 실거래 시세 조회 + 기간별 가격 추세."""
    st.markdown("## 🔍 아파트 시세 조회")
    st.caption("국토교통부 실거래가 자료 기반 — 최근 거래 내역과 기간별 가격 추세를 확인하세요.")

    if not HAS_MOLIT:
        st.info(
            "국토교통부 실거래가 API 키가 설정되지 않았습니다. "
            "`.env`에 `MOLIT_API_KEY`를 추가하면 이 섹션이 활성화됩니다."
        )
        return

    col_sido, col_sigungu = st.columns(2)
    with col_sido:
        sido = st.selectbox("시/도", list(LAWD_CODES.keys()), key="re_sido")
    with col_sigungu:
        sigungu = st.selectbox("시/군/구", list(LAWD_CODES[sido].keys()), key="re_sigungu")

    lawd_cd = LAWD_CODES[sido][sigungu]
    # 단지명 목록은 검색 기간(조회 기간)과 별개로 넉넉히 3년치로 채운다 — "현대(고덕)"처럼
    # 사용자가 정확한 등록명을 몰라 자유 입력으로는 못 찾던 문제를 원천 차단(직접 입력 대신 실재 단지만 선택).
    with st.spinner(f"{sido} {sigungu} 단지 목록 불러오는 중..."):
        apt_options = list_apt_names(lawd_cd, months=36)

    if not apt_options:
        st.info("이 지역은 최근 3년간 조회된 거래가 없어 단지 목록을 표시할 수 없습니다.")
        return

    apt_name = st.selectbox(
        "아파트 단지명", apt_options, index=None,
        placeholder="단지명을 입력해 검색하세요 (예: 래미안)", key="re_apt_name",
    )

    period_labels = ["1년", "3년", "5년"]
    period_months = [12, 36, 60]
    period_idx = st.selectbox(
        "조회 기간", range(len(period_labels)),
        format_func=lambda i: period_labels[i], index=0, key="re_period",
    )

    if st.button("🔍 시세 조회", type="primary", key="re_search_btn"):
        if not apt_name:
            st.warning("아파트 단지명을 선택해주세요.")
        else:
            months = period_months[period_idx]
            with st.spinner(f"{sido} {sigungu} '{apt_name}' 실거래 내역 조회 중... (최대 {period_labels[period_idx]}치)"):
                records = fetch_apt_trade_history(lawd_cd, apt_name, months=months)
            st.session_state["re_result"] = {
                "records": records, "apt_name": apt_name, "sido": sido, "sigungu": sigungu,
                "period_label": period_labels[period_idx],
            }

    result = st.session_state.get("re_result")
    if not result:
        return
    period_idx = period_labels.index(result["period_label"])

    records = result["records"]
    if not records:
        st.warning(
            f"'{result['apt_name']}' 단지는 최근 {result['period_label']} 동안 거래 내역이 없습니다. "
            "조회 기간을 늘려서 다시 시도해보세요."
        )
        return

    st.success(f"{result['sido']} {result['sigungu']} '{result['apt_name']}' 거래 {len(records)}건 조회됨")

    df = pd.DataFrame(records)
    show_df = df[["계약일", "전용면적", "층", "거래금액_만원", "건축년도"]].copy()
    show_df.columns = ["계약일", "전용면적(㎡)", "층", "거래금액(만원)", "건축년도"]
    show_df = show_df.sort_values("계약일", ascending=False)
    st.dataframe(show_df, use_container_width=True, hide_index=True)

    st.markdown(f"#### 📈 '{result['apt_name']}' 가격 추세 ({period_labels[period_idx]})")
    trend = (
        df.groupby("계약일", as_index=False)["거래금액_만원"].mean()
        .rename(columns={"계약일": "Date", "거래금액_만원": "Close"})
    )
    render_trend_with_stats(trend.to_dict("records"), decimals=0, show_stats=False)

    prices = trend["Close"].tolist()
    change = prices[-1] - prices[0]
    pct = (change / prices[0] * 100) if prices[0] else 0
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("현재", _fmt_manwon(prices[-1]))
    c2.metric("최고", _fmt_manwon(max(prices)))
    c3.metric("최저", _fmt_manwon(min(prices)))
    c4.metric("평균", _fmt_manwon(sum(prices) / len(prices)))
    c5.metric("기간 등락", f"{'+' if change >= 0 else ''}{_fmt_manwon(change)} ({pct:+.1f}%)")

    st.divider()


_render_price_lookup()

render_expert_page(
    title="부동산",
    icon="🏠",
    default_query="국내 아파트 청약 전세 매매 부동산 동향",
    youtube_sort="latest",
    tickers={
        "VNQ": "미국REITs",
        "IYR": "부동산ETF",
        "XLRE": "부동산섹터",
    },
    sub_topics=[
        ("🏢", "아파트/매매", "아파트 매매 시세 실거래가 분양"),
        ("🏠", "전세/월세", "전세 월세 보증금 역전세 임대차"),
        ("📋", "청약/분양", "아파트 청약 분양 당첨 조건 일정"),
        ("📊", "시장전망", "부동산 시장 전망 가격 하락 상승 예측"),
        ("🏗️", "재건축/재개발", "재건축 재개발 정비사업 규제 투자"),
    ],
    auto_news_query="아파트 매매 전세 청약 부동산 시장",
    external_links=[
        ("🏠 국토부 실거래가", "https://rt.molit.go.kr/"),
        ("📊 한국부동산원", "https://www.reb.or.kr/"),
        ("🏢 네이버 부동산", "https://land.naver.com/"),
        ("📋 청약홈", "https://www.applyhome.co.kr/"),
    ],
)
