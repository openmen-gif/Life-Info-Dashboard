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
