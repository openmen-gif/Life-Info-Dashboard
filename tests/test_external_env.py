# -*- coding: utf-8 -*-
"""OneDrive 밖 비밀 키 파일(LIFE_INFO_ENV_FILE) 로딩 테스트 (네트워크·실제 키 불필요)."""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.config import _external_env_path, load_external_env

_KEY = "LIFE_INFO_TEST_FAKE_KEY"


def test_reads_value_from_env_file(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text(f"{_KEY}=fake-value-123\n", encoding="utf-8")
    monkeypatch.setenv("LIFE_INFO_ENV_FILE", str(env_file))
    monkeypatch.delenv(_KEY, raising=False)

    assert load_external_env() is True
    assert os.environ[_KEY] == "fake-value-123"
    monkeypatch.delenv(_KEY, raising=False)


def test_missing_file_is_noop(tmp_path, monkeypatch):
    monkeypatch.setenv("LIFE_INFO_ENV_FILE", str(tmp_path / "없음" / ".env"))
    monkeypatch.delenv(_KEY, raising=False)

    assert load_external_env() is False
    assert _KEY not in os.environ


def test_does_not_override_existing_env(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text(f"{_KEY}=from-file\n", encoding="utf-8")
    monkeypatch.setenv("LIFE_INFO_ENV_FILE", str(env_file))
    monkeypatch.setenv(_KEY, "already-set")

    assert load_external_env() is True
    assert os.environ[_KEY] == "already-set"


def test_default_path_under_home(monkeypatch):
    monkeypatch.delenv("LIFE_INFO_ENV_FILE", raising=False)
    path = _external_env_path()
    assert path.parts[-3:] == ("_local_secrets", "life-info-dashboard", ".env")
