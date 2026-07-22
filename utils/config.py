"""Environment mode detection for dual-mode architecture.

기본 동작: LIFE_MODE 환경변수를 명시적으로 'api'로 지정하지 않는 한
대시보드는 standalone(직접 외부 API 호출) 모드로 동작한다.
이는 사용자가 별도의 FastAPI 백엔드를 띄우지 않고도 즉시 사용 가능하도록 보장한다.
"""
import os

try:
    # 로컬 실행 시 .env 파일을 실제 프로세스 환경변수로 로드 — 이게 없으면 아래 모든
    # os.getenv() 키 조회가 .env 파일 내용을 못 읽는다(2026-07-23 발견: 지금까지
    # NAVER/OpenWeather/YouTube 키도 로컬에선 이 이유로 전부 미적용 상태였음).
    # HF Spaces 등 .env 파일이 없는 배포 환경에서는 조용히 스킵된다(no-op).
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

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

# 국토교통부 아파트매매 실거래가 (선택) — 키 있으면 부동산 페이지에서 실제 시세 조회 가능.
# 키 없으면 시세 조회 섹션은 안내 메시지만 표시하고 나머지 기능은 그대로 동작.
# 발급: https://www.data.go.kr/data/15126469/openapi.do → 활용신청(자동승인) → 마이페이지
#       개발계정에서 Decoding 키 확인 (무료, 개발계정 일 10,000건)
MOLIT_API_KEY = os.getenv("MOLIT_API_KEY", "")
HAS_MOLIT = bool(MOLIT_API_KEY)
