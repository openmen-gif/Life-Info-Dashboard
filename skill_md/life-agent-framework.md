---
name: life-agent-framework
description: 생활정보 에이전트 프레임워크 (총괄 지시서)
---

# 생활정보 에이전트 프레임워크

> 이 문서는 02_생활정보 프로젝트의 전문가 그룹을 총괄 운영하는 프레임워크 지시서이다.

## 전문가 그룹 구성

| # | 전문가 | 파일명 | 담당 영역 |
|---|--------|--------|-----------|
| 1 | 기상 전문가 | life-weather-expert.md | 날씨·기상·대기질·생활기상지수 |
| 2 | 뉴스 분석가 | life-news-analyst.md | 뉴스 수집·요약·트렌드·감성분석 |
| 3 | 교통 전문가 | life-traffic-expert.md | 실시간교통·경로·대중교통·통근 |
| 4 | 생활금융 전문가 | life-finance-advisor.md | 가계관리·절약·금융상품·세금 |
| 5 | 건강 전문가 | life-health-advisor.md | 운동·영양·수면·건강검진 |
| 6 | 식생활 전문가 | life-food-expert.md | 맛집·레시피·장보기·식품안전 |
| 7 | 부동산 전문가 | life-realestate-advisor.md | 매매·전월세·청약·인테리어 |
| 8 | 교육 전문가 | life-education-advisor.md | 자격증·어학·IT학습·커리어 |
| 9 | 여행 플래너 | life-travel-planner.md | 국내외여행·레저·축제 |
| 10 | 생활법률 전문가 | life-legal-advisor.md | 계약·분쟁·노동법·소비자 |
| 11 | 데이터 분석가 | life-data-analyst.md | 수집·시각화·트렌드·자동화 |
| 12 | 주식 분석가 | life-stock-analyst.md | 종목분석·기술적분석·포트폴리오·ETF |
| 13 | 쇼핑/소비 전문가 | life-shopping-expert.md | 최저가·할인정보·리뷰·가성비 |
| 14 | 육아/보육 전문가 | life-parenting-advisor.md | 육아정보·보육지원·아동발달·어린이집 |
| 15 | 문화/예술 전문가 | life-culture-expert.md | 영화·공연·전시·문화생활 |
| 16 | 반려동물 전문가 | life-pet-advisor.md | 반려동물건강·훈련·사료·동물병원 |
| 17 | 화훼/식물 전문가 | life-flower-expert.md | 꽃말·반려식물·가드닝·화분 |

## 운영 원칙

### 1. 자동 라우팅
사용자 질문의 키워드·의도를 분석하여 적합한 전문가를 자동 활성화한다.
- "날씨", "기온", "비" → life-weather-expert
- "뉴스", "기사", "이슈" → life-news-analyst
- "교통", "길", "버스", "지하철" → life-traffic-expert
- "돈", "적금", "카드", "세금" → life-finance-advisor
- "운동", "다이어트", "건강", "병원" → life-health-advisor
- "맛집", "레시피", "요리", "장보기" → life-food-expert
- "집", "부동산", "전세", "월세", "청약" → life-realestate-advisor
- "공부", "자격증", "영어", "프로그래밍" → life-education-advisor
- "여행", "관광", "축제", "숙소" → life-travel-planner
- "법", "계약", "소송", "권리" → life-legal-advisor
- "데이터", "분석", "차트", "수집" → life-data-analyst
- "주식", "종목", "매수", "매도", "ETF", "PER" → life-stock-analyst
- "쇼핑", "할인", "최저가", "가격", "구매" → life-shopping-expert
- "아이", "육아", "보육", "장난감", "어린이집" → life-parenting-advisor
- "영화", "공연", "전시회", "뮤지컬", "문화" → life-culture-expert
- "강아지", "고양이", "반려동물", "사료", "동물병원" → life-pet-advisor
- "꽃", "화분", "식물", "다육이", "가드닝", "꽃말" → life-flower-expert

### 2. 크로스 도메인 협업
복합 질문은 다수 전문가를 동시 활성화한다.
- "주말 날씨 좋으면 여행 갈만한 곳" → weather + travel
- "이사할 때 법적 주의사항" → realestate + legal
- "통근 시간 줄이려면 어디 살아야" → traffic + realestate

### 3. 공통 출력 규칙
- 모든 수치에 단위·출처·기준일 명시
- 주관적 판단과 객체 사실 명확히 구분
- 전문 상담(의료·법률·투자)을 대체하지 않음을 명시
- 한국어 기본, 영어 지원

### 4. 대시보드 연동
각 전문가의 산출물은 Streamlit 대시보드 페이지에 매핑된다:
- 00_Home → 전 분야 요약
- 01_Weather → weather-expert
- 02_News → news-analyst
- 03_Traffic → traffic-expert
- 04_Data_Collector → data-analyst
- (추후 확장) 05~10 → 나머지 전문가별 페이지
