"""Custom CSS loader for Streamlit — 벤토 다크 글래스 토큰 시스템 + 데스크톱/모바일 반응형."""
import streamlit as st


def apply_custom_css():
    st.markdown("""
    <style>
    /* Hallmark · macrostructure: Bento Grid · theme: custom(벤토 다크 글래스) · tone: utilitarian
     * paper: #0A0D14 · accent: #7C9CFF · 2026 트렌드 A안 승인(2026-07-18)
     * 색·라운드는 반드시 아래 토큰만 참조 — 인라인 hex 추가 금지 */
    @import url("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css");

    /* ── Design Tokens ──────────────────────────────────── */
    :root {
        --bg: #0A0D14;
        --panel: rgba(255, 255, 255, 0.045);
        --panel-solid: #12161F;
        --line: rgba(255, 255, 255, 0.09);
        --ink: #E7EAF2;
        --ink-2: #C6CCDA;
        --muted: #8B93A7;
        --accent: #7C9CFF;
        --accent-soft: rgba(124, 156, 255, 0.16);
        --up: #FF6B6B;      /* 상승 — 한국 시장 관례 */
        --down: #4D96FF;    /* 하락 — 한국 시장 관례 */
        --radius: 14px;
        --radius-sm: 8px;
    }

    /* ── Base (Desktop) ─────────────────────────────────── */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
        font-family: "Pretendard Variable", Pretendard, -apple-system, "Malgun Gothic", sans-serif;
    }
    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(1100px 480px at 18% -8%, var(--accent-soft), transparent 62%),
            var(--bg);
    }
    /* 본문 폭 제한 + 중앙 정렬 — 초광폭 화면에서 가장자리 붙음(사이드 여백 부족) 방지 */
    .block-container,
    [data-testid="stMainBlockContainer"],
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 1rem;
        max-width: 1320px;
        padding-left: 3rem;
        padding-right: 3rem;
        margin-left: auto;
        margin-right: auto;
    }

    h1 { color: var(--ink); font-weight: 800; letter-spacing: -0.01em; }
    h2 { color: var(--ink); font-weight: 700; }
    h3 { color: var(--ink-2); font-weight: 700; }

    /* 메트릭 — 글래스 카드 (신·구 셀렉터 병기) */
    .stMetric, [data-testid="stMetric"] {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: var(--radius);
        padding: 15px 18px;
        backdrop-filter: blur(8px);
    }
    .stMetric label, [data-testid="stMetricLabel"] { color: var(--muted); }
    [data-testid="stMetricValue"], [data-testid="stMetricDelta"] {
        font-variant-numeric: tabular-nums;
    }

    /* 글래스 타일 — .tile-marker를 품은 보더 컨테이너만 opt-in.
       (Streamlit 1.42는 테두리 없는 일반 컨테이너도 같은 wrapper를 쓰므로
        일괄 적용하면 패딩 없는 유령 박스가 생김 — 마커 방식으로 한정) */
    .tile-marker { display: none; }
    /* :not(...)으로 조상 wrapper 제외 — 마커를 직접 품은 최근접 wrapper만 칠한다 */
    [data-testid="stVerticalBlockBorderWrapper"]:has(.tile-marker):not(:has([data-testid="stVerticalBlockBorderWrapper"] .tile-marker)) {
        background: var(--panel);
        border-radius: var(--radius);
    }
    /* 글래스 타일 안의 메트릭은 이중 카드 방지 — 평면화 */
    [data-testid="stVerticalBlockBorderWrapper"]:has(.tile-marker):not(:has([data-testid="stVerticalBlockBorderWrapper"] .tile-marker)) .stMetric,
    [data-testid="stVerticalBlockBorderWrapper"]:has(.tile-marker):not(:has([data-testid="stVerticalBlockBorderWrapper"] .tile-marker)) [data-testid="stMetric"] {
        background: transparent;
        border: 0;
        border-radius: 0;
        padding: 4px 2px;
        backdrop-filter: none;
    }

    /* 사이드바 */
    [data-testid="stSidebar"] {
        background: var(--panel-solid);
        border-right: 1px solid var(--line);
    }
    /* 사이드바 내비 — 그룹 헤더(작은 악센트 라벨 + 구분선) vs 항목(들여쓰기) 위계 분리 */
    [data-testid="stNavSectionHeader"] {
        color: var(--accent) !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.07em;
        margin-top: 14px;
        padding-top: 12px;
        border-top: 1px solid var(--line);
    }
    [data-testid="stSidebarNavItems"] > header:first-child {
        border-top: 0;
        margin-top: 0;
        padding-top: 0;
    }
    [data-testid="stSidebarNavLink"] {
        margin-left: 10px;
    }
    [data-testid="stSidebarNavLink"] span {
        color: var(--ink-2);
    }

    /* 탭 */
    .stTabs [data-baseweb="tab-list"] button { color: var(--muted); }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] { color: var(--accent); }
    .stTabs [data-baseweb="tab-highlight"] { background-color: var(--accent); }

    /* 버튼 — 라운드 통일 + 포커스 가시화 */
    .stButton > button, .stLinkButton > a, .stDownloadButton > button {
        border-radius: 10px;
    }
    .stButton > button:focus-visible,
    .stLinkButton > a:focus-visible,
    .stDownloadButton > button:focus-visible {
        outline: 2px solid var(--accent);
        outline-offset: 2px;
    }

    /* 구분선 */
    hr { border-color: var(--line); }

    /* info-card — 그라데이션·컬러보더 폐기, 글래스 카드로 통일 */
    .info-card {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: var(--radius); padding: 20px; margin: 10px 0;
    }
    /* 페이지네이션 마커(비표시) — 이 마커를 품은 컬럼 행은 모바일에서도 가로 유지 */
    .pager-marker { display: none; }
    /* iframe 반응형 */
    iframe {
        max-width: 100% !important;
        width: 100% !important;
        border-radius: var(--radius-sm);
    }

    /* ── Mobile (max-width: 768px) ───────────────────────── */
    @media (max-width: 768px) {
        /* 사이드바 숨김 — 햄버거 메뉴로 접근 */
        [data-testid="stSidebar"] {
            min-width: 0 !important;
        }
        /* 상단 고정 헤더(햄버거 메뉴 바)에 본문/사이드바 상단 글자가 가려지지 않게 여백 확보 */
        [data-testid="stHeader"] { background: rgba(10, 13, 20, 0.92) !important; }
        [data-testid="stSidebarContent"],
        [data-testid="stSidebar"] > div:first-child {
            padding-top: 2.8rem !important;
        }
        /* 전체 패딩 축소 — 단, 상단은 고정 헤더 높이만큼 확보 (구/신 컨테이너 모두 타깃) */
        .block-container,
        [data-testid="stMainBlockContainer"],
        [data-testid="stAppViewBlockContainer"] {
            padding: 3.8rem 0.8rem 0.6rem !important;
            max-width: 100% !important;
        }
        /* 제목 크기 축소 */
        h1 { font-size: 1.4rem !important; }
        h2 { font-size: 1.2rem !important; }
        h3 { font-size: 1.05rem !important; }
        /* 메트릭 카드 축소 */
        .stMetric, [data-testid="stMetric"] {
            padding: 8px 10px !important;
            border-radius: var(--radius-sm) !important;
        }
        .stMetric [data-testid="stMetricValue"] {
            font-size: 1.2rem !important;
        }
        .stMetric [data-testid="stMetricLabel"] {
            font-size: 0.75rem !important;
        }
        .stMetric [data-testid="stMetricDelta"] {
            font-size: 0.7rem !important;
        }
        /* Columns → 세로 스택 */
        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
            gap: 0.3rem !important;
        }
        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            min-width: 100% !important;
            flex: 1 1 100% !important;
        }
        /* 예외: 페이지네이션(◀ 1 2 3 ▶)은 세로로 쌓이면 어색 — 가로 유지 */
        [data-testid="stHorizontalBlock"]:has(.pager-marker) {
            flex-wrap: nowrap !important;
            gap: 0.25rem !important;
        }
        [data-testid="stHorizontalBlock"]:has(.pager-marker) > [data-testid="stColumn"] {
            min-width: 0 !important;
            flex: 0 0 auto !important;
        }
        [data-testid="stHorizontalBlock"]:has(.pager-marker) .stButton > button {
            min-height: 38px !important;
            padding: 6px 12px !important;
        }
        /* 탭 글씨 축소 */
        .stTabs [data-baseweb="tab-list"] button {
            font-size: 0.8rem !important;
            padding: 6px 10px !important;
        }
        /* 버튼 — 터치 타깃 최소 44px 확보(Apple/Google 모바일 접근성 권장) */
        .stButton > button {
            font-size: 0.85rem !important;
            padding: 11px 16px !important;
            min-height: 44px !important;
        }
        /* 링크/다운로드 버튼도 동일 터치 타깃 */
        .stLinkButton > a, .stDownloadButton > button {
            min-height: 44px !important;
        }
        /* info-card 모바일 */
        .info-card {
            padding: 12px !important;
            margin: 6px 0 !important;
        }
        /* iframe 반응형 높이 */
        iframe {
            height: min(400px, 60vh) !important;
        }
        /* 영상 카드 이미지 */
        .video-card img {
            max-width: 100% !important;
            height: auto !important;
        }
        /* 테이블 가로 스크롤 + 스크롤바 가시화 (잘린 것처럼 보여 스크롤 가능을 모르는 문제 해소) */
        [data-testid="stDataFrame"] {
            overflow-x: auto !important;
        }
        [data-testid="stDataFrame"]::-webkit-scrollbar { height: 6px; }
        [data-testid="stDataFrame"]::-webkit-scrollbar-thumb {
            background: var(--muted); border-radius: 3px;
        }
        /* 슬라이더 */
        .stSlider {
            padding: 0 !important;
        }
        /* 캡션 / 작은 텍스트 */
        .stCaption, small {
            font-size: 0.7rem !important;
        }
    }

    /* ── Small Mobile (max-width: 480px) ─────────────────── */
    @media (max-width: 480px) {
        .block-container,
        [data-testid="stMainBlockContainer"],
        [data-testid="stAppViewBlockContainer"] {
            padding: 3.6rem 0.5rem 0.4rem !important;  /* 상단 헤더 클리어런스 유지 */
        }
        h1 { font-size: 1.2rem !important; }
        h2 { font-size: 1.05rem !important; }
        h3 { font-size: 0.95rem !important; }
        iframe {
            height: min(300px, 50vh) !important;
        }
        /* 탭이 너무 많으면 스크롤 */
        .stTabs [data-baseweb="tab-list"] {
            overflow-x: auto !important;
            flex-wrap: nowrap !important;
        }
        .stTabs [data-baseweb="tab-list"] button {
            font-size: 0.7rem !important;
            padding: 4px 8px !important;
            white-space: nowrap !important;
        }
    }

    /* ── Tablet (769px ~ 1024px) ─────────────────────────── */
    @media (min-width: 769px) and (max-width: 1024px) {
        /* 3열 이상은 2열로 축소 */
        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
        }
        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            min-width: 48% !important;
            flex: 1 1 48% !important;
        }
        /* 예외: 페이지네이션은 가로 유지 */
        [data-testid="stHorizontalBlock"]:has(.pager-marker) {
            flex-wrap: nowrap !important;
        }
        [data-testid="stHorizontalBlock"]:has(.pager-marker) > [data-testid="stColumn"] {
            min-width: 0 !important;
            flex: 0 0 auto !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
