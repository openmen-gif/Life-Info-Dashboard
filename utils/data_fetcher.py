"""Data fetchers for weather, news, and traffic information.
Supports dual-mode: API (FastAPI backend) and Standalone (Local fetching)."""
import socket
# [주석] feedparser, urllib 등 내부 타임아웃 제어가 불가능한 라이브러리의 무한 락을 예방하고자 
#        모든 소켓 네트워크 연결에 3초 타임아웃을 전역 강제합니다.
socket.setdefaulttimeout(3.0)

import requests
import datetime
import feedparser
import re
from typing import Optional
import streamlit as st
from utils.config import (
    IS_API_MODE, API_BASE_URL, NAVER_CLIENT_ID, NAVER_CLIENT_SECRET, HAS_NAVER,
    OPENWEATHER_API_KEY, YOUTUBE_API_KEY, HAS_YOUTUBE_API,
)

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
    # 광역시·도
    "서울": "Seoul", "부산": "Busan", "대구": "Daegu", "인천": "Incheon",
    "광주": "Gwangju", "대전": "Daejeon", "울산": "Ulsan", "세종": "Sejong",
    "경기": "Gyeonggi-do", "강원": "Gangwon-do", "충북": "Chungcheongbuk-do",
    "충남": "Chungcheongnam-do", "전북": "Jeollabuk-do", "전남": "Jeollanam-do",
    "경북": "Gyeongsangbuk-do", "경남": "Gyeongsangnam-do", "제주": "Jeju",
    # 경기/강원 주요 시
    "수원": "Suwon", "성남": "Seongnam", "용인": "Yongin", "고양": "Goyang",
    "부천": "Bucheon", "안산": "Ansan", "안양": "Anyang", "남양주": "Namyangju",
    "화성": "Hwaseong", "평택": "Pyeongtaek", "의정부": "Uijeongbu",
    "시흥": "Siheung", "파주": "Paju", "김포": "Gimpo", "광명": "Gwangmyeong",
    "이천": "Icheon", "양주": "Yangju", "오산": "Osan", "구리": "Guri",
    "안성": "Anseong", "포천": "Pocheon", "하남": "Hanam", "여주": "Yeoju",
    "춘천": "Chuncheon", "원주": "Wonju", "강릉": "Gangneung", "동해": "Donghae",
    "속초": "Sokcho", "삼척": "Samcheok", "태백": "Taebaek",
    # 충청 주요 시
    "청주": "Cheongju", "충주": "Chungju", "제천": "Jecheon",
    "천안": "Cheonan", "아산": "Asan", "공주": "Gongju", "보령": "Boryeong",
    "서산": "Seosan", "논산": "Nonsan", "당진": "Dangjin",
    # 전라 주요 시
    "전주": "Jeonju", "익산": "Iksan", "군산": "Gunsan", "정읍": "Jeongeup",
    "남원": "Namwon", "김제": "Gimje",
    "목포": "Mokpo", "여수": "Yeosu", "순천": "Suncheon", "나주": "Naju",
    "광양": "Gwangyang",
    # 경상 주요 시 (창원 포함)
    "창원": "Changwon", "진주": "Jinju", "통영": "Tongyeong", "사천": "Sacheon",
    "김해": "Gimhae", "양산": "Yangsan", "거제": "Geoje", "밀양": "Miryang",
    "포항": "Pohang", "경주": "Gyeongju", "구미": "Gumi", "안동": "Andong",
    "영주": "Yeongju", "경산": "Gyeongsan", "상주": "Sangju", "문경": "Mungyeong",
    "김천": "Gimcheon",
    # 제주
    "제주시": "Jeju", "서귀포": "Seogwipo",
    # ── 미국 ──
    "뉴욕": "New York", "엘에이": "Los Angeles", "로스앤젤레스": "Los Angeles",
    "시카고": "Chicago", "샌프란시스코": "San Francisco", "시애틀": "Seattle",
    "휴스턴": "Houston", "마이애미": "Miami", "보스턴": "Boston",
    "워싱턴": "Washington", "라스베이거스": "Las Vegas", "댈러스": "Dallas",
    "필라델피아": "Philadelphia", "애틀랜타": "Atlanta", "디트로이트": "Detroit",
    "미니애폴리스": "Minneapolis", "올랜도": "Orlando", "샌디에이고": "San Diego",
    "호놀룰루": "Honolulu", "앵커리지": "Anchorage", "피닉스": "Phoenix",
    "덴버": "Denver", "포틀랜드": "Portland", "솔트레이크시티": "Salt Lake City",
    "오스틴": "Austin", "샌안토니오": "San Antonio", "내슈빌": "Nashville",
    "뉴올리언스": "New Orleans", "샬럿": "Charlotte", "콜럼버스": "Columbus",
    "인디애나폴리스": "Indianapolis", "신시내티": "Cincinnati", "클리블랜드": "Cleveland",
    "피츠버그": "Pittsburgh", "밀워키": "Milwaukee", "캔자스시티": "Kansas City",
    "세인트루이스": "St. Louis", "탬파": "Tampa", "잭슨빌": "Jacksonville",
    "멤피스": "Memphis", "버펄로": "Buffalo", "새크라멘토": "Sacramento",
    "투손": "Tucson", "앨버커키": "Albuquerque", "오마하": "Omaha",
    # ── 캐나다 ──
    "토론토": "Toronto", "밴쿠버": "Vancouver", "몬트리올": "Montreal",
    "오타와": "Ottawa", "캘거리": "Calgary", "에드먼턴": "Edmonton",
    "퀘벡": "Quebec City", "위니펙": "Winnipeg", "핼리팩스": "Halifax",
    # ── 중남미 ──
    "멕시코시티": "Mexico City", "과달라하라": "Guadalajara", "몬테레이": "Monterrey",
    "칸쿤": "Cancun", "티후아나": "Tijuana",
    "아바나": "Havana", "파나마시티": "Panama City", "산호세": "San Jose",
    "과테말라시티": "Guatemala City",
    "리마": "Lima", "산티아고": "Santiago", "보고타": "Bogota",
    "카라카스": "Caracas", "키토": "Quito", "라파스": "La Paz",
    "아순시온": "Asuncion", "몬테비데오": "Montevideo", "메데인": "Medellin",
    "상파울루": "Sao Paulo", "리우데자네이루": "Rio de Janeiro",
    "브라질리아": "Brasilia", "살바도르": "Salvador", "포르탈레자": "Fortaleza",
    "벨루오리존치": "Belo Horizonte", "쿠리치바": "Curitiba",
    "부에노스아이레스": "Buenos Aires", "코르도바": "Cordoba",
    # ── 유럽 (서유럽) ──
    "런던": "London", "에든버러": "Edinburgh", "맨체스터": "Manchester",
    "버밍엄": "Birmingham", "리버풀": "Liverpool", "글래스고": "Glasgow",
    "더블린": "Dublin", "리스본": "Lisbon", "포르투": "Porto",
    "파리": "Paris", "리옹": "Lyon", "마르세유": "Marseille",
    "니스": "Nice", "보르도": "Bordeaux", "툴루즈": "Toulouse",
    "스트라스부르": "Strasbourg",
    "베를린": "Berlin", "뮌헨": "Munich", "프랑크푸르트": "Frankfurt",
    "함부르크": "Hamburg", "쾰른": "Cologne", "뒤셀도르프": "Dusseldorf",
    "슈투트가르트": "Stuttgart", "라이프치히": "Leipzig", "드레스덴": "Dresden",
    "로마": "Rome", "밀라노": "Milan", "베니스": "Venice", "베네치아": "Venice",
    "피렌체": "Florence", "나폴리": "Naples", "토리노": "Turin",
    "볼로냐": "Bologna", "팔레르모": "Palermo",
    "마드리드": "Madrid", "바르셀로나": "Barcelona", "세비야": "Seville",
    "발렌시아": "Valencia", "빌바오": "Bilbao", "그라나다": "Granada",
    "암스테르담": "Amsterdam", "로테르담": "Rotterdam", "헤이그": "The Hague",
    "위트레흐트": "Utrecht",
    "브뤼셀": "Brussels", "안트베르펜": "Antwerp", "브뤼헤": "Bruges",
    "비엔나": "Vienna", "잘츠부르크": "Salzburg", "그라츠": "Graz",
    "인스브루크": "Innsbruck",
    "취리히": "Zurich", "제네바": "Geneva", "베른": "Bern",
    "바젤": "Basel", "루체른": "Lucerne", "로잔": "Lausanne",
    # ── 유럽 (북유럽) ──
    "스톡홀름": "Stockholm", "예테보리": "Gothenburg", "오슬로": "Oslo",
    "베르겐": "Bergen", "코펜하겐": "Copenhagen", "헬싱키": "Helsinki",
    "레이캬비크": "Reykjavik",
    # ── 유럽 (동유럽) ──
    "프라하": "Prague", "부다페스트": "Budapest", "바르샤바": "Warsaw",
    "크라쿠프": "Krakow", "그단스크": "Gdansk", "브로츠와프": "Wroclaw",
    "브라티슬라바": "Bratislava", "류블랴나": "Ljubljana", "자그레브": "Zagreb",
    "소피아": "Sofia", "부쿠레슈티": "Bucharest", "베오그라드": "Belgrade",
    "키이우": "Kyiv", "키예프": "Kyiv",
    "탈린": "Tallinn", "리가": "Riga", "빌뉴스": "Vilnius",
    "아테네": "Athens", "테살로니키": "Thessaloniki",
    "이스탄불": "Istanbul", "앙카라": "Ankara", "이즈미르": "Izmir",
    "안탈리아": "Antalya",
    "모스크바": "Moscow", "상트페테르부르크": "Saint Petersburg",
    "노보시비르스크": "Novosibirsk", "예카테린부르크": "Yekaterinburg",
    "블라디보스토크": "Vladivostok",
    # ── 일본 ──
    "도쿄": "Tokyo", "오사카": "Osaka", "교토": "Kyoto", "삿포로": "Sapporo",
    "후쿠오카": "Fukuoka", "나고야": "Nagoya", "요코하마": "Yokohama",
    "고베": "Kobe", "센다이": "Sendai", "히로시마": "Hiroshima",
    "나가사키": "Nagasaki", "오키나와": "Naha", "나하": "Naha",
    "가나자와": "Kanazawa", "벳푸": "Beppu",
    # ── 중국 ──
    "베이징": "Beijing", "상하이": "Shanghai", "광저우": "Guangzhou",
    "선전": "Shenzhen", "심천": "Shenzhen", "청두": "Chengdu",
    "충칭": "Chongqing", "시안": "Xian", "톈진": "Tianjin",
    "항저우": "Hangzhou", "난징": "Nanjing", "쑤저우": "Suzhou",
    "우한": "Wuhan", "칭다오": "Qingdao", "다롄": "Dalian",
    "하얼빈": "Harbin", "쿤밍": "Kunming", "샤먼": "Xiamen",
    "산야": "Sanya", "라싸": "Lhasa", "우루무치": "Urumqi",
    # ── 홍콩/대만 ──
    "홍콩": "Hong Kong", "마카오": "Macau",
    "타이베이": "Taipei", "가오슝": "Kaohsiung", "타이중": "Taichung",
    # ── 동남아시아 ──
    "싱가포르": "Singapore", "쿠알라룸푸르": "Kuala Lumpur",
    "페낭": "Penang", "조호르바루": "Johor Bahru",
    "방콕": "Bangkok", "치앙마이": "Chiang Mai", "푸켓": "Phuket",
    "파타야": "Pattaya", "코사무이": "Koh Samui",
    "호치민": "Ho Chi Minh", "하노이": "Hanoi", "다낭": "Da Nang",
    "나트랑": "Nha Trang", "하롱": "Ha Long",
    "자카르타": "Jakarta", "수라바야": "Surabaya", "발리": "Denpasar",
    "덴파사르": "Denpasar", "족자카르타": "Yogyakarta",
    "마닐라": "Manila", "세부": "Cebu", "다바오": "Davao",
    "보라카이": "Boracay",
    "프놈펜": "Phnom Penh", "시엠레아프": "Siem Reap",
    "양곤": "Yangon", "만달레이": "Mandalay",
    "비엔티안": "Vientiane", "루앙프라방": "Luang Prabang",
    "반다르스리브가완": "Bandar Seri Begawan",
    # ── 남아시아 ──
    "뭄바이": "Mumbai", "뉴델리": "New Delhi", "델리": "New Delhi",
    "방갈로르": "Bangalore", "벵갈루루": "Bangalore",
    "콜카타": "Kolkata", "첸나이": "Chennai", "하이데라바드": "Hyderabad",
    "푸네": "Pune", "아마다바드": "Ahmedabad", "자이푸르": "Jaipur",
    "고아": "Goa", "다카": "Dhaka", "콜롬보": "Colombo",
    "카트만두": "Kathmandu", "팀부": "Thimphu",
    "카라치": "Karachi", "라호르": "Lahore", "이슬라마바드": "Islamabad",
    # ── 중동 ──
    "두바이": "Dubai", "아부다비": "Abu Dhabi", "도하": "Doha",
    "리야드": "Riyadh", "제다": "Jeddah", "메카": "Mecca", "메디나": "Medina",
    "테헤란": "Tehran", "쿠웨이트": "Kuwait City", "마나마": "Manama",
    "무스카트": "Muscat", "암만": "Amman", "베이루트": "Beirut",
    "다마스쿠스": "Damascus", "바그다드": "Baghdad",
    "예루살렘": "Jerusalem", "텔아비브": "Tel Aviv",
    # ── 오세아니아 ──
    "시드니": "Sydney", "멜버른": "Melbourne", "브리즈번": "Brisbane",
    "퍼스": "Perth", "애들레이드": "Adelaide", "캔버라": "Canberra",
    "골드코스트": "Gold Coast", "다윈": "Darwin", "호바트": "Hobart",
    "케언스": "Cairns",
    "오클랜드": "Auckland", "웰링턴": "Wellington",
    "크라이스트처치": "Christchurch", "퀸스타운": "Queenstown",
    "수바": "Suva", "포트모르즈비": "Port Moresby",
    "파페에테": "Papeete", "괌": "Hagatna", "사이판": "Saipan",
    # ── 아프리카 ──
    "카이로": "Cairo", "알렉산드리아": "Alexandria",
    "케이프타운": "Cape Town", "요하네스버그": "Johannesburg",
    "더반": "Durban", "프리토리아": "Pretoria",
    "나이로비": "Nairobi", "라고스": "Lagos", "아부자": "Abuja",
    "카사블랑카": "Casablanca", "라바트": "Rabat", "마라케시": "Marrakesh",
    "튀니스": "Tunis", "알제": "Algiers", "트리폴리": "Tripoli",
    "아디스아바바": "Addis Ababa", "하르툼": "Khartoum",
    "아크라": "Accra", "다카르": "Dakar", "아비장": "Abidjan",
    "몸바사": "Mombasa", "다르에스살람": "Dar es Salaam",
    "킨샤사": "Kinshasa", "루안다": "Luanda", "하라레": "Harare",
    "마푸토": "Maputo", "안타나나리보": "Antananarivo",
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
    # 광역시·도
    "Seoul": (37.5665, 126.9780), "Busan": (35.1796, 129.0756),
    "Daegu": (35.8714, 128.6014), "Incheon": (37.4563, 126.7052),
    "Gwangju": (35.1595, 126.8526), "Daejeon": (36.3504, 127.3845),
    "Ulsan": (35.5384, 129.3114), "Sejong": (36.4800, 126.9252),
    "Jeju": (33.4996, 126.5312), "Seogwipo": (33.2541, 126.5601),
    # 경기/강원 주요 시
    "Suwon": (37.2636, 127.0286), "Seongnam": (37.4201, 127.1262),
    "Yongin": (37.2411, 127.1776), "Goyang": (37.6584, 126.8320),
    "Bucheon": (37.5035, 126.7660), "Ansan": (37.3219, 126.8309),
    "Anyang": (37.3943, 126.9568), "Namyangju": (37.6360, 127.2167),
    "Hwaseong": (37.1996, 126.8311), "Pyeongtaek": (36.9921, 127.1129),
    "Uijeongbu": (37.7381, 127.0337), "Siheung": (37.3803, 126.8030),
    "Paju": (37.7599, 126.7800), "Gimpo": (37.6151, 126.7159),
    "Gwangmyeong": (37.4787, 126.8649), "Icheon": (37.2725, 127.4350),
    "Yangju": (37.7853, 127.0457), "Osan": (37.1499, 127.0773),
    "Guri": (37.5944, 127.1297), "Anseong": (37.0080, 127.2797),
    "Pocheon": (37.8949, 127.2003), "Hanam": (37.5392, 127.2148),
    "Yeoju": (37.2982, 127.6371),
    "Chuncheon": (37.8813, 127.7298), "Wonju": (37.3422, 127.9202),
    "Gangneung": (37.7519, 128.8761), "Donghae": (37.5246, 129.1145),
    "Sokcho": (38.2070, 128.5918), "Samcheok": (37.4499, 129.1655),
    "Taebaek": (37.1640, 128.9856),
    # 충청 주요 시
    "Cheongju": (36.6424, 127.4890), "Chungju": (36.9711, 127.9325),
    "Jecheon": (37.1326, 128.1908),
    "Cheonan": (36.8151, 127.1139), "Asan": (36.7898, 127.0017),
    "Gongju": (36.4467, 127.1192), "Boryeong": (36.3334, 126.6128),
    "Seosan": (36.7848, 126.4503), "Nonsan": (36.1872, 127.0986),
    "Dangjin": (36.8895, 126.6457),
    # 전라 주요 시
    "Jeonju": (35.8242, 127.1480), "Iksan": (35.9483, 126.9577),
    "Gunsan": (35.9678, 126.7368), "Jeongeup": (35.5697, 126.8559),
    "Namwon": (35.4163, 127.3905), "Gimje": (35.8033, 126.8809),
    "Mokpo": (34.8118, 126.3922), "Yeosu": (34.7604, 127.6622),
    "Suncheon": (34.9506, 127.4872), "Naju": (35.0157, 126.7106),
    "Gwangyang": (34.9407, 127.6957),
    # 경상 주요 시
    "Changwon": (35.2280, 128.6811), "Jinju": (35.1800, 128.1076),
    "Tongyeong": (34.8544, 128.4331), "Sacheon": (35.0035, 128.0644),
    "Gimhae": (35.2284, 128.8893), "Yangsan": (35.3349, 129.0376),
    "Geoje": (34.8806, 128.6212), "Miryang": (35.5036, 128.7466),
    "Pohang": (36.0190, 129.3435), "Gyeongju": (35.8562, 129.2247),
    "Gumi": (36.1196, 128.3445), "Andong": (36.5684, 128.7294),
    "Yeongju": (36.8056, 128.6240), "Gyeongsan": (35.8252, 128.7415),
    "Sangju": (36.4111, 128.1592), "Mungyeong": (36.5945, 128.1869),
    "Gimcheon": (36.1397, 128.1136),
    # 해외 주요 도시 — 미국/캐나다
    "New York": (40.7128, -74.0060), "Los Angeles": (34.0522, -118.2437),
    "Chicago": (41.8781, -87.6298), "San Francisco": (37.7749, -122.4194),
    "Seattle": (47.6062, -122.3321), "Houston": (29.7604, -95.3698),
    "Miami": (25.7617, -80.1918), "Boston": (42.3601, -71.0589),
    "Washington": (38.9072, -77.0369), "Las Vegas": (36.1699, -115.1398),
    "Dallas": (32.7767, -96.7970), "Philadelphia": (39.9526, -75.1652),
    "Atlanta": (33.7490, -84.3880), "Detroit": (42.3314, -83.0458),
    "Minneapolis": (44.9778, -93.2650), "Orlando": (28.5384, -81.3789),
    "San Diego": (32.7157, -117.1611), "Honolulu": (21.3099, -157.8581),
    "Anchorage": (61.2181, -149.9003),
    "Toronto": (43.6532, -79.3832), "Vancouver": (49.2827, -123.1207),
    "Montreal": (45.5017, -73.5673), "Ottawa": (45.4215, -75.6972),
    "Calgary": (51.0447, -114.0719),
    # 중남미
    "Mexico City": (19.4326, -99.1332), "Lima": (-12.0464, -77.0428),
    "Santiago": (-33.4489, -70.6693), "Bogota": (4.7110, -74.0721),
    "Caracas": (10.4806, -66.9036),
    "Sao Paulo": (-23.5505, -46.6333), "Rio de Janeiro": (-22.9068, -43.1729),
    "Buenos Aires": (-34.6037, -58.3816),
    # 유럽
    "London": (51.5074, -0.1278), "Paris": (48.8566, 2.3522),
    "Berlin": (52.5200, 13.4050), "Munich": (48.1351, 11.5820),
    "Frankfurt": (50.1109, 8.6821), "Hamburg": (53.5511, 9.9937),
    "Rome": (41.9028, 12.4964), "Milan": (45.4642, 9.1900),
    "Venice": (45.4408, 12.3155), "Florence": (43.7696, 11.2558),
    "Naples": (40.8518, 14.2681),
    "Madrid": (40.4168, -3.7038), "Barcelona": (41.3851, 2.1734),
    "Seville": (37.3891, -5.9845),
    "Amsterdam": (52.3676, 4.9041), "Rotterdam": (51.9244, 4.4777),
    "Brussels": (50.8503, 4.3517),
    "Vienna": (48.2082, 16.3738), "Zurich": (47.3769, 8.5417),
    "Geneva": (46.2044, 6.1432), "Bern": (46.9480, 7.4474),
    "Prague": (50.0755, 14.4378), "Budapest": (47.4979, 19.0402),
    "Warsaw": (52.2297, 21.0122),
    "Stockholm": (59.3293, 18.0686), "Oslo": (59.9139, 10.7522),
    "Copenhagen": (55.6761, 12.5683), "Helsinki": (60.1699, 24.9384),
    "Dublin": (53.3498, -6.2603), "Lisbon": (38.7223, -9.1393),
    "Athens": (37.9838, 23.7275),
    "Istanbul": (41.0082, 28.9784), "Ankara": (39.9334, 32.8597),
    "Moscow": (55.7558, 37.6173), "Saint Petersburg": (59.9311, 30.3609),
    # 아시아
    "Tokyo": (35.6762, 139.6503), "Osaka": (34.6937, 135.5023),
    "Kyoto": (35.0116, 135.7681), "Sapporo": (43.0618, 141.3545),
    "Fukuoka": (33.5904, 130.4017), "Nagoya": (35.1815, 136.9066),
    "Yokohama": (35.4437, 139.6380),
    "Beijing": (39.9042, 116.4074), "Shanghai": (31.2304, 121.4737),
    "Guangzhou": (23.1291, 113.2644), "Shenzhen": (22.5431, 114.0579),
    "Chengdu": (30.5728, 104.0668), "Chongqing": (29.4316, 106.9123),
    "Xian": (34.3416, 108.9398), "Tianjin": (39.0842, 117.2010),
    "Hong Kong": (22.3193, 114.1694), "Macau": (22.1987, 113.5439),
    "Taipei": (25.0330, 121.5654),
    "Singapore": (1.3521, 103.8198), "Kuala Lumpur": (3.1390, 101.6869),
    "Bangkok": (13.7563, 100.5018), "Chiang Mai": (18.7883, 98.9853),
    "Ho Chi Minh": (10.8231, 106.6297), "Hanoi": (21.0285, 105.8542),
    "Da Nang": (16.0544, 108.2022),
    "Jakarta": (-6.2088, 106.8456), "Denpasar": (-8.6705, 115.2126),
    "Manila": (14.5995, 120.9842), "Cebu": (10.3157, 123.8854),
    "Mumbai": (19.0760, 72.8777), "New Delhi": (28.6139, 77.2090),
    "Bangalore": (12.9716, 77.5946), "Kolkata": (22.5726, 88.3639),
    "Chennai": (13.0827, 80.2707),
    "Dubai": (25.2048, 55.2708), "Abu Dhabi": (24.4539, 54.3773),
    "Doha": (25.2854, 51.5310), "Riyadh": (24.7136, 46.6753),
    "Tehran": (35.6892, 51.3890), "Kuwait City": (29.3759, 47.9774),
    # 오세아니아
    "Sydney": (-33.8688, 151.2093), "Melbourne": (-37.8136, 144.9631),
    "Brisbane": (-27.4698, 153.0251), "Perth": (-31.9505, 115.8605),
    "Adelaide": (-34.9285, 138.6007), "Canberra": (-35.2809, 149.1300),
    "Auckland": (-36.8485, 174.7633), "Wellington": (-41.2865, 174.7762),
    # 아프리카
    "Cairo": (30.0444, 31.2357), "Cape Town": (-33.9249, 18.4241),
    "Johannesburg": (-26.2041, 28.0473), "Nairobi": (-1.2921, 36.8219),
    "Lagos": (6.5244, 3.3792), "Casablanca": (33.5731, -7.5898),
}


