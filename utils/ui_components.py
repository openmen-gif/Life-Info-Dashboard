import streamlit as st

def render_weather_card(weather: dict):
    """Render a concise weather summary card."""
    st.markdown("### 🌤️ 오늘의 날씨")
    st.metric(
        label=f"{weather.get('city', 'Unknown')}",
        value=f"{weather.get('temp', '-')}°C",
        delta=f"체감 {weather.get('feels_like', '-')}°C",
    )
    st.caption(f"{weather.get('desc', '')} | 습도 {weather.get('humidity', '-')}% | 풍속 {weather.get('wind_speed', '-')}m/s")
    if weather.get("_sample"):
        st.info("API 키 미설정 — 샘플 데이터")

def render_news_summary(news_list: list, limit: int = 5):
    """Render a concise list of news headlines."""
    st.markdown("### 📰 주요 뉴스")
    if news_list:
        for item in news_list[:limit]:
            src = f" ({item['source']})" if item.get("source") else ""
            st.markdown(f"- [{item['title']}]({item['link']}){src}")
    else:
        st.info("뉴스를 불러올 수 없습니다.")

def render_traffic_summary(traffic_list: list, limit: int = 5):
    """Render traffic news headlines with status badges."""
    st.markdown("### 🚗 교통 뉴스")
    if traffic_list:
        for t in traffic_list[:limit]:
            color_icon = {"green": "🟢", "orange": "🟡", "red": "🔴", "blue": "🔵"}.get(t.get("color"), "⚪")
            title = t.get("title", t.get("route", ""))
            link = t.get("link", "")
            status = t.get("status", "")
            if link:
                st.markdown(f"{color_icon} [{title}]({link}) — **{status}**")
            else:
                st.markdown(f"{color_icon} {title} — **{status}**")
        # 실시간 교통 바로가기
        st.caption("[ITS 실시간 교통정보](https://www.its.go.kr/) | [네이버 지도](https://map.naver.com/)")
    else:
        st.info("교통 뉴스를 불러올 수 없습니다.")
        st.caption("[ITS 실시간 교통정보](https://www.its.go.kr/)")
