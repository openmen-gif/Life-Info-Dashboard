import streamlit as st

def render_weather_card(weather: dict):
    """Render a concise weather summary card. _sample/누락 시 명확한 안내."""
    st.markdown("### 🌤️ 오늘의 날씨")
    is_sample = bool(weather.get("_sample"))
    has_data = weather.get("temp") not in (None, "-") and not is_sample

    if not has_data:
        st.warning("⚠️ 날씨 데이터를 불러오지 못했습니다. Open-Meteo API 응답 지연 가능 — 잠시 후 새로고침해주세요.")
        st.caption(f"도시: {weather.get('city', 'Seoul')} · 갱신 시도: {weather.get('updated', '-')}")
        return

    st.metric(
        label=f"{weather.get('city', 'Unknown')}",
        value=f"{weather.get('temp', '-')}°C",
        delta=f"체감 {weather.get('feels_like', '-')}°C",
    )
    st.caption(
        f"{weather.get('desc', '')} | 습도 {weather.get('humidity', '-')}% | "
        f"풍속 {weather.get('wind_speed', '-')}m/s · 🕒 {weather.get('updated', '-')}"
    )

def _fmt_published(pub: str) -> str:
    """published 문자열을 'MM-DD HH:MM' 형식으로 짧게 표시. 파싱 실패 시 원본 앞 16자."""
    if not pub:
        return ""
    try:
        from dateutil import parser as _dp
        dt = _dp.parse(pub)
        return dt.strftime("%m-%d %H:%M")
    except Exception:
        return str(pub)[:16]


def render_news_summary(news_list: list, limit: int = 5):
    """Render a concise list of news headlines with published date."""
    st.markdown("### 📰 주요 뉴스")
    if news_list:
        for item in news_list[:limit]:
            src = f" ({item['source']})" if item.get("source") else ""
            pub = _fmt_published(item.get("published", ""))
            pub_str = f" · 🕒 {pub}" if pub else ""
            st.markdown(f"- [{item['title']}]({item['link']}){src}{pub_str}")
    else:
        st.info("뉴스를 불러올 수 없습니다.")

def render_traffic_summary(traffic_list: list, limit: int = 5):
    """Render traffic news headlines with status badges + published date."""
    st.markdown("### 🚗 교통 뉴스")
    if traffic_list:
        for t in traffic_list[:limit]:
            color_icon = {"green": "🟢", "orange": "🟡", "red": "🔴", "blue": "🔵"}.get(t.get("color"), "⚪")
            title = t.get("title", t.get("route", ""))
            link = t.get("link", "")
            status = t.get("status", "")
            pub = _fmt_published(t.get("published", ""))
            pub_str = f" · 🕒 {pub}" if pub else ""
            if link:
                st.markdown(f"{color_icon} [{title}]({link}) — **{status}**{pub_str}")
            else:
                st.markdown(f"{color_icon} {title} — **{status}**{pub_str}")
        st.caption("📅 발행 시각은 기사 작성 기준. 1일 이내 기사를 우선 표시합니다. [ITS 실시간 교통정보](https://www.its.go.kr/) | [네이버 지도](https://map.naver.com/)")
    else:
        st.info("교통 뉴스를 불러올 수 없습니다.")
        st.caption("[ITS 실시간 교통정보](https://www.its.go.kr/)")