def _resolve_city_coords(city: str) -> tuple:
    """도시명 → (lat, lon). 내장 좌표표 → 영문 지오코딩 → 한글 지오코딩 → 서울 폴백."""
    raw_city = city.strip()
    eng_city = KOR_CITY_MAP.get(raw_city, raw_city)
    coords = CITY_COORDS.get(eng_city)

    # 1. 영문 도시명으로 지오코딩
    if not coords:
        try:
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={eng_city}&count=1&language=en"
            gr = requests.get(geo_url, timeout=15)
            gr.raise_for_status()
            results = gr.json().get("results", [])
            if results:
                coords = (results[0]["latitude"], results[0]["longitude"])
        except Exception:
            pass

    # 2. 한글 도시명으로 지오코딩 (KOR_CITY_MAP에 없는 경우 백업)
    if not coords and raw_city != eng_city:
        try:
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={raw_city}&count=1&language=ko"
            gr = requests.get(geo_url, timeout=15)
            gr.raise_for_status()
            results = gr.json().get("results", [])
            if results:
                coords = (results[0]["latitude"], results[0]["longitude"])
        except Exception:
            pass

    # 3. 그래도 좌표를 못 찾았으면 서울 좌표로 폴백 (마지막 안전망)
    return coords or (37.5665, 126.9780)


