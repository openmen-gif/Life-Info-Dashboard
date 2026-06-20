# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

# ── 긴급 안전·재난 정보 (페이지 상단 고정) ─────────────────────────────────
st.markdown("## 🚨 긴급 안전·재난 정보")
st.caption("실시간 재난·안전 정보는 공식 채널을 우선 확인하세요. 정보가 생명을 구합니다.")

_sc1, _sc2, _sc3, _sc4 = st.columns(4)
with _sc1:
    st.link_button("🌀 기상청 특보", "https://www.weather.go.kr/w/special-report/overall.do", use_container_width=True)
with _sc2:
    st.link_button("🚨 국민재난안전포털", "https://www.safekorea.go.kr/", use_container_width=True)
with _sc3:
    st.link_button("🔥 산림청 산불정보", "https://fd.forest.go.kr/ffas/", use_container_width=True)
with _sc4:
    st.link_button("🌋 KMA 지진정보", "https://www.weather.go.kr/w/earthquake-volcano/recent.do", use_container_width=True)

_sc5, _sc6, _sc7, _sc8 = st.columns(4)
with _sc5:
    st.link_button("😷 에어코리아 (대기질)", "https://www.airkorea.or.kr/", use_container_width=True)
with _sc6:
    st.link_button("🚒 119 안전신고센터", "https://www.119.go.kr/", use_container_width=True)
with _sc7:
    st.link_button("🌊 해양수산부 (해상)", "https://www.mof.go.kr/", use_container_width=True)
with _sc8:
    st.link_button("📞 행안부 재난문자", "https://www.safekorea.go.kr/idsiSFK/neo/sfk/cs/sfc/dis/disasterMsgList.jsp", use_container_width=True)

# ── 실시간 강수 레이더 (Rainviewer) ───────────────────────────────────────
# 기상청 정적 합성 PNG(repositary/image/radar/...)는 KMA 가 경로를 폐기해 에러를
# 반환하므로, 임베드는 Rainviewer(X-Frame-Options: ALLOWALL)로 대체한다.
# 기상청 공식 특보·레이더는 상단 버튼(새 탭)으로 제공.
st.markdown("---")
st.markdown("### 🛰️ 실시간 강수 레이더")
st.caption("Rainviewer 인터랙티브 레이더(한반도). 기상청 공식 특보·레이더는 상단 버튼으로 새 탭 이동하세요.")
try:
    import streamlit.components.v1 as components
    components.html(
        '<iframe width="100%" height="460" '
        'src="https://www.rainviewer.com/map.html?loc=36.5,127.8,6&oCS=1&oF=0&oAP=1&c=3&o=83&lm=1&layer=radar-1h&sm=1&sn=1" '
        'frameborder="0" style="border-radius:8px;"></iframe>',
        height=480,
    )
except Exception:
    st.info("레이더 위젯을 불러올 수 없습니다. 상단 '🌀 기상청 특보' 버튼을 이용하세요.")

st.markdown("---")

render_expert_page(
    title="재난·안전",
    icon="🚨",
    default_query="한국 기상특보 태풍 호우 산불 지진 재난 안전",
    auto_news_query="기상특보 태풍 호우 산불 지진 재난 안전",
    sub_topics=[
        ("🌀", "기상특보/태풍", "태풍 호우 폭우 폭설 한파 폭염 기상특보"),
        ("🔥", "산불/화재", "산불 산림 화재 대형화재 안전 대응"),
        ("🌋", "지진/지질", "지진 지질재해 화산 진도 한반도"),
        ("🚨", "사회 안전사고", "교통사고 산업재해 안전사고 인명피해"),
        ("📢", "재난 대비/대피", "재난 대피요령 안전 매뉴얼 행동지침"),
    ],
    external_links=[
        ("🚨 국민재난안전포털", "https://www.safekorea.go.kr/"),
        ("🌀 기상청 특보", "https://www.weather.go.kr/w/special-report/overall.do"),
        ("🔥 산림청 산불정보", "https://fd.forest.go.kr/ffas/"),
        ("🌋 지진정보 KMA", "https://www.weather.go.kr/w/earthquake-volcano/recent.do"),
    ],
)
