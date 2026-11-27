# -*- coding: utf-8 -*-
"""국토교통부 아파트매매 실거래가 Open API 연동.

API 명세(data.go.kr 스웨거 문서 2026-07-23 확인 기준):
  Base URL: https://apis.data.go.kr/1613000/RTMSDataSvcAptTrade
  Endpoint: GET /getRTMSDataSvcAptTrade
  Params  : LAWD_CD(법정동코드 앞5자리), DEAL_YMD(계약년월 6자리), serviceKey
  응답 item 필드: aptNm, umdNm, jibun, excluUseAr, dealAmount, floor,
                 buildYear, dealYear, dealMonth, dealDay
데이터포맷이 XML로 고정 등록되어 있어 XML로 요청·파싱한다.
"""
import datetime
import threading
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

import requests

from utils.config import MOLIT_API_KEY

MOLIT_BASE_URL = "https://apis.data.go.kr/1613000/RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade"

# 성공 결과만 보관하는 경량 TTL 캐시 — API 장애(code=04 등) 빈 결과가 1시간 캐시되는 문제 차단 +
# HF 무료 컨테이너 메모리 보호를 위해 최대 엔트리 수를 제한한다.
_CACHE_TTL_SEC = 3600
_CACHE_MAX_ENTRIES = 32
_REGION_CACHE: dict[tuple[str, int], tuple[float, list[dict]]] = {}
_CACHE_LOCK = threading.Lock()

# 법정동코드(시군구 단위, 앞 5자리). 서울 25개구·6대 광역시·세종은 전수,
# 그 외 도 단위는 주요 시·군 위주로 담았다 — 행정구역 개편으로 최신 코드가
# 다를 수 있어, 목록에 없거나 조회가 안 되는 지역은 알려주면 추가한다.
LAWD_CODES: dict[str, dict[str, str]] = {
    "서울특별시": {
        "종로구": "11110", "중구": "11140", "용산구": "11170", "성동구": "11200",
        "광진구": "11215", "동대문구": "11230", "중랑구": "11260", "성북구": "11290",
        "강북구": "11305", "도봉구": "11320", "노원구": "11350", "은평구": "11380",
        "서대문구": "11410", "마포구": "11440", "양천구": "11470", "강서구": "11500",
        "구로구": "11530", "금천구": "11545", "영등포구": "11560", "동작구": "11590",
        "관악구": "11620", "서초구": "11650", "강남구": "11680", "송파구": "11710",
        "강동구": "11740",
    },
    "부산광역시": {
        "중구": "26110", "서구": "26140", "동구": "26170", "영도구": "26200",
        "부산진구": "26230", "동래구": "26260", "남구": "26290", "북구": "26320",
        "해운대구": "26350", "사하구": "26380", "금정구": "26410", "강서구": "26440",
        "연제구": "26470", "수영구": "26500", "사상구": "26530", "기장군": "26710",
    },
    "대구광역시": {
        "중구": "27110", "동구": "27140", "서구": "27170", "남구": "27200",
        "북구": "27230", "수성구": "27260", "달서구": "27290", "달성군": "27710",
    },
    "인천광역시": {
        "중구": "28110", "동구": "28140", "미추홀구": "28177", "연수구": "28185",
        "남동구": "28200", "부평구": "28237", "계양구": "28245", "서구": "28260",
        "강화군": "28710", "옹진군": "28720",
    },
    "광주광역시": {
        "동구": "29110", "서구": "29140", "남구": "29155", "북구": "29170", "광산구": "29200",
    },
    "대전광역시": {
        "동구": "30110", "중구": "30140", "서구": "30170", "유성구": "30200", "대덕구": "30230",
    },
    "울산광역시": {
        "중구": "31110", "남구": "31140", "동구": "31170", "북구": "31200", "울주군": "31710",
    },
    "세종특별자치시": {"세종시": "36110"},
    "경기도": {
        "수원시 장안구": "41111", "수원시 권선구": "41113", "수원시 팔달구": "41115",
        "수원시 영통구": "41117", "성남시 수정구": "41131", "성남시 중원구": "41133",
        "성남시 분당구": "41135", "의정부시": "41150", "안양시 만안구": "41171",
        "안양시 동안구": "41173", "부천시": "41190", "광명시": "41210", "평택시": "41220",
        "동두천시": "41250", "안산시 상록구": "41271", "안산시 단원구": "41273",
        "고양시 덕양구": "41281", "고양시 일산동구": "41285", "고양시 일산서구": "41287",
        "과천시": "41290", "구리시": "41310", "남양주시": "41360", "오산시": "41370",
        "시흥시": "41390", "군포시": "41410", "의왕시": "41430", "하남시": "41450",
        "용인시 처인구": "41461", "용인시 기흥구": "41463", "용인시 수지구": "41465",
        "파주시": "41480", "이천시": "41500", "안성시": "41550", "김포시": "41570",
        "화성시": "41590", "광주시": "41610", "양주시": "41630", "포천시": "41650",
        "여주시": "41670", "연천군": "41800", "가평군": "41820", "양평군": "41830",
    },
    "강원특별자치도": {
        "춘천시": "51110", "원주시": "51130", "강릉시": "51150", "동해시": "51170",
        "태백시": "51190", "속초시": "51210", "삼척시": "51230",
    },
    "충청북도": {
        "청주시 상당구": "43111", "청주시 서원구": "43112", "청주시 흥덕구": "43113",
        "청주시 청원구": "43114", "충주시": "43130", "제천시": "43150",
    },
    "충청남도": {
        "천안시 동남구": "44131", "천안시 서북구": "44133", "공주시": "44150",
        "보령시": "44180", "아산시": "44200", "서산시": "44210", "논산시": "44230",
        "계룡시": "44250", "당진시": "44270",
    },
    "전북특별자치도": {
        "전주시 완산구": "52111", "전주시 덕진구": "52113", "군산시": "52130",
        "익산시": "52140", "정읍시": "52180", "남원시": "52190", "김제시": "52210",
    },
    "전라남도": {
        "목포시": "46110", "여수시": "46130", "순천시": "46150", "나주시": "46170",
        "광양시": "46230",
    },
    "경상북도": {
        "포항시 남구": "47111", "포항시 북구": "47113", "경주시": "47130",
        "김천시": "47150", "안동시": "47170", "구미시": "47190", "영주시": "47210",
        "경산시": "47290",
    },
    "경상남도": {
        "창원시 의창구": "48121", "창원시 성산구": "48123", "창원시 마산합포구": "48125",
        "창원시 마산회원구": "48127", "창원시 진해구": "48129", "진주시": "48170",
        "통영시": "48220", "사천시": "48240", "김해시": "48250", "밀양시": "48270",
        "거제시": "48310", "양산시": "48330",
    },
    "제주특별자치도": {"제주시": "50110", "서귀포시": "50130"},
}