def _fetch_weather_open_meteo(city: str) -> Optional[dict]:
    """Fetch real-time weather from Open-Meteo (free, no API key).

    Retries once on transient network errors and converts wind speed
    from km/h (Open-Meteo default) to m/s for UI consistency.
    """
    lat, lon = _resolve_city_coords(city)
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m"
        f"&wind_speed_unit=ms"
        f"&timezone=auto"
    )
    # HF 등 데이터센터 IP는 기본 python-requests UA로 거부될 수 있어 브라우저 UA 부착.
    _OM_UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    for _ in range(3):  # retry 2 → 3
        try:
            r = requests.get(url, timeout=15, headers=_OM_UA)  # 12 → 15
            r.raise_for_status()
            d = r.json()
            current = d.get("current", {})
            if not current or current.get("temperature_2m") is None:
                continue
            wmo_code = current.get("weather_code", 0)
            desc, icon = WMO_WEATHER_CODES.get(wmo_code, ("알 수 없음", "01d"))
            return {
                "city": city,
                "lat": lat,
                "lon": lon,
                "temp": round(float(current.get("temperature_2m", 0)), 1),
                "feels_like": round(float(current.get("apparent_temperature", 0)), 1),
                "humidity": int(current.get("relative_humidity_2m", 0) or 0),
                "desc": desc,
                "icon": icon,
                "wind_speed": round(float(current.get("wind_speed_10m", 0)), 1),
                "updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
        except Exception:
            continue
    return None


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_weather_series(city: str = "Seoul") -> dict:
    """Open-Meteo 한 번 호출로 기온 추이(지난 7일) + 예보(7일) 시계열 조회.

    Returns:
      {"ok": bool,
       "daily": [{"Date","tmax","tmin","pop"}...],   # pop=강수확률(%) — 예보 구간만 값 존재
       "hourly": [{"Time","temp"}...],               # 1시간 간격, 과거 2일~예보 2일
       "today": "YYYY-MM-DD", "now": "YYYY-MM-DDTHH:00"}
    """
    lat, lon = _resolve_city_coords(city)
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max"
        f"&hourly=temperature_2m"
        f"&past_days=7&forecast_days=8&timezone=auto"
    )
    _UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
           "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    for _ in range(3):
        try:
            r = requests.get(url, timeout=15, headers=_UA)
            r.raise_for_status()
            d = r.json()
            dly = d.get("daily", {})
            dates = dly.get("time", [])
            if not dates:
                continue
            daily = []
            for i, ds in enumerate(dates):
                try:
                    daily.append({
                        "Date": ds,
                        "tmax": round(float(dly["temperature_2m_max"][i]), 1),
                        "tmin": round(float(dly["temperature_2m_min"][i]), 1),
                        "pop": dly.get("precipitation_probability_max", [None] * len(dates))[i],
                    })
                except (TypeError, ValueError, IndexError, KeyError):
                    continue
            hly = d.get("hourly", {})
            now = datetime.datetime.now()
            today_str = now.strftime("%Y-%m-%d")
            now_hour = now.strftime("%Y-%m-%dT%H:00")
            hourly = []
            lo = (now - datetime.timedelta(days=2)).strftime("%Y-%m-%dT%H:00")
            hi = (now + datetime.timedelta(days=2)).strftime("%Y-%m-%dT%H:00")
            for t, v in zip(hly.get("time", []), hly.get("temperature_2m", [])):
                if v is None or not (lo <= t <= hi):
                    continue
                hourly.append({"Time": t, "temp": round(float(v), 1)})
            if daily:
                return {"ok": True, "daily": daily, "hourly": hourly,
                        "today": today_str, "now": now_hour}
        except Exception:
            continue
    return {"ok": False, "daily": [], "hourly": [], "today": "", "now": ""}


