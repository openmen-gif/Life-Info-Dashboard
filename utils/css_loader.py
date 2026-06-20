"""Custom CSS loader for Streamlit — desktop + mobile responsive."""
import streamlit as st


def apply_custom_css():
    st.markdown("""
    <style>
    /* ── Base (Desktop) ──────────────────────────────────── */
    .block-container { padding-top: 1rem; }
    .stMetric { background: #1a1a2e; border-radius: 10px; padding: 15px; }
    .stMetric label { color: #8892b0; }
    h1 { color: #64ffda; }
    h2 { color: #8892b0; }
    h3 { color: #ccd6f6; }
    .info-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 12px; padding: 20px; margin: 10px 0;
        border-left: 4px solid #4CAF50;
    }
    /* iframe 반응형 */
    iframe {
        max-width: 100% !important;
        width: 100% !important;
    }

    /* ── Mobile (max-width: 768px) ───────────────────────── */
    @media (max-width: 768px) {
        /* 사이드바 숨김 — 햄버거 메뉴로 접근 */
        [data-testid="stSidebar"] {
            min-width: 0 !important;
        }
        /* 상단 고정 헤더(햄버거 메뉴 바)에 본문/사이드바 상단 글자가 가려지지 않게 여백 확보 */
        [data-testid="stHeader"] { background: rgba(14,17,23,0.92) !important; }
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
        .stMetric {
            padding: 8px 10px !important;
            border-radius: 8px !important;
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
        /* 탭 글씨 축소 */
        .stTabs [data-baseweb="tab-list"] button {
            font-size: 0.8rem !important;
            padding: 6px 10px !important;
        }
        /* 버튼 크기 */
        .stButton > button {
            font-size: 0.8rem !important;
            padding: 6px 12px !important;
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
        /* 테이블 가로 스크롤 */
        [data-testid="stDataFrame"] {
            overflow-x: auto !important;
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
    }
    </style>
    """, unsafe_allow_html=True)
