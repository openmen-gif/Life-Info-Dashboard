# -*- coding: utf-8 -*-
"""배포 환경의 날씨 실패 지연과 영상 자동 표시 회귀 테스트."""
import inspect
from pathlib import Path

from utils import data_fetcher
from utils.expert_template import render_youtube_section


def test_weather_series_limits_failed_requests_to_two_five_second_attempts(monkeypatch):
    calls = []

    def fail_get(*args, **kwargs):
        calls.append(kwargs.get("timeout"))
        raise TimeoutError("deployment egress timeout")

    monkeypatch.setattr(data_fetcher.requests, "get", fail_get)
    result = data_fetcher.fetch_weather_series.__wrapped__("서울")

    assert result["ok"] is False
    assert calls == [5, 5]


def test_weather_video_section_requests_automatic_loading():
    signature = inspect.signature(render_youtube_section)
    assert signature.parameters["auto_load"].default is False

    source = (Path(__file__).parents[1] / "views" / "01_Weather.py").read_text(encoding="utf-8")
    assert 'render_youtube_section("오늘 날씨 일기예보", sort="latest", auto_load=True)' in source
