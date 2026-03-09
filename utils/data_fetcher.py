"""Data fetchers for weather, news, and traffic information.
Supports dual-mode: API (FastAPI backend) and Standalone (Local fetching)."""
import requests
import datetime
import feedparser
import re
from typing import Optional
import streamlit as st
from utils.config import IS_API_MODE, API_BASE_URL

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
}


def _detect_domain(query: str) -> str:
    """검색 쿼리에서 도메인을 감지하여 제외 키워드 매핑."""
    domain_keywords = {
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
    }
    for domain, keywords in domain_keywords.items():
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
    """제목 유사도 기반 중복 기사 제거. 정규화 후 80% 이상 겹치면 중복 처리."""
    if not items:
        return items

    def _normalize(text: str) -> set:
        text = re.sub(r"[^\w\s]", "", text)
        return set(text.split())

    seen: list[set] = []
    unique: list[dict] = []
    for item in items:
        title = item.get(title_key, "")
        words = _normalize(title)
        if not words:
            unique.append(item)
            continue
        is_dup = False
        for prev_words in seen:
            if not prev_words:
                continue
            overlap = len(words & prev_words) / min(len(words), len(prev_words))
            if overlap >= 0.8:
                is_dup = True
                break
        if not is_dup:
            seen.append(words)
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

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_news(category: str = "종합", limit: int = 10) -> list[dict]:
    """Fetch news data from API or fallback to local execution."""
    if IS_API_MODE:
        try:
            r = requests.get(f"{API_BASE_URL}/data/news", params={"category": category, "limit": limit}, timeout=5)
            r.raise_for_status()
            news = r.json().get("news", [])
            return _deduplicate_news(news)
        except Exception:
            pass
    result = _fetch_news_local(category, limit)
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


def _fetch_news_ddg(query: str, limit: int = 10) -> list[dict]:
    """Fetch news via DuckDuckGo — provides real article snippets."""
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.news(query, region="kr-kr", max_results=limit))
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
    """Fallback: search news via Google News RSS."""
    import urllib.parse
    encoded = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=ko&gl=KR&ceid=KR:ko"
    try:
        feed = feedparser.parse(url)
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
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
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
def fetch_stock_data(symbol: str, period: str = "5d") -> dict:
    """Fetch stock/index data via yfinance (free, no key).
    Returns: {name, symbol, price, change, change_pct, history_df, ok}
    """
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        if hist.empty:
            return {"symbol": symbol, "ok": False}
        info = ticker.info or {}
        last_close = float(hist["Close"].iloc[-1])
        prev_close = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else last_close
        change = last_close - prev_close
        change_pct = (change / prev_close * 100) if prev_close else 0
        # Build a simple history dataframe
        hist_records = []
        for dt, row in hist.iterrows():
            hist_records.append({
                "Date": dt.strftime("%m-%d"),
                "Close": round(float(row["Close"]), 2),
                "Volume": int(row["Volume"]) if row["Volume"] else 0,
            })
        return {
            "name": info.get("shortName", info.get("longName", symbol)),
            "symbol": symbol,
            "price": round(last_close, 2),
            "prev_close": round(prev_close, 2),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "high": round(float(hist["High"].max()), 2),
            "low": round(float(hist["Low"].min()), 2),
            "volume": int(hist["Volume"].iloc[-1]) if hist["Volume"].iloc[-1] else 0,
            "history": hist_records,
            "updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "ok": True,
        }
    except Exception as e:
        return {"symbol": symbol, "ok": False, "error": str(e)}


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_youtube_search(query: str, limit: int = 5) -> list[dict]:
    """Fetch YouTube videos via DuckDuckGo videos search (no API key)."""
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.videos(query, region="kr-kr", max_results=limit + 3))
        items = []
        for r in results:
            url = r.get("content", "")
            # Only keep YouTube videos
            if "youtube.com" not in url and "youtu.be" not in url:
                continue
            title = _strip_html(r.get("title", ""))
            desc = _strip_html(r.get("description", ""))
            # Extract video ID for embed/thumbnail
            vid_id = ""
            if "watch?v=" in url:
                vid_id = url.split("watch?v=")[-1].split("&")[0]
            elif "youtu.be/" in url:
                vid_id = url.split("youtu.be/")[-1].split("?")[0]
            embed_url = f"https://www.youtube.com/embed/{vid_id}" if vid_id else ""
            thumbnail = f"https://img.youtube.com/vi/{vid_id}/mqdefault.jpg" if vid_id else ""
            stats = r.get("statistics", {}) or {}
            items.append({
                "title": title,
                "url": url,
                "embed_url": embed_url,
                "thumbnail": thumbnail,
                "vid_id": vid_id,
                "duration": r.get("duration", ""),
                "uploader": r.get("uploader", ""),
                "published": r.get("published", ""),
                "view_count": stats.get("viewCount", ""),
                "description": desc[:200] if desc else "",
            })
            if len(items) >= limit:
                break
        domain = _detect_domain(query)
        items = _filter_by_domain(items, domain, title_key="title")
        return items
    except Exception:
        return []


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