def _text(item: "ET.Element", tag: str) -> str:
    v = item.findtext(tag)
    return v.strip() if v else ""


def _parse_amount(raw: str) -> int:
    """'  35,000' 형태(공백·콤마 포함, 만원 단위) 금액 문자열 → 정수."""
    if not raw:
        return 0
    try:
        return int(raw.replace(",", "").strip())
    except ValueError:
        return 0


def clear_region_cache() -> None:
    """테스트 및 수동 재시도용 지역 실거래 캐시 초기화."""
    with _CACHE_LOCK:
        _REGION_CACHE.clear()


def _format_api_error(code: str | None, msg: str | None, http_status: int | None = None) -> str:
    """공공데이터포털·국토부 API 오류 코드를 사용자 안내 문구로 변환한다."""
    code_s = (code or "").strip()
    msg_s = (msg or "").strip()
    if code_s == "04":
        return "국토교통부 실거래가 API 일시 장애/점검 중입니다 (코드 04: HTTP_ERROR)."
    if code_s == "22":
        return "국토교통부 실거래가 API 일일 호출 한도를 초과했습니다 (코드 22)."
    if code_s in ("30", "31", "32") or http_status in (401, 403):
        return f"국토교통부 실거래가 API 인증 키 오류입니다 (코드 {code_s or http_status})."
    if code_s:
        detail = f"{code_s}: {msg_s}" if msg_s else code_s
        return f"국토교통부 실거래가 API 오류가 발생했습니다 ({detail})."
    if http_status and http_status >= 400:
        return f"국토교통부 실거래가 API 응답 오류입니다 (HTTP {http_status})."
    return "국토교통부 실거래가 API 연결에 실패했습니다."