def _fetch_weather_wttr(city: str) -> Optional[dict]:
    """wttr.in 무키 날씨 폴백 — Open-Meteo 가 HF 데이터센터 IP에서 막힐 때 대체.

    다른 서비스라 차단 패턴이 달라 한쪽이 막혀도 다른 쪽이 응답할 수 있다.
    """
    raw_city = city.strip()
    eng_city = KOR_CITY_MAP.get(raw_city, raw_city)
    try:
        r = requests.get(
            f"https://wttr.in/{eng_city}?format=j1&lang=ko",
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"},
            timeout=12,
        )
        r.raise_for_status()
        cc = (r.json().get("current_condition") or [{}])[0]
        if not cc or cc.get("temp_C") is None:
            return None
        desc = ""
        if cc.get("lang_ko"):
            desc = (cc["lang_ko"][0] or {}).get("value", "")
        if not desc and cc.get("weatherDesc"):
            desc = (cc["weatherDesc"][0] or {}).get("value", "")
        coords = CITY_COORDS.get(eng_city, (37.5665, 126.9780))
        return {
            "city": city,
            "lat": coords[0],
            "lon": coords[1],
            "temp": round(float(cc.get("temp_C", 0)), 1),
            "feels_like": round(float(cc.get("FeelsLikeC", cc.get("temp_C", 0))), 1),
            "humidity": int(cc.get("humidity", 0) or 0),
            "desc": desc or "현재 날씨",
            "icon": "01d",
            "wind_speed": round(float(cc.get("windspeedKmph", 0) or 0) / 3.6, 1),  # km/h → m/s
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

    # 2.5. wttr.in 무키 폴백 — Open-Meteo 가 HF에서 차단될 때 (다른 서비스라 차단 패턴 다름)
    result = _fetch_weather_wttr(city)
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

_TRAFFIC_QUERY = "고속도로 교통 도로 상황"
_TRAFFIC_STATUS_KEYWORDS = [
    ("원활", "원활", "green"), ("소통", "원활", "green"),
    ("서행", "서행", "orange"), ("혼잡", "혼잡", "orange"),
    ("지체", "지체", "orange"),
    ("정체", "정체", "red"), ("통제", "통제", "red"),
    ("사고", "사고", "red"),
]


def _classify_traffic(text: str) -> tuple[str, str]:
    """기사 본문/제목에서 교통 상태 키워드를 감지해 (status, color) 반환."""
    for kw, st_val, clr in _TRAFFIC_STATUS_KEYWORDS:
        if kw in text:
            return st_val, clr
    return "정보", "blue"


def _fetch_traffic_local() -> list[dict]:
    """실시간 교통 뉴스 수집. DDG news → Google News RSS 다단 폴백.

    실시간성을 위해 1일 → 1주 → RSS(7일) 순으로 시도하여 빈 결과를 피함.
    RSS는 Google News가 보통 최신순으로 보내주므로 묵은 기사 위험이 낮음.
    """
    items: list[dict] = []

    # ── DDG 시도 (1일 → 1주) ────────────────────────────────────────────
    def _try_ddg(timelimit: str) -> list:
        try:
            if not _DDGS:
                return []
            with _DDGS() as ddgs:
                return list(ddgs.news(
                    _TRAFFIC_QUERY,
                    region="kr-kr",
                    max_results=8,
                    timelimit=timelimit,
                ))
        except Exception:
            return []

    raw = _try_ddg("d")
    if len(raw) < 4:
        raw = raw + _try_ddg("w")

    for r in raw:
        title = _strip_html(r.get("title", ""))
        body = _strip_html(r.get("body", ""))
        if not title:
            continue
        status, color = _classify_traffic(title + " " + body)
        items.append({
            "title": title,
            "status": status,
            "color": color,
            "source": r.get("source", ""),
            "link": r.get("url", ""),
            "published": r.get("date", ""),
            "snippet": body[:120] if body else "",
        })

    # ── DDG가 비었거나 부족하면 Google News RSS 폴백 ─────────────────────
    if len(items) < 4:
        try:
            rss_results = _fetch_news_rss(_TRAFFIC_QUERY, limit=8, rss_when="7d")
            for r in rss_results:
                title = _strip_html(r.get("title", ""))
                if not title:
                    continue
                snippet = _strip_html(r.get("snippet", ""))
                status, color = _classify_traffic(title + " " + snippet)
                items.append({
                    "title": title,
                    "status": status,
                    "color": color,
                    "source": r.get("source", ""),
                    "link": r.get("link", ""),
                    "published": r.get("published", ""),
                    "snippet": snippet[:120],
                })
        except Exception:
            pass

    if not items:
        return []

    items = _deduplicate_news(items, title_key="title")
    items.sort(key=lambda v: v.get("published", "") or "", reverse=True)
    return items[:8]

# ── API Calls (Backend) and Public Functions ───────────────────────────────

@st.cache_data(ttl=900, show_spinner=False)
def _fetch_weather_cached(city: str, api_key: Optional[str]) -> dict:
    """캐시 가능한 실제 호출 — 실패 결과는 캐시되지 않도록 호출부에서 분기."""
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


def fetch_weather(city: str = "Seoul", api_key: Optional[str] = None) -> dict:
    """Fetch weather data. Mock(_sample=True) 결과는 캐싱하지 않고 매 호출마다 재시도."""
    # HF Secrets 등에 OpenWeatherMap 키가 있으면 우선 사용(클라우드에서 Open-Meteo 차단 대비)
    if not api_key and OPENWEATHER_API_KEY:
        api_key = OPENWEATHER_API_KEY
    result = _fetch_weather_cached(city, api_key)
    if result.get("_sample"):
        # 캐시 무효화: 다음 호출에서 다시 시도하도록 캐시 비우기
        try:
            _fetch_weather_cached.clear()
        except Exception:
            pass
        # 즉시 한 번 더 직접 시도 (캐시 우회) — Open-Meteo → wttr.in 순
        eng_city = KOR_CITY_MAP.get(city.strip(), city.strip())
        retry = _fetch_weather_open_meteo(eng_city) or _fetch_weather_wttr(eng_city)
        if retry:
            return retry
    return result

_NEWS_CAT_QUERY = {
    "종합": "오늘 주요뉴스 시사 사회 정치",
    "IT/과학": "IT 과학 기술 AI 반도체 뉴스",
    "경제": "경제 금융 증시 환율 뉴스",
    "생활": "생활 사회 날씨 건강 뉴스",
}

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_news(category: str = "종합", limit: int = 10) -> list[dict]:
    """Fetch news: DDG + Google RSS 병합 (부족하면 보충)."""
    if IS_API_MODE:
        try:
            r = requests.get(f"{API_BASE_URL}/data/news", params={"category": category, "limit": limit}, timeout=5)
            r.raise_for_status()
            news = r.json().get("news", [])
            if news:
                return _deduplicate_news(news)
        except Exception:
            pass

    query = _NEWS_CAT_QUERY.get(category, "오늘 주요 뉴스")
    result = []

    # 1순위: DDG 뉴스
    result = _fetch_news_ddg(query, limit=limit, timelimit="d")

    # 부족하면 1주일로 재시도
    if len(result) < limit:
        more = _fetch_news_ddg(query, limit=limit, timelimit="w")
        result = _deduplicate_news(result + more)

    # 2순위: Google News RSS 보충
    if len(result) < limit:
        rss = _fetch_news_local(category, limit)
        result = _deduplicate_news(result + rss)

    # 3순위: Google RSS 검색 보충
    if len(result) < limit:
        rss2 = _fetch_news_rss(query, limit=limit)
        result = _deduplicate_news(result + rss2)

    return result[:limit]

@st.cache_data(ttl=600, show_spinner=False)
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


def _fetch_news_rss(query: str, limit: int = 10, rss_when: str = "7d") -> list[dict]:
    """Fallback: search news via Google News RSS."""
    import urllib.parse
    encoded = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded}+when:{rss_when}&hl=ko&gl=KR&ceid=KR:ko"
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


