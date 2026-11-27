# -*- coding: utf-8 -*-
"""테스트 격리: utils.config import 시 실제 홈의 비밀 키 파일을 읽지 않도록
LIFE_INFO_ENV_FILE 을 존재하지 않는 경로로 고정한다(테스트 수집 전에 실행됨)."""
import os
import tempfile

os.environ["LIFE_INFO_ENV_FILE"] = os.path.join(
    tempfile.gettempdir(), "life-info-test-없는-경로", ".env"
)
