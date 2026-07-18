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
UP = "#FF6B6B"                          # --up (상승/최고)
DOWN = "#4D96FF"                        # --down (하락/최저)
GRID = "rgba(255,255,255,0.08)"
GRID_SOFT = "rgba(255,255,255,0.04)"
_REF_LINE = "rgba(255,255,255,0.35)"


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
    # 현시점(마지막) 값 — 점 마커 + 숫자 라벨
    _lx, _ly = history[-1]["Date"], closes[-1]
    fig.add_trace(go.Scatter(x=[_lx], y=[_ly], mode="markers",
                             marker=dict(color=ACCENT, size=8),
                             showlegend=False, hoverinfo="skip"))
    fig.add_annotation(x=_lx, y=_ly, text=f"{_ly:,.{decimals}f}",
                       showarrow=False, xanchor="right", yanchor="bottom",
                       font=dict(size=11))
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


def render_temp_daily(daily: list, today: str, height: int = 340) -> None:
    """일별 최고·최저 기온 — 과거(실선) + 예보(점선), '오늘' 세로 기준선.

    daily=[{"Date","tmax","tmin","pop"}...], today="YYYY-MM-DD"."""
    if not daily:
        st.warning("기온 추이 데이터를 가져오지 못했습니다.")
        return
    past = [r for r in daily if r["Date"] <= today]
    future = [r for r in daily if r["Date"] >= today]  # 오늘 포함 — 선이 끊기지 않게

    fig = go.Figure()

    def _add(rows, key, color, name, dash=None):
        if len(rows) >= 2:
            fig.add_trace(go.Scatter(
                x=[r["Date"] for r in rows], y=[r[key] for r in rows],
                mode="lines", name=name,
                line=dict(color=color, width=2, dash=dash),
                hovertemplate="%{x}<br>%{y:.1f}°C<extra>" + name + "</extra>",
            ))

    _add(past, "tmax", UP, "최고(관측)")
    _add(future, "tmax", UP, "최고(예보)", dash="dash")
    _add(past, "tmin", DOWN, "최저(관측)")
    _add(future, "tmin", DOWN, "최저(예보)", dash="dash")

    vals = [r["tmax"] for r in daily] + [r["tmin"] for r in daily]
    pad = max((max(vals) - min(vals)) * 0.1, 0.5)
    fig.add_vline(x=today, line_dash="dot", line_color=_REF_LINE)
    fig.add_annotation(x=today, y=1, yref="paper", text="오늘", showarrow=False,
                       yanchor="bottom", font=dict(size=11))
    # 현시점(오늘) 최고·최저 수치 표기
    _tr = next((r for r in daily if r["Date"] == today), None)
    if _tr:
        fig.add_trace(go.Scatter(x=[today, today], y=[_tr["tmax"], _tr["tmin"]],
                                 mode="markers", marker=dict(color=[UP, DOWN], size=8),
                                 showlegend=False, hoverinfo="skip"))
        fig.add_annotation(x=today, y=_tr["tmax"], text=f"{_tr['tmax']:.0f}°",
                           showarrow=False, xanchor="left", yanchor="bottom",
                           font=dict(size=12, color=UP))
        fig.add_annotation(x=today, y=_tr["tmin"], text=f"{_tr['tmin']:.0f}°",
                           showarrow=False, xanchor="left", yanchor="top",
                           font=dict(size=12, color=DOWN))
    fig.update_layout(
        height=height, margin=dict(l=0, r=0, t=28, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(range=[min(vals) - pad, max(vals) + pad],
                   ticksuffix="°", gridcolor=GRID),
        xaxis=dict(gridcolor=GRID_SOFT),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.caption("실선 = 관측(지난 7일) · 점선 = 예보(7일) · 데이터: Open-Meteo")


def render_temp_hourly(hourly: list, now_hour: str, height: int = 280,
                       compact: bool = False) -> None:
    """시간대별 기온 — 과거(실선) + 예보(점선), '지금' 세로 기준선.

    hourly=[{"Time","temp"}...], now_hour="YYYY-MM-DDTHH:00".
    compact=True면 홈 타일용 미니 차트(축·범례·캡션 생략)."""
    if not hourly:
        if not compact:
            st.warning("시간대별 기온 데이터를 가져오지 못했습니다.")
        return
    past = [r for r in hourly if r["Time"] <= now_hour]
    future = [r for r in hourly if r["Time"] >= now_hour]

    fig = go.Figure()
    if len(past) >= 2:
        fig.add_trace(go.Scatter(
            x=[r["Time"] for r in past], y=[r["temp"] for r in past],
            mode="lines", name="관측", line=dict(color=ACCENT, width=2),
            hovertemplate="%{x}<br>%{y:.1f}°C<extra>관측</extra>"))
    if len(future) >= 2:
        fig.add_trace(go.Scatter(
            x=[r["Time"] for r in future], y=[r["temp"] for r in future],
            mode="lines", name="예보", line=dict(color=ACCENT, width=2, dash="dash"),
            hovertemplate="%{x}<br>%{y:.1f}°C<extra>예보</extra>"))
    fig.add_vline(x=now_hour, line_dash="dot", line_color=_REF_LINE)

    # 현시점(지금) 기온 — 점 마커 + 수치 표기
    _now_row = next((r for r in hourly if r["Time"] == now_hour), None) or (past[-1] if past else None)
    if _now_row:
        fig.add_trace(go.Scatter(x=[_now_row["Time"]], y=[_now_row["temp"]],
                                 mode="markers", marker=dict(color=ACCENT, size=7),
                                 showlegend=False, hoverinfo="skip"))
        fig.add_annotation(x=_now_row["Time"], y=_now_row["temp"],
                           text=f"{_now_row['temp']:.1f}°", showarrow=False,
                           xanchor="left", yanchor="bottom",
                           font=dict(size=10 if compact else 12, color=ACCENT))

    vals = [r["temp"] for r in hourly]
    pad = max((max(vals) - min(vals)) * 0.1, 0.5)
    if compact:
        fig.update_layout(
            height=max(70, height if height < 200 else 96),
            margin=dict(l=0, r=0, t=2, b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=True, nticks=3, tickformat="%m/%d %H시",
                       tickfont=dict(size=9), showgrid=False),
            yaxis=dict(visible=False),
            showlegend=False,
        )
    else:
        fig.add_annotation(x=now_hour, y=1, yref="paper", text="지금", showarrow=False,
                           yanchor="bottom", font=dict(size=11))
        fig.update_layout(
            height=height, margin=dict(l=0, r=0, t=28, b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(range=[min(vals) - pad, max(vals) + pad],
                       ticksuffix="°", gridcolor=GRID),
            xaxis=dict(gridcolor=GRID_SOFT),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    if not compact:
        st.caption("실선 = 관측 · 점선 = 예보 · 어제부터 내일모레까지 1시간 간격")


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
    # 현시점(마지막) 상대값 수치 표기 — 시리즈별
    for col in df_norm.columns:
        fig.add_annotation(x=x[-1], y=float(df_norm[col].iloc[-1]),
                           text=f"{df_norm[col].iloc[-1]:,.1f}", showarrow=False,
                           xanchor="right", yanchor="bottom", font=dict(size=10))
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
