"""Environment mode detection for dual-mode architecture.

기본 동작: LIFE_MODE 환경변수를 명시적으로 'api'로 지정하지 않는 한
대시보드는 standalone(직접 외부 API 호출) 모드로 동작한다.
이는 사용자가 별도의 FastAPI 백엔드를 띄우지 않고도 즉시 사용 가능하도록 보장한다.
"""
import os

_explicit = os.getenv("LIFE_MODE")

if _explicit:
    MODE = _explicit.lower()
else:
    MODE = "standalone"

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8001/api/v1")
IS_API_MODE = (MODE == "api")

# Naver 검색 API (선택) — HF Secrets/환경변수에 키를 넣으면 뉴스 fetch가
# DDG/RSS 보다 먼저 Naver를 사용한다. 클라우드(HF)에서 레이트리밋이 없어
# 모든 카테고리가 빠르고 안정적으로 로드됨. 키가 없으면 기존 DDG→RSS 그대로.
# 발급: https://developers.naver.com/apps/  (검색 API, 무료 일 25,000건)
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "")
HAS_NAVER = bool(NAVER_CLIENT_ID and NAVER_CLIENT_SECRET)

# OpenWeatherMap (선택) — 키 있으면 날씨를 Open-Meteo 보다 먼저 사용.
# HF에서 Open-Meteo 가 IP 차단/레이트리밋될 때 안정적. 발급: https://openweathermap.org/api (무료)
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

# YouTube Data API v3 (선택) — 키 있으면 영상 검색을 스크래핑 대신 공식 API로.
# HF에서 유튜브 스크래핑이 차단되므로 영상 표시의 사실상 유일한 클라우드 해법.
# 발급: https://console.cloud.google.com → YouTube Data API v3 사용설정 → API 키 (무료 일 10,000 units)
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
HAS_YOUTUBE_API = bool(YOUTUBE_API_KEY)
