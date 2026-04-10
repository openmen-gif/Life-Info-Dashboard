"""Data fetchers for weather, news, and traffic information.
Supports dual-mode: API (FastAPI backend) and Standalone (Local fetching)."""
import requests
import datetime
import feedparser
import re
from typing import Optional
import streamlit as st
from utils.config import IS_API_MODE, API_BASE_URL

# 외부 의존성 모듈 레벨 import (lazy: 실패 시 None)
try:
    from ddgs import DDGS as _DDGS
except ImportError:
    _DDGS = None  # type: ignore

try:
    import yfinance as _yf
except ImportError:
    _yf = None  # type: ignore

# ── 사전 컴파일 정규식 ────────────────────────────────────────────────────────
_PUNCT_RE = re.compile(r"[^\w\s]")
_SPACE_RE = re.compile(r"\s+")

# ── 분야별 제외 키워드 (교차 오염 방지) ──────────────────────────────────────
DOMAIN_EXCLUDE_KEYWORDS = {
    "부동산": ["여행", "관광", "항공권", "호캉스", "맛집", "주식", "코스피", "나스닥", "증시"],
    "주식": ["여행", "관광", "항공권", "부동산", "아파트", "청약", "전세", "매매", "맛집"],
    "여행": ["아파트", "청약", "전세", "매매", "코스피", "나스닥", "증시", "금리", "대출"],
    "생활금융": ["여행", "관광", "항공권", "호캉스", "아파트", "청약", "코스피", "나스닥"],
    "식생활": ["아파트", "청약", "전세", "코스피", "나스닥", "증시", "항공권"],
    "건강": ["아파트", "청약", "코스피", "나스닥", "증시", "항공권", "관광"],
    "교육": ["아파트", "코스피", "나스닥", "항공권", "관광", "맛집"],
    "생활법률": ["맛집", "관광", "항공권", "코스피", "나스닥"],
    "환율": ["아파트", "청약", "맛집", "관광", "항공권", "호캉스"],
    "관세": ["아파트", "청약", "맛집", "관광", "코스피", "나스닥"],
    "주식 분석": ["여행", "관광", "항공권", "부동산", "아파트", "청약", "전세", "매매", "맛집"],
    "IT": ["아파트", "청약", "전세", "매매", "맛집", "관광", "항공권", "호캉스"],
    "취업": ["아파트", "청약", "전세", "코스피", "나스닥", "관광", "항공권", "맛집"],
}


_DOMAIN_KEYWORDS = {
    "부동산": ["부동산", "아파트", "청약", "전세", "매매", "리츠"],
    "주식": ["주식", "코스피", "코스닥", "증시", "나스닥", "S&P", "시황"],
    "주식 분석": ["주식", "코스피", "코스닥", "증시", "나스닥", "S&P", "시황"],
    "여행": ["여행", "관광", "호캉스", "항공권", "명소"],
    "생활금융": ["재테크", "저축", "금리", "생활금융"],
    "식생활": ["외식", "맛집", "요리", "식생활"],
    "건강": ["헬스케어", "메디컬", "건강"],
    "교육": ["에듀테크", "입시", "교육"],
    "생활법률": ["법률", "판례", "대법원"],
    "환율": ["환율", "달러", "엔화"],
    "관세": ["관세", "수출입", "무역"],
    "IT": ["AI", "반도체", "스마트폰", "IT", "클라우드", "사이버보안"],
    "취업": ["채용", "취업", "자격증", "구인", "이직", "면접"],
}

def _detect_domain(query: str) -> str:
    """검색 쿼리에서 도메인을 감지하여 제외 키워드 매핑."""
    for domain, keywords in _DOMAIN_KEYWORDS.items():
        for kw in keywords:
            if kw in query:
                return domain
    return ""


def _filter_by_domain(items: list[dict], domain: str, title_key: str = "title") -> list[dict]:
    """제외 키워드 기반으로 해당 도메인에 맞지 않는 결과를 필터링."""
    exclude_words = DOMAIN_EXCLUDE_KEYWORDS.get(domain, [])
    if not exclude_words:
        return items
    filtered = []
    for item in items:
        title = item.get(title_key, "")
        if not any(ew in title for ew in exclude_words):
            filtered.append(item)
    return filtered if filtered else items  # 필터 후 결과가 없으면 원본 유지


def _deduplicate_news(items: list[dict], title_key: str = "title") -> list[dict]:
    """제목 기반 중복 기사 제거. 정규화된 키워드 frozenset 해시로 O(n) 처리."""
    if not items:
        return items

    def _normalize_key(text: str) -> frozenset:
        text = _PUNCT_RE.sub("", text)
        words = sorted(text.split())
        # 주요 키워드(상위 5개)만 비교하여 유사 제목 그룹핑
        return frozenset(words[:5]) if len(words) > 5 else frozenset(words)

    seen: set[frozenset] = set()
    unique: list[dict] = []
    for item in items:
        title = item.get(title_key, "")
        key = _normalize_key(title)
        if not key:
            unique.append(item)
            continue
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique

# ── Local Fetching Logic (Fallback/Standalone) ──────────────────────────────

KOR_CITY_MAP = {
    # 국내 주요 도시
    "서울": "Seoul", "부산": "Busan", "대구": "Daegu", "인천": "Incheon",
    "광주": "Gwangju", "대전": "Daejeon", "울산": "Ulsan", "세종": "Sejong",
    "경기": "Gyeonggi-do", "강원": "Gangwon-do", "충북": "Chungcheongbuk-do",
    "충남": "Chungcheongnam-do", "전북": "Jeollabuk-do", "전남": "Jeollanam-do",
    "경북": "Gyeongsangbuk-do", "경남": "Gyeongsangnam-do", "제주": "Jeju",
    # 미국/캐나다
    "뉴욕": "New York", "뉴요크": "New York",
    "시카고": "Chicago", "로스앤젠레스": "Los Angeles", "엘얠": "Los Angeles",
    "새프란시스코": "San Francisco", "샜프란시스코": "San Francisco",
    "시애틀": "Seattle", "휴스턴": "Houston", "마이애미": "Miami",
    "미네아폴리스": "Minneapolis", "시애틀": "Seattle",
    "토론토": "Toronto", "밴쿠버": "Vancouver",
    # 유럽
    "맰던": "London", "파리": "Paris", "베를린": "Berlin",
    "로마": "Rome", "마드리드": "Madrid", "바르셈로나": "Barcelona",
    "암스테르담": "Amsterdam", "비엔나": "Vienna", "좤리히": "Zurich",
    "프라하": "Prague", "부눓페스트": "Budapest", "와르샤바": "Warsaw",
    # 아시아
    "도쿄": "Tokyo", "오사카": "Osaka", "교토": "Kyoto", "쯤응": "Chengdu",
    "베이징": "Beijing", "상하이": "Shanghai", "광저우": "Guangzhou",
    "싱가포르": "Singapore", "어슦달라럼푸르": "Kuala Lumpur",
    "방콕": "Bangkok", "호치민": "Ho Chi Minh", "하노이": "Hanoi",
    "자카르타": "Jakarta", "두바이": "Dubai", "아부다비": "Abu Dhabi",
    "이스탄불": "Istanbul", "토나카": "Ankara",
    # 오세아니아/남미
    "시드니": "Sydney", "멜바른": "Melbourne", "브리즈번": "Brisbane",
    "색파울루": "Sao Paulo", "리우데자네이로": "Rio de Janeiro",
    "부에노스아이레스": "Buenos Aires",
}

MOCK_COORD_MAP = {
    "Seoul": (37.5665, 126.9780),
    "Busan": (35.1796, 129.0756),
    "Jeju": (33.4996, 126.5312),
    "New York": (40.7128, -74.0060),
    "Chicago": (41.8781, -87.6298),
    "London": (51.5074, -0.1278),
    "Tokyo": (35.6762, 139.6503),
    "Osaka": (34.6937, 135.5023),
    "Paris": (48.8566, 2.3522),
    "Texas": (31.9686, -99.9018)
}

WMO_WEATHER_CODES = {
    0: ("맑음", "01d"), 1: ("대체로 맑음", "02d"), 2: ("구름 조금", "03d"), 3: ("흐림", "04d"),
    45: ("안개", "50d"), 48: ("짙은 안개", "50d"),
    51: ("이슬비", "09d"), 53: ("이슬비", "09d"), 55: ("강한 이슬비", "09d"),
    61: ("약한 비", "10d"), 63: ("비", "10d"), 65: ("강한 비", "10d"),
    71: ("약한 눈", "13d"), 73: ("눈", "13d"), 75: ("강한 눈", "13d"),
    77: ("싸락눈", "13d"), 80: ("소나기", "09d"), 81: ("소나기", "09d"), 82: ("강한 소나기", "09d"),
    85: ("눈보라", "13d"), 86: ("강한 눈보라", "13d"),
    95: ("뇌우", "11d"), 96: ("우박 뇌우", "11d"), 99: ("강한 우박 뇌우", "11d"),
}

