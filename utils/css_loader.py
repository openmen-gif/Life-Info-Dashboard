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
        /* 전체 패딩 축소 */
        .block-container {
            padding: 0.5rem 0.8rem !important;
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
        /* iframe 높이 축소 */
        iframe {
            height: 350px !important;
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
        .block-container {
            padding: 0.3rem 0.5rem !important;
        }
        h1 { font-size: 1.2rem !important; }
        h2 { font-size: 1.05rem !important; }
        h3 { font-size: 0.95rem !important; }
        iframe {
            height: 280px !important;
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
