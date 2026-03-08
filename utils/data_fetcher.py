"""Data fetchers for weather, news, and traffic information.
Supports dual-mode: API (FastAPI backend) and Standalone (Local fetching)."""
import requests
import datetime
import feedparser
from typing import Optional
import streamlit as st
from utils.config import IS_API_MODE, API_BASE_URL

# ── Local Fetching Logic (Fallback/Standalone) ──────────────────────────────
def _fetch_weather_local(city: str, api_key: Optional[str]) -> dict:
    if api_key:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=kr"
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            d = r.json()
            return {
                "city": city,
                "temp": d["main"]["temp"],
                "feels_like": d["main"]["feels_like"],
                "humidity": d["main"]["humidity"],
                "desc": d["weather"][0]["description"],
                "icon": d["weather"][0]["icon"],
                "wind_speed": d["wind"]["speed"],
                "updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
        except Exception:
            pass
    return {
        "city": city, "temp": 12.5, "feels_like": 10.2, "humidity": 55,
        "desc": "맑음", "icon": "01d", "wind_speed": 3.2,
        "updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "_sample": True,
    }

NEWS_FEEDS = {
    "종합": "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko",
    "IT/과학": "https://news.google.com/rss/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNRGRqTVhZU0FtdHZLQUFQAQ?hl=ko&gl=KR&ceid=KR:ko",
    "경제": "https://news.google.com/rss/topics/CAAqIggKIhxDQkFTRHdvSkwyMHZNR2RtY0RFU0FtdHZLQUFQAQ?hl=ko&gl=KR&ceid=KR:ko",
    "생활": "https://news.google.com/rss/topics/CAAqIggKIhxDQkFTRHdvSkwyMHZNREp0WTJvU0FtdHZLQUFQAQ?hl=ko&gl=KR&ceid=KR:ko",
}

def _fetch_news_local(category: str, limit: int) -> list[dict]:
    url = NEWS_FEEDS.get(category, NEWS_FEEDS["종합"])
    try:
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries[:limit]:
            items.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "source": entry.get("source", {}).get("title", ""),
                "published": entry.get("published", ""),
            })
        return items
    except Exception:
        return []

def _fetch_traffic_local() -> list[dict]:
    return [
        {"route": "경부고속도로 (서울→부산)", "status": "원활", "speed_kmh": 95, "color": "green"},
        {"route": "서해안고속도로 (서울→목포)", "status": "서행", "speed_kmh": 45, "color": "orange"},
        {"route": "영동고속도로 (서울→강릉)", "status": "정체", "speed_kmh": 20, "color": "red"},
        {"route": "중부고속도로 (서울→대전)", "status": "원활", "speed_kmh": 88, "color": "green"},
        {"route": "호남고속도로 (대전→광주)", "status": "원활", "speed_kmh": 100, "color": "green"},
    ]

# ── API Calls (Backend) and Public Functions ───────────────────────────────

@st.cache_data(ttl=600, show_spinner=False)
def fetch_weather(city: str = "Seoul", api_key: Optional[str] = None) -> dict:
    """Fetch weather data from API or fallback to local execution."""
    if IS_API_MODE:
        try:
            params = {"city": city}
            if api_key:
                params["api_key"] = api_key
            r = requests.get(f"{API_BASE_URL}/data/weather", params=params, timeout=5)
            r.raise_for_status()
            return r.json()
        except Exception:
            pass  # Fallback to local on API failure
    return _fetch_weather_local(city, api_key)

@st.cache_data(ttl=300, show_spinner=False)
def fetch_news(category: str = "종합", limit: int = 10) -> list[dict]:
    """Fetch news data from API or fallback to local execution."""
    if IS_API_MODE:
        try:
            r = requests.get(f"{API_BASE_URL}/data/news", params={"category": category, "limit": limit}, timeout=5)
            r.raise_for_status()
            return r.json().get("news", [])
        except Exception:
            pass
    return _fetch_news_local(category, limit)

@st.cache_data(ttl=300, show_spinner=False)
def fetch_traffic_status() -> list[dict]:
    """Fetch traffic data from API or fallback to local execution."""
    if IS_API_MODE:
        try:
            r = requests.get(f"{API_BASE_URL}/data/traffic", timeout=5)
            r.raise_for_status()
            return r.json().get("traffic", [])
        except Exception:
            pass
    return _fetch_traffic_local()
