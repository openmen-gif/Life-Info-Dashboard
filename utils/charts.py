# -*- coding: utf-8 -*-
"""공용 차트 헬퍼 — Y축이 데이터 범위에 밀착되는 plotly 라인차트 + 정규화 비교 차트.

주식(12_Stock)·환율/유가(18_Exchange) 페이지가 공유한다.
색상은 css_loader.py :root 토큰과 동일 값을 유지한다 (plotly는 CSS 변수 접근 불가).
"""
import math

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ACCENT = "#7C9CFF"                      # --accent
GRID = "rgba(255,255,255,0.08)"
GRID_SOFT = "rgba(255,255,255,0.04)"


def nice_dtick(vmin: float, vmax: float) -> float:
    """Y축 눈금 간격을 1-2-5 계열로 산정 (범위/6 기준) — 변동 폭이 읽히는 간격 보장."""
    rng = max(vmax - vmin, 1e-9)
    raw = rng / 6
    mag = 10 ** math.floor(math.log10(raw))
    for m in (1, 2, 5, 10):
        if raw <= m * mag:
            return m * mag
    return 10 * mag


def render_trend_with_stats(history: list, unit: str = "", decimals: int = 2,
                            dtick: float | None = None, height: int = 320,
                            show_stats: bool = True) -> None:
    """history=[{"Date","Close"}...] → Y축 데이터 범위 밀착 라인차트 + 통계 5종.

    unit: 표시 통화 기호($/₩/€/¥ 또는 ""), decimals: 소수 자리,
    dtick: Y축 눈금 간격(예: KRW 10원). None이면 1-2-5 계열 자동."""
    if not history:
        st.warning("추세 데이터를 가져오지 못했습니다.")
        return
    closes = [r["Close"] for r in history]
    if dtick is None:
        dtick = nice_dtick(min(closes), max(closes))
    pad = max((max(closes) - min(closes)) * 0.08, dtick * 0.3)
    fig = go.Figure(go.Scatter(
        x=[r["Date"] for r in history], y=closes,
        mode="lines", line=dict(color=ACCENT, width=2),
        hovertemplate="%{x}<br>%{y:,." + str(decimals) + "f}<extra></extra>",
    ))
    fig.update_layout(
        height=height, margin=dict(l=0, r=0, t=8, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(range=[min(closes) - pad, max(closes) + pad],
                   dtick=dtick, tickformat=f",.{decimals}f", gridcolor=GRID),
        xaxis=dict(gridcolor=GRID_SOFT),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.caption(f"Y축 눈금 간격: {unit + ' ' if unit else ''}{dtick:g} · 축 범위는 데이터에 맞춤")
    if not show_stats:
        return
    avg = sum(closes) / len(closes)
    total_change = closes[-1] - closes[0]
    total_pct = (total_change / closes[0] * 100) if closes[0] else 0
    fmt = f",.{decimals}f"
    u = f"{unit} " if unit else ""
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("현재", f"{u}{closes[-1]:{fmt}}")
    c2.metric("최고", f"{u}{max(closes):{fmt}}")
    c3.metric("최저", f"{u}{min(closes):{fmt}}")
    c4.metric("평균", f"{u}{avg:{fmt}}")
    c5.metric("기간 등락", f"{total_change:+{fmt}} ({total_pct:+.1f}%)")


def render_line_tight(history: list, decimals: int = 2, height: int = 300,
                      dtick: float | None = None) -> None:
    """history=[{"Date","Close"}...] → Y축 데이터 범위 밀착 라인차트 (통계 행 없음).

    st.line_chart 대체용 — 모든 지표 추이 차트의 표준."""
    render_trend_with_stats(history, unit="", decimals=decimals, dtick=dtick,
                            height=height, show_stats=False)


def render_normalized_compare(series_map: dict, caption: str, height: int = 340) -> None:
    """{라벨: [{"Date","Close"}...]} → 시작일=100 정규화 상대 변화율 비교 차트.

    상대 비교이므로 Y축을 데이터 범위에 밀착시킨다 (기준선 100 점선 표시).
    날짜(concat+dropna) 기준으로 공통 구간을 정렬해 비교한다."""
    frames = []
    for label, hist in series_map.items():
        if hist:
            frames.append(pd.DataFrame(hist).set_index("Date")["Close"].rename(label))
    if not frames:
        st.warning("비교할 추세 데이터가 없습니다.")
        return
    df = pd.concat(frames, axis=1).dropna()
    if len(df) < 2:
        st.warning("비교 구간의 공통 데이터가 부족합니다.")
        return
    df_norm = df / df.iloc[0] * 100
    x = pd.to_datetime(df_norm.index)
    vmin, vmax = float(df_norm.values.min()), float(df_norm.values.max())
    pad = max((vmax - vmin) * 0.1, 0.3)
    fig = go.Figure()
    for col in df_norm.columns:
        fig.add_trace(go.Scatter(x=x, y=df_norm[col], mode="lines",
                                 name=str(col), line=dict(width=2)))
    fig.add_hline(y=100, line_dash="dot", line_color="rgba(255,255,255,0.25)")
    fig.update_layout(
        height=height, margin=dict(l=0, r=0, t=8, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(range=[min(vmin - pad, 100 - pad), max(vmax + pad, 100 + pad)],
                   gridcolor=GRID),
        xaxis=dict(gridcolor=GRID_SOFT),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.caption(caption)
