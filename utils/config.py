"""Environment mode detection for dual-mode architecture."""
import os

_space = os.getenv("SPACE_ID")
_explicit = os.getenv("LIFE_MODE")

if _explicit:
    MODE = _explicit.lower()
elif _space:
    MODE = "standalone"
else:
    MODE = "api"

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8001/api/v1")
IS_API_MODE = (MODE == "api")