# Geocoding for common cities (lat, lon)
CITY_COORDS = {
    "Seoul": (37.5665, 126.9780), "Busan": (35.1796, 129.0756),
    "Daegu": (35.8714, 128.6014), "Incheon": (37.4563, 126.7052),
    "Gwangju": (35.1595, 126.8526), "Daejeon": (36.3504, 127.3845),
    "Ulsan": (35.5384, 129.3114), "Sejong": (36.4800, 126.9252),
    "Jeju": (33.4996, 126.5312),
    "New York": (40.7128, -74.0060), "Chicago": (41.8781, -87.6298),
    "London": (51.5074, -0.1278), "Tokyo": (35.6762, 139.6503),
    "Osaka": (34.6937, 135.5023), "Paris": (48.8566, 2.3522),
    "Beijing": (39.9042, 116.4074), "Shanghai": (31.2304, 121.4737),
    "Singapore": (1.3521, 103.8198), "Sydney": (-33.8688, 151.2093),
    "Dubai": (25.2048, 55.2708), "Bangkok": (13.7563, 100.5018),
    "Ho Chi Minh": (10.8231, 106.6297), "Hanoi": (21.0285, 105.8542),
}


def _fetch_weather_open_meteo(city: str) -> Optional[dict]:
    """Fetch real-time weather from Open-Meteo (free, no API key)."""
    eng_city = KOR_CITY_MAP.get(city.strip(), city.strip())
    coords = CITY_COORDS.get(eng_city)
    if not coords:
        # Try geocoding API
        try:
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={eng_city}&count=1&language=en"
            gr = requests.get(geo_url, timeout=5)
            gr.raise_for_status()
            results = gr.json().get("results", [])
            if results:
                coords = (results[0]["latitude"], results[0]["longitude"])
        except Exception:
            coords = (37.5665, 126.9780)  # Default Seoul

    lat, lon = coords
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m"
        f"&timezone=auto"
    )
    try:
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        d = r.json()
        current = d.get("current", {})
        wmo_code = current.get("weather_code", 0)
        desc, icon = WMO_WEATHER_CODES.get(wmo_code, ("알 수 없음", "01d"))
        return {
            "city": city,
            "lat": lat,
            "lon": lon,
            "temp": current.get("temperature_2m", 0),
            "feels_like": current.get("apparent_temperature", 0),
            "humidity": current.get("relative_humidity_2m", 0),
            "desc": desc,
            "icon": icon,
            "wind_speed": current.get("wind_speed_10m", 0),
            "updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    except Exception:
        return None


def _fetch_weather_local(city: str, api_key: Optional[str]) -> dict:
    # 1. Try OpenWeatherMap if API key provided
    if api_key:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=kr"
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            d = r.json()
            return {
                "city": city,
                "lat": d["coord"]["lat"],
                "lon": d["coord"]["lon"],
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

    # 2. Try Open-Meteo (free, no key)
    result = _fetch_weather_open_meteo(city)
    if result:
        return result

    # 3. Final fallback — mock data
    eng_city = KOR_CITY_MAP.get(city.strip(), city.strip())
    mock_lat, mock_lon = CITY_COORDS.get(eng_city, (37.5665, 126.9780))

    return {
        "city": city, "lat": mock_lat, "lon": mock_lon, "temp": 0, "feels_like": 0, "humidity": 0,
        "desc": "데이터 없음", "icon": "01d", "wind_speed": 0,
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
        # User-Agent 헤더 추가 (HF Spaces에서 Google 차단 우회)
        _BROWSER_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        feed = feedparser.parse(url, request_headers={"User-Agent": _BROWSER_UA})
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
    """Fetch real-time traffic news via DDG news search."""
    try:
        if not _DDGS:
            return []
        with _DDGS() as ddgs:
            results = list(ddgs.news("고속도로 교통 도로 상황", region="kr-kr", max_results=8))
        items = []
        for r in results:
            title = _strip_html(r.get("title", ""))
            body = _strip_html(r.get("body", ""))
            if not title:
                continue
            # 기사 내용에서 교통 상태 키워드 감지
            text = title + " " + body
            status, color = "정보", "blue"
            for kw, st_val, clr in [
                ("원활", "원활", "green"), ("소통", "원활", "green"),
                ("서행", "서행", "orange"), ("혼잡", "혼잡", "orange"),
                ("지체", "지체", "orange"),
                ("정체", "정체", "red"), ("통제", "통제", "red"),
                ("사고", "사고", "red"),
            ]:
                if kw in text:
                    status, color = st_val, clr
                    break
            items.append({
                "title": title,
                "status": status,
                "color": color,
                "source": r.get("source", ""),
                "link": r.get("url", ""),
                "published": r.get("date", ""),
                "snippet": body[:120] if body else "",
            })
        if items:
            return _deduplicate_news(items, title_key="title")
    except Exception:
        pass
    return []

# ── API Calls (Backend) and Public Functions ───────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def fetch_weather(city: str = "Seoul", api_key: Optional[str] = None) -> dict:
    """Fetch weather data from API or fallback to local execution."""
    eng_city = KOR_CITY_MAP.get(city.strip(), city.strip())
    
    if IS_API_MODE:
        try:
            params = {"city": eng_city}
            if api_key:
                params["api_key"] = api_key
            r = requests.get(f"{API_BASE_URL}/data/weather", params=params, timeout=5)
            r.raise_for_status()
            return r.json()
        except Exception:
            pass  # Fallback to local on API failure
    return _fetch_weather_local(eng_city, api_key)

_NEWS_CAT_QUERY = {
    "종합": "오늘 뉴스 주요 속보",
    "IT/과학": "IT 과학 기술 뉴스",
    "경제": "경제 금융 주식 뉴스",
    "생활": "생활 사회 뉴스",
}

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_news(category: str = "종합", limit: int = 10) -> list[dict]:
    """Fetch news: DDG (1순위, HF 안정) → Google RSS (2순위) → RSS 검색 (3순위)."""
    if IS_API_MODE:
        try:
            r = requests.get(f"{API_BASE_URL}/data/news", params={"category": category, "limit": limit}, timeout=5)
            r.raise_for_status()
            news = r.json().get("news", [])
            if news:
                return _deduplicate_news(news)
        except Exception:
            pass

    # 1순위: DDG 뉴스 (HF Spaces에서 가장 안정적)
    query = _NEWS_CAT_QUERY.get(category, "오늘 주요 뉴스")
    result = _fetch_news_ddg(query, limit=limit)

    # 2순위: Google News RSS (User-Agent 포함)
    if not result:
        result = _fetch_news_local(category, limit)

    # 3순위: Google RSS 검색
    if not result:
        result = _fetch_news_rss(query, limit=limit)

    return _deduplicate_news(result)

@st.cache_data(ttl=1800, show_spinner=False)
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

def _strip_html(text: str) -> str:
    """Remove HTML tags and decode entities from text."""
    if not text:
        return ""
    from html import unescape
    clean = re.sub(r"<[^>]+>", " ", text)
    clean = unescape(clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def _is_similar(text1: str, text2: str, threshold: float = 0.6) -> bool:
    """Check if two texts are too similar by word overlap."""
    if not text1 or not text2:
        return False
    w1 = set(re.sub(r"[^\w\s]", "", text1).split())
    w2 = set(re.sub(r"[^\w\s]", "", text2).split())
    if not w1 or not w2:
        return False
    overlap = len(w1 & w2)
    return overlap / min(len(w1), len(w2)) >= threshold


def _fetch_news_ddg(query: str, limit: int = 10, timelimit: str = "w") -> list[dict]:
    """Fetch news via DuckDuckGo — provides real article snippets.

    Args:
        timelimit: "d" (1일), "w" (1주), "m" (1개월)
    """
    try:
        if not _DDGS:
            return []
        with _DDGS() as ddgs:
            results = list(ddgs.news(query, region="kr-kr", timelimit=timelimit, max_results=limit))
        items = []
        for r in results:
            title = _strip_html(r.get("title", ""))
            body = _strip_html(r.get("body", ""))
            # Ensure snippet is genuinely different from title
            if body and not _is_similar(body, title):
                snippet = body[:200]
            else:
                snippet = ""
            items.append({
                "title": title,
                "link": r.get("url", r.get("link", "")),
                "source": r.get("source", ""),
                "published": r.get("date", ""),
                "snippet": snippet,
            })
        return items
    except Exception:
        return []


def _fetch_news_rss(query: str, limit: int = 10) -> list[dict]:
    """Fallback: search news via Google News RSS (최근 7일)."""
    import urllib.parse
    encoded = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded}+when:7d&hl=ko&gl=KR&ceid=KR:ko"
    try:
        _BROWSER_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        feed = feedparser.parse(url, request_headers={"User-Agent": _BROWSER_UA})
        items = []
        for entry in feed.entries[:limit]:
            raw_title = _strip_html(entry.get("title", ""))
            raw_summary = _strip_html(entry.get("summary", "") or "")[:200]
            # Google News RSS summary often equals title — word-overlap check
            if raw_summary and not _is_similar(raw_summary, raw_title):
                snippet = raw_summary
            else:
                snippet = ""
            if snippet.startswith("http") or len(snippet) < 10:
                snippet = ""
            items.append({
                "title": raw_title,
                "link": entry.get("link", ""),
                "source": entry.get("source", {}).get("title", ""),
                "published": entry.get("published", ""),
                "snippet": snippet,
            })
        return items
    except Exception:
        return []


def _fetch_web_ddg(query: str, limit: int = 10) -> list[dict]:
    """Fetch web results via DuckDuckGo — provides real snippets."""
    try:
        if not _DDGS:
            return []
        with _DDGS() as ddgs:
            results = list(ddgs.text(query, region="kr-kr", max_results=limit))
        items = []
        for r in results:
            title = _strip_html(r.get("title", ""))
            body = _strip_html(r.get("body", ""))
            if body and not _is_similar(body, title):
                snippet = body[:200]
            else:
                snippet = ""
            items.append({
                "title": title,
                "link": r.get("href", r.get("link", "")),
                "source": "",
                "snippet": snippet,
            })
        return items
    except Exception:
        return []


@st.cache_data(ttl=900, show_spinner=False)
def fetch_web_search(query: str, limit: int = 10) -> list[dict]:
    """Fetch web search results. DuckDuckGo first, then RSS fallback."""
    results = []
    if IS_API_MODE:
        try:
            r = requests.get(f"{API_BASE_URL}/data/search/web", params={"query": query, "limit": limit}, timeout=5)
            r.raise_for_status()
            results = r.json().get("results", [])
        except Exception:
            pass
    if not results:
        results = _fetch_web_ddg(query, limit=limit)
    if not results:
        results = _fetch_news_rss(query, limit=limit)
    domain = _detect_domain(query)
    results = _filter_by_domain(results, domain, title_key="title")
    results = _deduplicate_news(results, title_key="title")
    return results

@st.cache_data(ttl=300, show_spinner=False)
def fetch_exchange_rates() -> dict:
    """Fetch real-time exchange rates from open.er-api.com (free, no key)."""
    try:
        r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=8)
        r.raise_for_status()
        data = r.json()
        return {
            "rates": data.get("rates", {}),
            "updated": data.get("time_last_update_utc", ""),
            "ok": True,
        }
    except Exception as e:
        return {"rates": {}, "updated": str(e), "ok": False}


@st.cache_data(ttl=300, show_spinner=False)
def fetch_kr_index(code: str = "KOSPI") -> dict:
    """네이버 금융 API로 한국 지수(KOSPI/KOSDAQ) 실시간 데이터 조회."""
    try:
        url = f"https://m.stock.naver.com/api/index/{code}/basic"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
        r.raise_for_status()
        d = r.json()
        price = float(d.get("closePrice", "0").replace(",", ""))
        change = float(d.get("compareToPreviousClosePrice", "0").replace(",", ""))
        change_pct = float(d.get("fluctuationsRatio", "0").replace(",", ""))
        return {
            "name": code, "symbol": code,
            "price": round(price, 2),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "high": price, "low": price, "volume": 0,
            "history": [], "ok": True,
            "updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    except Exception:
        return {"symbol": code, "ok": False}


@st.cache_data(ttl=300, show_spinner=False)
def fetch_stock_data(symbol: str, period: str = "5d") -> dict:
    """Fetch stock/index data via yfinance (free, no key).
    Returns: {name, symbol, price, change, change_pct, history, ok}
    """
    import math
    if not _yf:
        return {"symbol": symbol, "ok": False, "error": "yfinance not installed"}
    for attempt in range(2):
        try:
            ticker = _yf.Ticker(symbol)
            hist = ticker.history(period=period)
            # NaN 행 완전 제거 (Close 기준)
            if "Close" in hist.columns:
                hist = hist[hist["Close"].notna() & hist["Close"].apply(lambda x: not math.isnan(x) if isinstance(x, float) else True)]
            # NaN 잔여 컬럼도 정리
            for col in ["High", "Low", "Volume"]:
                if col in hist.columns:
                    hist[col] = hist[col].fillna(0)
            if hist.empty:
                if attempt == 0:
                    continue
                return {"symbol": symbol, "ok": False}
            last_close = float(hist["Close"].iloc[-1])
            if math.isnan(last_close):
                if attempt == 0:
                    continue
                return {"symbol": symbol, "ok": False}
            prev_close = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else last_close
            if math.isnan(prev_close):
                prev_close = last_close
            change = last_close - prev_close
            change_pct = (change / prev_close * 100) if prev_close else 0
            hist_records = []
            for dt, row in hist.iterrows():
                vol = row.get("Volume", 0)
                hist_records.append({
                    "Date": dt.strftime("%m-%d"),
                    "Close": round(float(row["Close"]), 2),
                    "Volume": int(vol) if vol else 0,
                })
            high_val = round(float(hist["High"].max()), 2) if "High" in hist.columns and not hist["High"].isna().all() else last_close
            low_val = round(float(hist["Low"].min()), 2) if "Low" in hist.columns and not hist["Low"].isna().all() else last_close
            last_vol = hist["Volume"].iloc[-1] if "Volume" in hist.columns else 0
            return {
                "name": symbol,
                "symbol": symbol,
                "price": round(last_close, 2),
                "prev_close": round(prev_close, 2),
                "change": round(change, 2),
                "change_pct": round(change_pct, 2),
                "high": high_val,
                "low": low_val,
                "volume": int(last_vol) if last_vol else 0,
                "history": hist_records,
                "updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "ok": True,
            }
        except Exception as e:
            if attempt == 0:
                continue  # sleep 제거 — 즉시 재시도
            return {"symbol": symbol, "ok": False, "error": str(e)}
    return {"symbol": symbol, "ok": False}


# ── YouTube 검색: YouTube 페이지 파싱 → RSS → DDG (3단계) ─────────────────
import json as _json

def _yt_parse_item(vid_id: str, title: str, uploader: str, pub_str: str,
                   view_count, duration_str: str, desc: str) -> dict:
    """Build a standard video dict."""
    return {
        "title": title,
        "url": f"https://www.youtube.com/watch?v={vid_id}",
        "embed_url": f"https://www.youtube.com/embed/{vid_id}",
        "thumbnail": f"https://img.youtube.com/vi/{vid_id}/mqdefault.jpg",
        "vid_id": vid_id,
        "duration": duration_str,
        "uploader": uploader,
        "published": pub_str,
        "view_count": str(view_count) if view_count else "",
        "description": desc[:200] if desc else "",
    }


def _yt_search_scrape(query: str, limit: int, sort_by_date: bool = False) -> list[dict]:
    """Search YouTube by scraping search page — same results as browser.

    Args:
        sort_by_date: True → sort by upload date (sp=CAI%3D)
    """
    import urllib.parse
    # sp=CAI%3D means sort by upload date on YouTube
    sp = "&sp=CAI%3D" if sort_by_date else ""
    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}{sp}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return []
    except Exception:
        return []

    # ytInitialData JSON 추출
    text = resp.text
    items = []

    # 방법1: var ytInitialData = {...};
    match = re.search(r'var\s+ytInitialData\s*=\s*(\{.+?\});\s*</script>', text, re.DOTALL)
    if not match:
        # 방법2: window["ytInitialData"] = {...};
        match = re.search(r'window\["ytInitialData"\]\s*=\s*(\{.+?\});\s*</script>', text, re.DOTALL)
    if not match:
        return []

    try:
        data = _json.loads(match.group(1))
    except Exception:
        return []

    # JSON 구조 탐색: 검색 결과 videoRenderer 추출
    try:
        contents = (data.get("contents", {})
                    .get("twoColumnSearchResultsRenderer", {})
                    .get("primaryContents", {})
                    .get("sectionListRenderer", {})
                    .get("contents", []))
    except Exception:
        return []

    for section in contents:
        item_section = section.get("itemSectionRenderer", {})
        for item in item_section.get("contents", []):
            vr = item.get("videoRenderer")
            if not vr:
                continue
            vid_id = vr.get("videoId", "")
            if not vid_id:
                continue
            # 제목
            title = ""
            title_runs = vr.get("title", {}).get("runs", [])
            if title_runs:
                title = title_runs[0].get("text", "")
            # 업로더
            uploader = ""
            ch_runs = vr.get("ownerText", {}).get("runs", [])
            if ch_runs:
                uploader = ch_runs[0].get("text", "")
            # 게시일 (상대적: "13일 전", "1개월 전" 등)
            pub_text = vr.get("publishedTimeText", {}).get("simpleText", "")
            pub_str = _yt_relative_to_date(pub_text)
            # 조회수
            vc_text = vr.get("viewCountText", {}).get("simpleText", "")
            vc = re.sub(r"[^\d]", "", vc_text)
            # 길이
            dur_text = vr.get("lengthText", {}).get("simpleText", "")
            # 설명
            desc_parts = vr.get("detailedMetadataSnippets", [{}])
            desc = ""
            if desc_parts:
                snippet_runs = desc_parts[0].get("snippetText", {}).get("runs", [])
                desc = "".join(r.get("text", "") for r in snippet_runs)

            items.append(_yt_parse_item(vid_id, title, uploader, pub_str, vc, dur_text, desc))
            if len(items) >= limit:
                break
        if len(items) >= limit:
            break

    return items


def _yt_relative_to_date(text: str) -> str:
    """Convert YouTube relative time ('13일 전', '1개월 전') to ISO date string."""
    if not text:
        return ""
    now = datetime.datetime.now()
    try:
        # 숫자 추출
        nums = re.findall(r"\d+", text)
        n = int(nums[0]) if nums else 0
        if "초" in text or "second" in text:
            dt = now - datetime.timedelta(seconds=n)
        elif "분" in text or "minute" in text:
            dt = now - datetime.timedelta(minutes=n)
        elif "시간" in text or "hour" in text:
            dt = now - datetime.timedelta(hours=n)
        elif "일" in text or "day" in text:
            dt = now - datetime.timedelta(days=n)
        elif "주" in text or "week" in text:
            dt = now - datetime.timedelta(weeks=n)
        elif "개월" in text or "month" in text:
            dt = now - datetime.timedelta(days=n * 30)
        elif "년" in text or "year" in text:
            dt = now - datetime.timedelta(days=n * 365)
        else:
            return ""
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    except Exception:
        return ""


def _yt_search_rss(query: str, limit: int) -> list[dict]:
    """Fetch latest videos from YouTube channel RSS feeds matching query keywords."""
    _YT_CHANNELS = {
        "뉴스": [
            ("UCcQTRi69dsVYHN3exePtZ1A", "KBS News"),
            ("UCF4Wxdo3inmxP-Y59wXDsFw", "MBC News"),
            ("UCkinYTS9IHqOEwR1Ane-6UA", "SBS News"),
            ("UChlgI3UHCOnwUGzWzbJ3H5w", "YTN"),
            ("UCsU-I-vHLiaMfQ_5iBYLMoQ", "JTBC News"),
        ],
        "날씨": [
            ("UCcQTRi69dsVYHN3exePtZ1A", "KBS News"),
            ("UCF4Wxdo3inmxP-Y59wXDsFw", "MBC News"),
            ("UCkinYTS9IHqOEwR1Ane-6UA", "SBS News"),
            ("UChlgI3UHCOnwUGzWzbJ3H5w", "YTN"),
        ],
        "경제": [
            ("UC0MhDBzy_MuJVMfxQf0d5lg", "한국경제TV"),
            ("UCTkbUcCVnMmBOhBDNUBaZXg", "머니투데이방송"),
            ("UCsU-I-vHLiaMfQ_5iBYLMoQ", "JTBC News"),
            ("UChlgI3UHCOnwUGzWzbJ3H5w", "YTN"),
        ],
    }
    _CHANNEL_KEYWORDS = {
        "날씨": "날씨", "기상": "날씨", "예보": "날씨", "일기예보": "날씨",
        "뉴스": "뉴스", "시사": "뉴스", "속보": "뉴스", "이슈": "뉴스",
        "경제": "경제", "주식": "경제", "금융": "경제", "환율": "경제",
        "금리": "경제", "유가": "경제", "부동산": "경제", "관세": "경제",
    }

    matched_channels = set()
    query_lower = query.lower()
    for kw, cat in _CHANNEL_KEYWORDS.items():
        if kw in query_lower:
            for ch in _YT_CHANNELS.get(cat, []):
                matched_channels.add(ch)
    if not matched_channels:
        return []

    items = []
    query_words = set(re.findall(r"[가-힣]{2,}", query))
    for channel_id, channel_name in matched_channels:
        try:
            feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:8]:
                title = entry.get("title", "")
                title_words = set(re.findall(r"[가-힣]{2,}", title))
                # 키워드 일치 체크를 완화: 채널이 3개 초과일 때만 필터링
                if not query_words.intersection(title_words) and len(matched_channels) > 3:
                    continue
                vid_url = entry.get("link", "")
                vid_id = vid_url.split("watch?v=")[-1].split("&")[0] if "watch?v=" in vid_url else ""
                if not vid_id:
                    continue
                pub_str = ""
                if entry.get("published"):
                    try:
                        from dateutil import parser as _dp
                        pub_str = _dp.parse(entry["published"]).strftime("%Y-%m-%dT%H:%M:%S")
                    except Exception:
                        pub_str = entry.get("published", "")[:19]
                items.append(_yt_parse_item(vid_id, title, channel_name, pub_str, "", "", entry.get("summary", "")))
        except Exception:
            continue

    items.sort(key=lambda v: v.get("published", ""), reverse=True)
    seen = set()
    return [it for it in items if not (it["vid_id"] in seen or seen.add(it["vid_id"]))][:limit]


def _yt_search_ddg(query: str, limit: int, youtube_only: bool = False,
                    timelimit: str | None = None) -> list[dict]:
    """DDG videos search — includes YouTube + Naver TV + Kakao etc.

    Args:
        timelimit: "d" (day), "w" (week), "m" (month), None (all time)
    """
    if not _DDGS:
        return []
    results = []
    # 시간 범위를 점진적으로 넓혀가며 검색 (d → w → m → None)
    _time_order = []
    if timelimit == "d":
        _time_order = ["d", "w", "m", None]
    elif timelimit == "w":
        _time_order = ["w", "m", None]
    elif timelimit == "m":
        _time_order = ["m", None]
    else:
        _time_order = [None]

    for tl in _time_order:
        try:
            with _DDGS() as ddgs:
                kwargs = {"region": "kr-kr", "max_results": limit + 10}
                if tl:
                    kwargs["timelimit"] = tl
                results = list(ddgs.videos(query, **kwargs))
            if len(results) >= 3:
                break
        except Exception:
            continue
    if not results:
        return []
    items = []
    for r in results:
        url = r.get("content", "")
        if not url:
            continue
        # YouTube 전용 모드가 아니면 모든 영상 플랫폼 허용
        if youtube_only and "youtube.com" not in url and "youtu.be" not in url:
            continue
        title = _strip_html(r.get("title", ""))
        desc = _strip_html(r.get("description", ""))
        vid_id = ""
        thumbnail = r.get("thumbnail", "") or ""
        if "watch?v=" in url:
            vid_id = url.split("watch?v=")[-1].split("&")[0]
        elif "youtu.be/" in url:
            vid_id = url.split("youtu.be/")[-1].split("?")[0]
        # YouTube가 아닌 플랫폼도 처리
        if vid_id:
            thumbnail = f"https://img.youtube.com/vi/{vid_id}/mqdefault.jpg"
        # 플랫폼 표시
        platform = ""
        if "youtube.com" in url or "youtu.be" in url:
            platform = "YouTube"
        elif "naver.com" in url or "tv.naver" in url:
            platform = "Naver TV"
        elif "kakao" in url or "daum.net" in url:
            platform = "Kakao"
        elif "tiktok.com" in url:
            platform = "TikTok"
        elif "twitter.com" in url or "x.com" in url:
            platform = "X"
        elif "instagram.com" in url:
            platform = "Instagram"
        elif "facebook.com" in url or "fb.watch" in url:
            platform = "Facebook"
        elif "vimeo.com" in url:
            platform = "Vimeo"
        stats = r.get("statistics", {}) or {}
        item = {
            "title": title,
            "url": url,
            "embed_url": f"https://www.youtube.com/embed/{vid_id}" if vid_id else "",
            "thumbnail": thumbnail,
            "vid_id": vid_id,
            "duration": r.get("duration", ""),
            "uploader": r.get("uploader", ""),
            "published": r.get("published", ""),
            "view_count": str(stats.get("viewCount", "")),
            "description": desc[:200] if desc else "",
            "platform": platform,
        }
        items.append(item)
        if len(items) >= limit:
            break
    return items


@st.cache_data(ttl=900, show_spinner=False)
def fetch_youtube_search(query: str, limit: int = 12, timelimit: str | None = None) -> list[dict]:
    """Fetch YouTube videos: YouTube 페이지 파싱 → RSS → DDG (3단계).

    Args:
        timelimit: "d"/"w"/"m"/None — when set, YouTube search sorts by upload date.
    """
    sort_by_date = timelimit is not None
    domain = _detect_domain(query)
    all_items = []
    existing_ids = set()

    def _merge(new_items):
        for it in new_items:
            vid = it.get("vid_id", "")
            url = it.get("url", "")
            key = vid or url
            if key and key not in existing_ids:
                all_items.append(it)
                existing_ids.add(key)

    # 1차: YouTube 검색 페이지 직접 파싱
    try:
        _merge(_yt_search_scrape(query, limit, sort_by_date=sort_by_date))
    except Exception:
        pass

    # 2차: YouTube 채널 RSS — 항상 시도
    try:
        _merge(_yt_search_rss(query, limit))
    except Exception:
        pass

    # 3차: DDG videos — 항상 시도 (다양한 플랫폼 + 최신 영상 보강)
    try:
        _merge(_yt_search_ddg(query, limit, timelimit=timelimit))
    except Exception:
        pass

    if all_items:
        filtered = _filter_by_domain(all_items, domain, title_key="title")
        if sort_by_date:
            filtered.sort(key=lambda v: v.get("published", ""), reverse=True)
        return filtered[:limit]

    return []


@st.cache_data(ttl=900, show_spinner=False)
def fetch_news_search(query: str, limit: int = 10) -> list[dict]:
    """Fetch news search results. DuckDuckGo first (better snippets), then RSS fallback."""
    news = []
    if IS_API_MODE:
        try:
            r = requests.get(f"{API_BASE_URL}/data/search/news", params={"query": query, "limit": limit}, timeout=5)
            r.raise_for_status()
            news = r.json().get("news", [])
        except Exception:
            pass
    if not news:
        news = _fetch_news_ddg(query, limit=limit)
    if not news:
        news = _fetch_news_rss(query, limit=limit)
    domain = _detect_domain(query)
    news = _filter_by_domain(news, domain, title_key="title")
    news = _deduplicate_news(news, title_key="title")
    return news