def _fetch_news_naver(query: str, limit: int = 10) -> list[dict]:
    """Naver 검색 API 뉴스. 키(HAS_NAVER) 있을 때만 동작 — 없으면 즉시 [].

    클라우드(HF)에서 DDG/Google RSS 와 달리 레이트리밋이 없어 모든 카테고리가
    안정적으로 로드된다. 발급: https://developers.naver.com/apps/ (무료 일 25,000건).
    """
    if not HAS_NAVER:
        return []
    try:
        r = requests.get(
            "https://openapi.naver.com/v1/search/news.json",
            headers={
                "X-Naver-Client-Id": NAVER_CLIENT_ID,
                "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
            },
            params={"query": query, "display": min(max(limit, 1), 100), "sort": "date"},
            timeout=8,
        )
        r.raise_for_status()
        items = []
        for it in r.json().get("items", []):
            title = _strip_html(it.get("title", ""))
            desc = _strip_html(it.get("description", "") or "")[:200]
            snippet = desc if (desc and not _is_similar(desc, title)) else ""
            items.append({
                "title": title,
                "link": it.get("originallink") or it.get("link", ""),
                "source": "",
                "published": it.get("pubDate", ""),
                "snippet": snippet,
            })
        return items
    except Exception:
        return []


def _fetch_web_ddg(query: str, limit: int = 10, timelimit: str | None = None) -> list[dict]:
    """Fetch web results via DuckDuckGo — provides real snippets.

    Args:
        timelimit: DDG 시간 필터. "d"(1일), "w"(1주), "m"(1개월), "y"(1년). None이면 무필터.
    """
    try:
        if not _DDGS:
            return []
        with _DDGS() as ddgs:
            _kwargs = {"region": "kr-kr", "max_results": limit}
            if timelimit:
                _kwargs["timelimit"] = timelimit
            results = list(ddgs.text(query, **_kwargs))
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


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_web_search(query: str, limit: int = 10, timelimit: str = "w", sort_by_date: bool = True) -> list[dict]:
    """Fetch web search results. DuckDuckGo first, then RSS fallback.

    Args:
        timelimit: "d"(1일), "w"(1주), "m"(1개월), "3m"(3개월), "6m"(6개월), "y"(1년).
                   기본 "w" — 최신 이슈 우선 노출. DDG는 d/w/m/y만 지원하므로 3m/6m은 m으로 매핑.
        sort_by_date: published 필드 기준 내림차순 정렬. 기본 True.
    """
    _ddg_tl_map = {"d": "d", "w": "w", "m": "m", "3m": "m", "6m": "m", "y": "y"}
    _rss_when_map = {"d": "1d", "w": "7d", "m": "30d", "3m": "90d", "6m": "180d", "y": "365d"}
    _ddg_tl = _ddg_tl_map.get(timelimit, "w")
    _rss_when = _rss_when_map.get(timelimit, "7d")
    results = []
    if IS_API_MODE:
        try:
            r = requests.get(f"{API_BASE_URL}/data/search/web", params={"query": query, "limit": limit}, timeout=5)
            r.raise_for_status()
            results = r.json().get("results", [])
        except Exception:
            pass
    if not results:
        results = _fetch_news_naver(query, limit=limit)   # 키 있으면 최우선(레이트리밋 없음)
    _used_ddg = False
    if not results:
        results = _fetch_web_ddg(query, limit=limit, timelimit=_ddg_tl)
        _used_ddg = bool(results)
    if not results:
        results = _fetch_news_rss(query, limit=limit, rss_when=_rss_when)
    # DDG가 일부만 반환했을 때만 시간창 확장(w→m)으로 보충 — DDG 빈 결과면 재호출도
    # 레이트리밋만 늘리므로 생략(HF 요청 수 절감).
    if _used_ddg and len(results) < limit and timelimit == "w":
        _more_ddg = _fetch_web_ddg(query, limit=limit, timelimit="m")
        results = _deduplicate_news(results + _more_ddg, title_key="title")
    domain = _detect_domain(query)
    results = _filter_by_domain(results, domain, title_key="title")
    results = _deduplicate_news(results, title_key="title")
    if sort_by_date:
        results.sort(key=lambda v: v.get("published", "") or "", reverse=True)
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