def _fetch_month_detail(lawd_cd: str, deal_ymd: str) -> tuple[list[dict], str | None]:
    """단일 (지역, 계약년월) 실거래 내역과 오류 사유를 함께 반환한다."""
    if not MOLIT_API_KEY:
        return [], "국토교통부 실거래가 API 키가 설정되지 않았습니다."
    params = {
        "serviceKey": MOLIT_API_KEY,
        "LAWD_CD": lawd_cd,
        "DEAL_YMD": deal_ymd,
        "numOfRows": 999,
        "pageNo": 1,
    }
    try:
        r = requests.get(MOLIT_BASE_URL, params=params, timeout=10)
        http_status = r.status_code
        root = None
        try:
            root = ET.fromstring(r.content)
        except ET.ParseError:
            root = None

        if root is not None:
            # 공공데이터포털 게이트웨이 오류는 cmmMsgHeader(returnReasonCode/errMsg)로 내려온다.
            gw_code = root.findtext(".//cmmMsgHeader/returnReasonCode")
            gw_msg = root.findtext(".//cmmMsgHeader/errMsg") or root.findtext(".//cmmMsgHeader/returnAuthMsg")
            if gw_code and gw_code not in ("000", "00", "0"):
                return [], _format_api_error(gw_code, gw_msg, http_status)

            result_code = root.findtext("./header/resultCode")
            result_msg = root.findtext("./header/resultMsg")
            if result_code not in (None, "000", "00", "0"):  # 실제 API 성공 코드는 "000"(2026-07-23 실측 확인)
                return [], _format_api_error(result_code, result_msg, http_status)

        if http_status >= 400:
            return [], _format_api_error(None, None, http_status)
        if root is None:
            return [], "국토교통부 실거래가 API 응답 형식을 해석하지 못했습니다."

        records = []
        for item in root.findall("./body/items/item"):
            y, m, d = _text(item, "dealYear"), _text(item, "dealMonth"), _text(item, "dealDay")
            if not (y and m and d):
                continue
            try:
                excl_ar = float(_text(item, "excluUseAr") or 0)
            except ValueError:
                excl_ar = 0.0
            records.append({
                "아파트명": _text(item, "aptNm"),
                "법정동": _text(item, "umdNm"),
                "전용면적": excl_ar,
                "층": _text(item, "floor"),
                "건축년도": _text(item, "buildYear"),
                "거래금액_만원": _parse_amount(_text(item, "dealAmount")),
                "계약일": f"{y}-{m.zfill(2)}-{d.zfill(2)}",
            })
        return records, None
    except requests.Timeout:
        return [], "국토교통부 실거래가 API 응답 시간이 초과되었습니다."
    except Exception:
        return [], "국토교통부 실거래가 API 연결 중 오류가 발생했습니다."


def _fetch_month(lawd_cd: str, deal_ymd: str) -> list[dict]:
    """단일 (지역, 계약년월) 실거래 내역 조회. 실패·키없음이면 빈 리스트(하위 호환)."""
    records, _ = _fetch_month_detail(lawd_cd, deal_ymd)
    return records


def _recent_deal_ymds(months: int) -> list[str]:
    today = datetime.date.today()
    y, m = today.year, today.month
    out = []
    for _ in range(months):
        out.append(f"{y}{m:02d}")
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    return out


def _fetch_region_history_with_status(lawd_cd: str, months: int) -> tuple[list[dict], str | None]:
    """최근 N개월 지역 실거래 내역과 오류 상태를 반환한다.

    모든 월 요청이 오류로 실패한 경우에는 캐시에 저장하지 않아,
    외부 API 복구 직후 즉시 정상 재조회되도록 보장한다.
    """
    cache_key = (lawd_cd, months)
    now_mono = time.monotonic()
    with _CACHE_LOCK:
        cached = _REGION_CACHE.get(cache_key)
        if cached and (now_mono - cached[0]) < _CACHE_TTL_SEC:
            return list(cached[1]), None

    deal_ymds = _recent_deal_ymds(months)
    all_records: list[dict] = []
    errors: list[str] = []
    ok_months = 0

    with ThreadPoolExecutor(max_workers=min(len(deal_ymds), 2)) as executor:
        futures = [executor.submit(_fetch_month_detail, lawd_cd, ymd) for ymd in deal_ymds]
        for future in futures:
            try:
                recs, err = future.result(timeout=15)
            except Exception:
                errors.append("국토교통부 실거래가 API 응답 시간이 초과되었습니다.")
                continue
            if err:
                errors.append(err)
            else:
                ok_months += 1
                all_records.extend(recs)

    # 정상 응답을 1개월도 못 받고 오류만 발생한 경우: 캐시하지 않고 오류 사유를 그대로 반환
    if ok_months == 0 and errors:
        return [], errors[0]

    with _CACHE_LOCK:
        if len(_REGION_CACHE) >= _CACHE_MAX_ENTRIES:
            oldest_key = min(_REGION_CACHE, key=lambda k: _REGION_CACHE[k][0])
            _REGION_CACHE.pop(oldest_key, None)
        _REGION_CACHE[cache_key] = (time.monotonic(), list(all_records))
    return all_records, None


