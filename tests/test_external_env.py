# -*- coding: utf-8 -*-
"""OneDrive 밖 비밀 키 파일(LIFE_INFO_ENV_FILE) 로딩 테스트 (네트워크·실제 키 불필요)."""
import importlib
import os
import sys
from pathlib import Path

import dotenv
import pytest

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
    expected = Path.home() / "_local_secrets" / "life-info-dashboard" / ".env"
    assert _external_env_path() == expected


def test_keeps_existing_empty_string(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text(f"{_KEY}=from-file\n", encoding="utf-8")
    monkeypatch.setenv("LIFE_INFO_ENV_FILE", str(env_file))
    monkeypatch.setenv(_KEY, "")

    assert load_external_env() is True
    assert os.environ[_KEY] == ""


def test_project_env_wins_over_external(tmp_path, monkeypatch):
    """config 와 같은 순서(프로젝트 .env → 외부 파일)로 읽으면 프로젝트 값이 남는다."""
    from dotenv import load_dotenv

    project = tmp_path / "project.env"
    project.write_text(f"{_KEY}=from-project\n", encoding="utf-8")
    external = tmp_path / "external.env"
    external.write_text(
        f"{_KEY}=from-external\n{_KEY}_ONLY_EXT=ext-only\n", encoding="utf-8"
    )
    monkeypatch.setenv("LIFE_INFO_ENV_FILE", str(external))
    monkeypatch.delenv(_KEY, raising=False)
    monkeypatch.delenv(f"{_KEY}_ONLY_EXT", raising=False)

    load_dotenv(project, override=False)
    assert load_external_env() is True
    assert os.environ[_KEY] == "from-project"
    assert os.environ[f"{_KEY}_ONLY_EXT"] == "ext-only"
    monkeypatch.delenv(_KEY, raising=False)
    monkeypatch.delenv(f"{_KEY}_ONLY_EXT", raising=False)


def test_invalid_encoding_warns_and_returns_false(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_bytes(b"LIFE_INFO_TEST_FAKE_KEY=\xff\xfe\xfa\n")
    monkeypatch.setenv("LIFE_INFO_ENV_FILE", str(env_file))
    monkeypatch.delenv(_KEY, raising=False)

    with pytest.warns(RuntimeWarning) as record:
        assert load_external_env() is False
    assert _KEY not in os.environ
    # 경고에 값·내용이 들어가지 않음
    assert "�" not in str(record[0].message)


@pytest.mark.parametrize(
    "exc",
    [
        PermissionError("가짜 권한 오류"),
        FileNotFoundError("확인 뒤 사라짐"),
        UnicodeDecodeError("utf-8", b"\xff", 0, 1, "가짜"),
    ],
)
def test_read_errors_do_not_propagate(tmp_path, monkeypatch, exc):
    env_file = tmp_path / ".env"
    env_file.write_text(f"{_KEY}=secret-like\n", encoding="utf-8")
    monkeypatch.setenv("LIFE_INFO_ENV_FILE", str(env_file))

    def _boom(*args, **kwargs):
        raise exc

    monkeypatch.setattr(dotenv, "load_dotenv", _boom)
    with pytest.warns(RuntimeWarning) as record:
        assert load_external_env() is False
    assert "secret-like" not in str(record[0].message)


def test_home_lookup_failure_does_not_propagate(monkeypatch):
    monkeypatch.delenv("LIFE_INFO_ENV_FILE", raising=False)

    def _no_home():
        raise RuntimeError("홈 경로 없음")

    monkeypatch.setattr(Path, "home", staticmethod(_no_home))
    with pytest.warns(RuntimeWarning):
        assert load_external_env() is False


def test_config_reimport_survives_read_error(tmp_path, monkeypatch):
    """모듈 최상위 호출에서 읽기 오류가 나도 config import 가 성공한다."""
    env_file = tmp_path / ".env"
    env_file.write_bytes(b"X=\xff\n")
    monkeypatch.setenv("LIFE_INFO_ENV_FILE", str(env_file))
    import utils.config as cfg

    with pytest.warns(RuntimeWarning):
        importlib.reload(cfg)
    assert cfg.MODE
