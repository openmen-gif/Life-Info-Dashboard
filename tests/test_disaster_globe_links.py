# -*- coding: utf-8 -*-
"""재난·안전(10종) 및 사이버보안(1종) 3D 지구본 모니터 링크 회귀 테스트.

2026-11-20 sync-to-hf.yml 의 --force 푸시로 지구본 모니터 링크 11종이 일괄 소실된
사고의 재발을 막기 위해, 모든 지구본 URL 존재와 워크플로 비강제 푸시 정책을 검증한다.
"""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATIC_BASE = "https://openmen-gif.github.io/life-info-static"

EXPECTED_SAFETY_MONITORS = [
    "global_seismic_monitor.html",
    "typhoon_monitor.html",
    "wildfire_monitor.html",
    "flood_monitor.html",
    "drought_monitor.html",
    "volcano_monitor.html",
    "tsunami_monitor.html",
    "airquality_monitor.html",
    "spaceweather_monitor.html",
    "radiation_monitor.html",
]

EXPECTED_CYBER_MONITORS = [
    "cyber_threat_monitor.html",
]


def test_safety_view_contains_all_ten_disaster_globe_links():
    src = (ROOT / "views" / "33_Safety.py").read_text(encoding="utf-8")
    assert STATIC_BASE in src
    for filename in EXPECTED_SAFETY_MONITORS:
        assert filename in src, f"views/33_Safety.py 에 {filename} 링크가 누락되었습니다."


def test_cybersecurity_view_contains_cyberwatch_globe_link():
    src = (ROOT / "views" / "36_CyberSecurity.py").read_text(encoding="utf-8")
    for filename in EXPECTED_CYBER_MONITORS:
        expected_url = f"{STATIC_BASE}/{filename}"
        assert expected_url in src, f"views/36_CyberSecurity.py 에 {expected_url} 링크가 누락되었습니다."


def test_stock_view_preserves_finviz_and_kr_heatmap_links():
    # PR #3(life-stock-finviz) 변경이 회귀 없이 보존되는지 함께 확인한다.
    src = (ROOT / "views" / "12_Stock.py").read_text(encoding="utf-8")
    for url in (
        "https://etfshopping.com/treemap",
        "https://finviz.com/map",
        "https://finviz.com/map?t=sec_ndx",
    ):
        assert url in src, f"views/12_Stock.py 에 기존 히트맵 링크 {url} 가 누락되었습니다."


def test_sync_workflow_does_not_force_push_to_hf():
    workflow = (ROOT / ".github" / "workflows" / "sync-to-hf.yml").read_text(encoding="utf-8")
    push_lines = [
        line.strip()
        for line in workflow.splitlines()
        if "git push" in line and not line.strip().startswith("#")
    ]
    assert push_lines, "sync-to-hf.yml 에 git push 명령이 없습니다."
    for line in push_lines:
        assert "--force" not in line and " -f" not in line, (
            f"sync-to-hf.yml 이 HF 원격에 강제 푸시를 사용합니다: {line}"
        )
