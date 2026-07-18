# -*- coding: utf-8 -*-
import streamlit as st
import datetime
from utils.css_loader import apply_custom_css
from utils.charts import render_temp_hourly
from utils.data_fetcher import fetch_weather, fetch_news, fetch_traffic_status, fetch_stock_data, fetch_stock_data_long, fetch_weather_series
from utils.ui_components import render_weather_card, render_news_summary, render_traffic_summary
from utils.report_downloader import render_download_buttons

apply_custom_css()


def _mark_tile():
    """글래스 타일 opt-in 마커 — css_loader의 :has(.tile-marker) 규칙이 참조."""
    st.markdown('<span class="tile-marker"></span>', unsafe_allow_html=True)


st.title("생활정보 대시보드")
st.caption(f"{datetime.datetime.now().strftime('%Y년 %m월 %d일 %A')}")

# ── 벤토 1행: 날씨(좌) + 주요 뉴스(우) — 타일 크기가 곧 정보 위계 ──────
col1, col2 = st.columns([1, 1.4], gap="small")

with col1:
    with st.container(border=True):
        weather = fetch_weather()
        render_weather_card(weather)
        # 24시간 기온 미니 차트 — 실선=관측, 점선=예보
        _ws = fetch_weather_series("Seoul")
        if _ws and _ws.get("ok"):
            render_temp_hourly(_ws["hourly"], _ws["now"], compact=True)
        _mark_tile()

with col2:
    with st.container(border=True):
        news = fetch_news("종합", limit=5)
        render_news_summary(news, limit=5)
        _mark_tile()

# ── 벤토 2행: 환율·유가 미니 타일(경향 그래프 포함) + 실시간 교통(와이드) ──
_ACCENT = "#7C9CFF"  # css_loader :root --accent와 동일 값 유지 (plotly는 CSS 변수 접근 불가)