def _fetch_region_history(lawd_cd: str, months: int) -> list[dict]:
    """최근 N개월, 해당 지역의 단지명 필터 없는 전체 실거래 내역(하위 호환)."""
    records, _ = _fetch_region_history_with_status(lawd_cd, months)
    return records


def _name_tokens(apt_name: str) -> list[str]:
    return [t for t in apt_name.strip().split() if t]


def fetch_apt_trade_history_with_status(
    lawd_cd: str, apt_name: str, months: int = 12
) -> tuple[list[dict], str | None]:
    """최근 N개월 실거래 내역과 API 오류 상태를 함께 반환한다."""
    all_records, error = _fetch_region_history_with_status(lawd_cd, months)
    if error:
        return [], error
    tokens = _name_tokens(apt_name)
    if tokens:
        # 실거래 자료는 동명 단지 구분을 위해 "현대(고덕)"처럼 지역명을 괄호로 뒤에 붙이는
        # 경우가 많아, 사용자가 익숙한 "고덕 현대" 어순으로 입력하면 단순 부분일치로는
        # 못 찾는다 — 공백으로 나눈 각 단어가 순서·위치 무관하게 전부 포함되면 매칭.
        all_records = [
            r for r in all_records
            if all(t in r["아파트명"] for t in tokens)
        ]
    all_records.sort(key=lambda r: r["계약일"])
    return all_records, None


def fetch_apt_trade_history(lawd_cd: str, apt_name: str, months: int = 12) -> list[dict]:
    """최근 N개월 실거래 내역 중 단지명이 일치하는 거래만 모아 계약일 오름차순으로 반환."""
    records, _ = fetch_apt_trade_history_with_status(lawd_cd, apt_name, months=months)
    return records


def list_apt_names_with_status(lawd_cd: str, months: int = 12) -> tuple[list[str], str | None]:
    """해당 지역 실제 거래 단지명 목록과 API 오류 상태를 함께 반환한다."""
    all_records, error = _fetch_region_history_with_status(lawd_cd, months)
    if error:
        return [], error
    return sorted({r["아파트명"] for r in all_records}), None


def list_apt_names(lawd_cd: str, months: int = 12) -> list[str]:
    """해당 지역에서 실제로 거래된 단지명 전체 목록(가나다순) — 검색 가능한 선택창 채우기용.

    "고덕현대"처럼 사용자가 실제 등록명("현대(고덕)")을 몰라 못 찾는 문제를 원천 차단한다:
    자유 입력 대신 이 목록에서 고르게 하면 오타·어순 문제 자체가 생기지 않는다."""
    names, _ = list_apt_names_with_status(lawd_cd, months=months)
    return names


def find_similar_apt_names(lawd_cd: str, apt_name: str, months: int = 12, limit: int = 8) -> list[str]:
    """검색어가 0건일 때 후보 제시용 — 입력 단어 중 1개라도 포함하는 실제 단지명을
    매칭 단어 수 많은 순 -> 이름 순으로 최대 limit개 반환."""
    tokens = _name_tokens(apt_name)
    if not tokens:
        return []
    all_records = _fetch_region_history(lawd_cd, months)
    names = {r["아파트명"] for r in all_records}
    scored = [
        (sum(1 for t in tokens if t in n), n)
        for n in names
        if any(t in n for t in tokens)
    ]
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [n for _, n in scored[:limit]]
