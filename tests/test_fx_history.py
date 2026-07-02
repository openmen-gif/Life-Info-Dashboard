# -*- coding: utf-8 -*-
"""fetch_fx_history 순수 헬퍼 단위 테스트 (네트워크 불필요).
실행: python tests/test_fx_history.py   (pytest 로도 실행 가능)"""
import os
import sys

# dashboard 루트를 import 경로에 추가 (utils 패키지 해석)
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.data_fetcher import _fx_period_to_days, _parse_frankfurter_timeseries


def test_period_to_days():
    assert _fx_period_to_days("5d") == 7
    assert _fx_period_to_days("1y") == 370
    assert _fx_period_to_days("unknown") == 35  # 기본값


def test_parse_sorts_ascending_and_filters_nonpositive():
    payload = {
        "base": "USD",
        "rates": {
            "2026-06-30": {"KRW": 1550.89, "EUR": 0.87765},
            "2026-06-25": {"KRW": 1542.92, "EUR": 0.88168},
            "2026-06-29": {"KRW": 0, "EUR": 0.87673},  # KRW 0 → 제외
        },
    }
    hist = _parse_frankfurter_timeseries(payload, ("KRW", "EUR"))
    assert [p["Date"] for p in hist["KRW"]] == ["2026-06-25", "2026-06-30"]
    assert hist["KRW"][0]["Close"] == 1542.92
    assert len(hist["EUR"]) == 3  # EUR 3개 모두 유효


def test_parse_empty_payload():
    assert _parse_frankfurter_timeseries({}, ("KRW",)) == {"KRW": []}


if __name__ == "__main__":
    _failed = 0
    for _name, _fn in sorted(globals().items()):
        if _name.startswith("test_") and callable(_fn):
            try:
                _fn()
                print(f"PASS {_name}")
            except AssertionError as e:
                _failed += 1
                print(f"FAIL {_name}: {e}")
    print("모든 테스트 통과" if _failed == 0 else f"{_failed}건 실패")
    sys.exit(1 if _failed else 0)