def _render_trend_tile(label: str, value: str, delta: str, hist: list):
    """주식 페이지와 같은 방식의 최근 1개월 경향 라인차트를 품은 미니 타일."""
    import plotly.graph_objects as go
    st.metric(label, value, delta)
    if hist:
        fig = go.Figure(go.Scatter(
            x=[h["Date"] for h in hist], y=[h["Close"] for h in hist],
            mode="lines", line=dict(color=_ACCENT, width=2),
            hovertemplate="%{x}<br>%{y:,.2f}<extra></extra>",
        ))
        # 현시점 점 마커 (수치는 위 메트릭에 이미 표시)
        fig.add_trace(go.Scatter(x=[hist[-1]["Date"]], y=[hist[-1]["Close"]],
                                 mode="markers", marker=dict(color=_ACCENT, size=7),
                                 showlegend=False, hoverinfo="skip"))
        fig.update_layout(
            height=104, margin=dict(l=0, r=0, t=4, b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=True, nticks=3, tickformat="%m/%d",
                       tickfont=dict(size=9), showgrid=False),
            yaxis=dict(visible=False), showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


_m1, _m2, _m3 = st.columns([1, 1, 2], gap="small")

with _m1:
    with st.container(border=True):
        # [주석] 1mo 이력 추이는 6시간 캐시 fetch_stock_data_long을 사용해 무한 대기 멈춤을 방지합니다.
        _fx = fetch_stock_data_long("KRW=X", "1mo")
        if _fx and _fx.get("ok"):
            _render_trend_tile("환율 USD/KRW", f"{_fx['price']:,.0f}원",
                               f"{_fx['change_pct']:+.2f}%", _fx.get("history", []))
        else:
            st.metric("환율 USD/KRW", "—", help="데이터 로딩 실패 — 잠시 후 새로고침")
        _mark_tile()

with _m2:
    with st.container(border=True):
        # [주석] 1mo 이력 추이는 6시간 캐시 fetch_stock_data_long을 사용해 무한 대기 멈춤을 방지합니다.
        _oil = fetch_stock_data_long("CL=F", "1mo")
        if _oil and _oil.get("ok"):
            _render_trend_tile("유가 WTI", f"${_oil['price']:,.2f}",
                               f"{_oil['change_pct']:+.2f}%", _oil.get("history", []))
        else:
            st.metric("유가 WTI", "—", help="데이터 로딩 실패 — 잠시 후 새로고침")
        _mark_tile()

with _m3:
    with st.container(border=True):
        traffic = fetch_traffic_status()
        render_traffic_summary(traffic, limit=3)
        _mark_tile()

_tc1, _tc2, _tc3 = st.columns(3)
with _tc1:
    st.link_button("네이버 지도 (교통)", "https://map.naver.com/p?c=15.00,0,0,0,dh&mapMode=0&trafficMode=1", use_container_width=True)
with _tc2:
    st.link_button("카카오맵", "https://map.kakao.com/", use_container_width=True)
with _tc3:
    st.link_button("ITS 실시간 교통", "https://www.its.go.kr/", use_container_width=True)

st.markdown("---")
render_download_buttons()

# ── 관련 영상 ─────────────────────────────────────────────────────
st.markdown("---")
_today_str = datetime.datetime.now().strftime("%Y년 %m월 %d일")
st.markdown(f"## {_today_str} 생활정보 영상")
# 유튜브 수집은 홈 첫 로딩의 최대 지연 요인 — 클릭 시 지연 로드 (세션 내 유지)
if st.session_state.get("home_yt_loaded"):
    from utils.expert_template import render_youtube_section
    render_youtube_section("오늘 뉴스 시사 경제", sort="latest")
else:
    st.caption("홈을 빠르게 열기 위해 영상 목록은 버튼을 누를 때 불러옵니다.")
    if st.button("생활정보 영상 불러오기", use_container_width=True):
        st.session_state["home_yt_loaded"] = True
        st.rerun()

st.markdown("---")
st.markdown("## 전체 카테고리 (38개 페이지)")
st.caption("카테고리 안의 항목을 클릭하면 해당 페이지로 이동합니다. 사이드바에서도 그룹별로 탐색 가능합니다.")

# (카테고리 제목, [(페이지 파일, 표시 라벨, 아이콘), ...])
_categories = [
    ("🌤️ 일상·생활", [
        ("views/01_Weather.py", "날씨", "🌤️"),
        ("views/02_News.py", "뉴스", "📰"),
        ("views/03_Traffic.py", "교통", "🚗"),
        ("views/07_Food.py", "식생활", "🍽️"),
        ("views/13_Shopping.py", "쇼핑/소비", "🛍️"),
        ("views/10_Travel.py", "여행", "✈️"),
    ]),
    ("💰 금융·투자", [
        ("views/05_Finance.py", "생활금융", "💰"),
        ("views/12_Stock.py", "주식 분석", "📈"),
        ("views/18_Exchange.py", "환율/유가", "💱"),
        ("views/32_Crypto.py", "암호화폐", "🪙"),
    ]),
    ("🚨 안전·재난·정책", [
        ("views/33_Safety.py", "재난·안전", "🚨"),
        ("views/36_CyberSecurity.py", "사이버 보안", "🛡️"),
        ("views/34_PublicUtility.py", "공공요금", "💡"),
        ("views/35_Policy.py", "정부 정책", "🏛️"),
        ("views/31_Environment.py", "환경/에너지", "🌱"),
        ("views/11_Legal.py", "생활법률", "⚖️"),
    ]),
    ("🏥 건강·가족", [
        ("views/06_Health.py", "건강", "🏥"),
        ("views/30_Insurance.py", "보험/연금", "🛡️"),
        ("views/14_Parenting.py", "육아/보육", "👶"),
        ("views/09_Education.py", "교육", "📚"),
        ("views/37_Demography.py", "인구·결혼", "👰"),
        ("views/38_Silver.py", "실버산업", "👴"),
    ]),
    ("🏠 부동산·자동차", [
        ("views/08_RealEstate.py", "부동산", "🏠"),
        ("views/29_Car.py", "자동차", "🚗"),
    ]),
    ("🏢 비즈니스", [
        ("views/20_Business.py", "사업/창업", "🏢"),
        ("views/19_Customs.py", "관세/무역", "🚢"),
        ("views/21_Transport.py", "운송/물류", "🚚"),
        ("views/25_Tech.py", "IT/테크", "💻"),
        ("views/26_Jobs.py", "취업/채용", "💼"),
    ]),
    ("🎬 문화·여가", [
        ("views/15_Culture.py", "문화/예술", "🎭"),
        ("views/28_Entertainment.py", "연예/엔터", "🎬"),
        ("views/27_Sports.py", "스포츠", "⚽"),
        ("views/16_Pet.py", "반려동물", "🐾"),
        ("views/17_Flower.py", "화훼/식물", "🌷"),
    ]),
    ("🌍 글로벌", [
        ("views/22_GlobalWar.py", "해외 분쟁/전쟁", "🌍"),
    ]),
    ("🛠️ 도구", [
        ("views/04_Data_Collector.py", "데이터 수집 (마스터 리포트)", "📊"),
    ]),
]

_cat_cols = st.columns(3)
for i, (cat_title, page_items) in enumerate(_categories):
    with _cat_cols[i % 3]:
        with st.container(border=True):
            st.markdown(f"**{cat_title}**")
            for page_path, label, icon in page_items:
                try:
                    st.page_link(page_path, label=label, icon=icon)
                except Exception:
                    # page_link 실패(미등록 페이지 등) 시 텍스트 표시로 폴백
                    st.markdown(f"<small style='color:var(--muted)'>{icon} {label}</small>", unsafe_allow_html=True)
            _mark_tile()
