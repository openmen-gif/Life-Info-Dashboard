---
title: Life Info Dashboard
emoji: 🏠
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
---

# Life Info Dashboard

27개 분야 생활정보 AI 대시보드

## 로컬 비밀 키 위치

- 로컬 실행 시 API 키는 `~/_local_secrets/life-info-dashboard/.env`(OneDrive 밖)에서 추가로 읽어요. 다른 경로는 `LIFE_INFO_ENV_FILE` 환경변수로 지정해요.
- 앱 폴더의 `.env`와 이미 설정된 환경변수가 우선이고, 외부 파일은 빈 값만 채워요(덮어쓰지 않음).
- HF Spaces 배포에서는 이 파일이 없으므로 Space 시크릿(환경변수)을 그대로 써요.