_FX_PERIOD_DAYS = {"5d": 7, "1mo": 35, "3mo": 95, "6mo": 185, "1y": 370}


def _fx_period_to_days(period: str) -> int:
    """환율 기간 코드 → Frankfurter 조회용 시작일 오프셋(달력일).
    주말·공휴일 갭을 감안해 여유를 둔다."""
    return _FX_PERIOD_DAYS.get(period, 35)


def _parse_frankfurter_timeseries(payload: dict, symbols) -> dict:
    """Frankfurter 시계열 응답 → {code: [{"Date","Close"}...]} (날짜 오름차순, Close>0만).

    payload 예: {"base":"USD","rates":{"2026-06-25":{"KRW":1542.92,...}, ...}}
    """
    rates = (payload or {}).get("rates", {}) or {}
    history: dict = {code: [] for code in symbols}
    for date_str in sorted(rates.keys()):
        day = rates.get(date_str) or {}
        for code in symbols:
            val = day.get(code)
            if val is None:
                continue
            try:
                close = round(float(val), 4)
            except (TypeError, ValueError):
                continue
            if close > 0:
                history[code].append({"Date": date_str, "Close": close})
    return history


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_fx_history(symbols: tuple = ("KRW", "EUR", "JPY", "CNY"),
                     period: str = "1mo") -> dict:
    """Frankfurter(ECB)로 USD 기준 환율 히스토리 조회.

    Returns: {"ok": bool, "history": {code: [{"Date","Close"}...]}, "updated": str}
    실패 시 {"ok": False, "history": {}}.
    """
    try:
        end = datetime.date.today()
        start = end - datetime.timedelta(days=_fx_period_to_days(period))
        sym_csv = ",".join(symbols)
        url = (
            f"https://api.frankfurter.dev/v1/{start.isoformat()}..{end.isoformat()}"
            f"?base=USD&symbols={sym_csv}"
        )
        _UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
               "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        r = requests.get(url, headers=_UA, timeout=10)
        r.raise_for_status()
        payload = r.json()
        history = _parse_frankfurter_timeseries(payload, symbols)
        if not any(history.values()):
            return {"ok": False, "history": {}}
        return {
            "ok": True,
            "history": history,
            "updated": payload.get("end_date", end.isoformat()),
        }
    except Exception:
        return {"ok": False, "history": {}}


def _kr_period_to_range(period: str) -> str:
    """yfinance period → 네이버 차트 range 변환."""
    return {"5d": "1W", "1mo": "1M", "3mo": "3M", "6mo": "6M", "1y": "1Y"}.get(period, "1M")


@st.cache_data(ttl=600, show_spinner=False)
def fetch_kr_index(code: str = "KOSPI", period: str = "1mo") -> dict:
    """네이버 금융 API로 한국 지수(KOSPI/KOSDAQ) 실시간 + 히스토리 데이터 조회."""
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        # 1) 현재가 조회
        url = f"https://m.stock.naver.com/api/index/{code}/basic"
        r = requests.get(url, headers=headers, timeout=8)
        r.raise_for_status()
        d = r.json()
        price = float(d.get("closePrice", "0").replace(",", ""))
        change = float(d.get("compareToPreviousClosePrice", "0").replace(",", ""))
        change_pct = float(d.get("fluctuationsRatio", "0").replace(",", ""))

        # 2) 히스토리 차트 데이터 조회
        history = []
        high_val, low_val = price, price
        try:
            period_days = {"5d": 5, "1mo": 22, "3mo": 66, "6mo": 132, "1y": 252}.get(period, 22)
            chart_url = f"https://m.stock.naver.com/api/index/{code}/price?pageSize={period_days}&page=1"
            cr = requests.get(chart_url, headers=headers, timeout=8)
            cr.raise_for_status()
            chart_data = cr.json()
            # 네이버 price API: list of {localTradedAt, closePrice, ...}
            if isinstance(chart_data, list):
                price_list = chart_data
            else:
                price_list = chart_data.get("priceInfos", chart_data.get("prices", []))

            price_list = price_list[:period_days]

            for item in reversed(price_list):
                close_str = item.get("closePrice", "0")
                close_val = float(str(close_str).replace(",", ""))
                date_str = item.get("localTradedAt", "")
                if not (date_str and len(date_str) >= 10):
                    continue            # 날짜 없는 레코드는 건너뜀(차트 파싱 오류 방지)
                date_fmt = date_str[:10]   # YYYY-MM-DD (연도 포함 — 트레일링 구간 정렬 보장)
                if close_val > 0:
                    history.append({"Date": date_fmt, "Close": round(close_val, 2), "Volume": 0})

            if history:
                closes = [h["Close"] for h in history]
                high_val = max(closes)
                low_val = min(closes)
        except Exception:
            pass

        # 네이버 차트는 pageSize 한도로 3mo+(66·132·252)에서 빈 응답 → yfinance로 히스토리 폴백
        _pdays = {"5d": 5, "1mo": 22, "3mo": 66, "6mo": 132, "1y": 252}.get(period, 22)
        if _yf and len(history) < max(5, int(_pdays * 0.5)):
            try:
                _yf_code = {"KOSPI": "^KS11", "KOSDAQ": "^KQ11"}.get(code)
                if _yf_code:
                    _yh = _yf.Ticker(_yf_code).history(period=period)
                    _yrecs = []
                    for _dt, _row in _yh.iterrows():
                        _cv = float(_row["Close"])
                        if _cv == _cv and _cv > 0:          # NaN 제외
                            _vol = _row.get("Volume", 0)
                            _yrecs.append({
                                "Date": _dt.strftime("%Y-%m-%d"),
                                "Close": round(_cv, 2),
                                "Volume": int(_vol) if _vol == _vol else 0,
                            })
                    if len(_yrecs) > len(history):
                        history = _yrecs
                        _c = [h["Close"] for h in history]
                        high_val, low_val = max(_c), min(_c)
            except Exception:
                pass

        return {
            "name": code, "symbol": code,
            "price": round(price, 2),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "high": round(high_val, 2), "low": round(low_val, 2), "volume": 0,
            "history": history, "ok": True,
            "updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    except Exception:
        # 네이버 API 일시 장애 시 yfinance 지수 심볼로 전체 폴백 (현재가+히스토리)
        _yf_code = {"KOSPI": "^KS11", "KOSDAQ": "^KQ11"}.get(code)
        if _yf_code:
            fb = fetch_stock_data(_yf_code, period=period)
            if fb.get("ok"):
                return {**fb, "name": code, "symbol": code}
        return {"symbol": code, "ok": False}


@st.cache_data(ttl=600, show_spinner=False)
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
                    "Date": dt.strftime("%Y-%m-%d"),
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


def period_points_for_query(query: str):
    """검색어의 기간 의도 → (yfinance period, 표본 점 수, 장기라벨 여부).
    예) '1년 추세'→('1y',12,True), '3개월'→('3mo',10,False), 기본→('1mo',8,False)."""
    import re as _re
    q = query or ""
    m = _re.search(r"(\d+)\s*(년|개월|분기|주|일)", q)
    if m:
        num, unit = int(m.group(1)), m.group(2)
        if unit == "년":
            return ("1y", 12, True)
        if unit == "개월":
            if num >= 6:
                return ("6mo", 12, True)
            if num >= 3:
                return ("3mo", 10, False)
            return ("1mo", 10, False)
        if unit == "분기":
            return ("3mo", 10, False)
        if unit in ("주", "일"):
            return ("5d", 7, False)
    if any(k in q for k in ("연간", "장기", "1년", "올해", "연중")):
        return ("1y", 12, True)
    if "반기" in q or "6개월" in q:
        return ("6mo", 12, True)
    if "분기" in q:
        return ("3mo", 10, False)
    if "월간" in q:
        return ("1mo", 10, False)
    if "주간" in q:
        return ("5d", 7, False)
    return ("1mo", 8, False)  # 기본: 최근 1개월(7일보다 정보량↑)


def build_trend_for_query(query: str, symbol: str = "069500.KS"):
    """검색어 기간 의도에 맞춰 실데이터 트렌드 시계열 생성 → (dates, values, period_label).
    장기(1y·6mo)는 'YY-MM', 단기는 'MM-DD' 라벨. 데이터 표본을 n개로 균등 샘플링."""
    import pandas as _pd
    period, n, long_fmt = period_points_for_query(query)
    d = fetch_stock_data(symbol, period=period)
    hist = (d.get("history") or []) if isinstance(d, dict) else []
    pairs = [(h.get("Date", ""), h.get("Close")) for h in hist if h.get("Close") is not None]
    if not pairs:
        dates = _pd.date_range(end=datetime.datetime.today(), periods=n).strftime("%m-%d").tolist()
        return dates, [0] * n, period
    if len(pairs) > n:
        idx = sorted(set(round(i * (len(pairs) - 1) / (n - 1)) for i in range(n)))
        pairs = [pairs[i] for i in idx]
    dates, values = [], []
    for dt_str, close in pairs:
        if long_fmt and len(dt_str) >= 7:
            dates.append(dt_str[2:7])   # YY-MM
        elif len(dt_str) >= 10:
            dates.append(dt_str[5:10])  # MM-DD
        else:
            dates.append(dt_str)
        values.append(close)
    return dates, values, period


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


@st.cache_data(ttl=1800, show_spinner=False)
def _yt_search_api(query: str, limit: int = 12, sort_by_date: bool = False) -> list[dict]:
    """YouTube Data API v3 검색 — 키(HAS_YOUTUBE_API) 있을 때만 동작, 없으면 [].

    HF 등 클라우드에서 유튜브 스크래핑이 차단되므로 영상 검색의 사실상 유일한
    안정 클라우드 경로. 발급: console.cloud.google.com → YouTube Data API v3.
    """
    if not HAS_YOUTUBE_API:
        return []
    try:
        r = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": min(max(limit, 1), 50),
                "order": "date" if sort_by_date else "relevance",
                "regionCode": "KR",
                "relevanceLanguage": "ko",
                "key": YOUTUBE_API_KEY,
            },
            timeout=8,
        )
        r.raise_for_status()
        items = []
        for it in r.json().get("items", []):
            vid = (it.get("id") or {}).get("videoId", "")
            if not vid:
                continue
            sn = it.get("snippet", {})
            th = sn.get("thumbnails", {})
            thumb = (th.get("high") or th.get("medium") or th.get("default") or {}).get("url", "")
            items.append({
                "vid_id": vid,
                "title": _strip_html(sn.get("title", "")),
                "url": f"https://www.youtube.com/watch?v={vid}",
                "thumbnail": thumb,
                "platform": "YouTube",
                "uploader": sn.get("channelTitle", ""),
                "published": sn.get("publishedAt", ""),
                "description": _strip_html(sn.get("description", "") or "")[:150],
            })
        return items
    except Exception:
        return []


def fetch_youtube_search(query: str, limit: int = 12, timelimit: str | None = None) -> list[dict]:
    """Fetch YouTube videos. 빈 결과는 캐시하지 않아 다음 렌더에서 재시도한다.

    스크래핑(HF에서 flaky)이 일시적으로 []를 주면 캐시 고정 대신 재시도해 복구.
    비어있지 않은 결과만 캐시(30분) → YouTube Data API 할당량 보호 + 속도.
    """
    result = _fetch_youtube_cached(query, limit, timelimit)
    if not result:
        try:
            _fetch_youtube_cached.clear()
        except Exception:
            pass
    return result


@st.cache_data(ttl=1800, show_spinner=False)
def _fetch_youtube_cached(query: str, limit: int = 12, timelimit: str | None = None) -> list[dict]:
    """실제 수집: Data API(키) → YouTube 페이지 파싱 → RSS → DDG (4단계 병합).

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

    # 0차: YouTube Data API (키 있으면 최우선 — HF 스크래핑 차단 대안)
    try:
        _merge(_yt_search_api(query, limit, sort_by_date=sort_by_date))
    except Exception:
        pass

    # 1차: YouTube 검색 페이지 직접 파싱
    try:
        _merge(_yt_search_scrape(query, limit, sort_by_date=sort_by_date))
    except Exception:
        pass

    def _enough() -> bool:
        # 도메인 필터 후에도 limit 만큼 남으면 충분 → 느린 후속 단계 생략(표시 건수 보존).
        return len(_filter_by_domain(all_items, domain, title_key="title")) >= limit

    # 2차: YouTube 채널 RSS — 1차(스크래핑)로 부족할 때만. RSS 가 ~2초로 가장 느려,
    # 1차가 보통 limit 을 채우면 이 단계를 건너뛰어 영상 fetch 를 ~2.6s 단축한다.
    if not _enough():
        try:
            _merge(_yt_search_rss(query, limit))
        except Exception:
            pass

    # 3차: DDG videos — 여전히 부족할 때만 (다양한 플랫폼 + 최신 영상 보강)
    if not _enough():
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


# 여러 페이지의 '데이터 갱신' 버튼이 fetch_youtube_search.clear() 를 호출한다.
# 래퍼로 분리하며 @st.cache_data 가 _fetch_youtube_cached 로 옮겨가 .clear() 가
# 사라졌으므로, 실제 캐시의 clear 를 래퍼에 위임 부착해 호환을 유지한다.
fetch_youtube_search.clear = _fetch_youtube_cached.clear


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_news_search(query: str, limit: int = 10, timelimit: str = "m") -> list[dict]:
    """Fetch news search results. DuckDuckGo first (better snippets), then RSS fallback.

    Args:
        timelimit: "d"(1일), "w"(1주), "m"(1개월), "3m"(3개월),
                   "6m"(6개월), "y"(1년), "2y"(2년), "3y"(3년)
    """
    _rss_when_map = {
        "d": "1d", "w": "7d", "m": "30d", "3m": "90d",
        "6m": "180d", "y": "365d", "2y": "730d", "3y": "1095d",
    }
    _ddg_tl_map = {"d": "d", "w": "w", "m": "m", "3m": "m", "6m": "m", "y": "y", "2y": "y", "3y": "y"}
    _rss_when = _rss_when_map.get(timelimit, "30d")
    _ddg_tl = _ddg_tl_map.get(timelimit, "m")
    news = []
    if IS_API_MODE:
        try:
            r = requests.get(f"{API_BASE_URL}/data/search/news", params={"query": query, "limit": limit}, timeout=5)
            r.raise_for_status()
            news = r.json().get("news", [])
        except Exception:
            pass
    if not news:
        news = _fetch_news_naver(query, limit=limit)   # 키 있으면 최우선(레이트리밋 없음)
    _rss_done = False
    if not news:
        news = _fetch_news_ddg(query, limit=limit, timelimit=_ddg_tl)
    if not news:
        news = _fetch_news_rss(query, limit=limit, rss_when=_rss_when)
        _rss_done = True
    # DDG가 일부만 반환했을 때만 RSS로 보충 — DDG 빈 결과면 RSS는 위에서 이미 호출했으므로
    # 재호출은 같은 HF IP 요청만 늘려 레이트리밋을 악화시킨다(중복 제거).
    if not _rss_done and len(news) < limit:
        more = _fetch_news_rss(query, limit=limit, rss_when=_rss_when)
        news = _deduplicate_news(news + more, title_key="title")
    domain = _detect_domain(query)
    news = _filter_by_domain(news, domain, title_key="title")
    news = _deduplicate_news(news, title_key="title")
    return news
