# -*- coding: utf-8 -*-
"""국토교통부 아파트 실거래가 API 오류 분리 및 실패 캐시 방지 회귀 테스트."""
from unittest.mock import Mock

from utils import realestate_fetcher as rf


def _xml_resp(body: str, status_code: int = 200) -> Mock:
    r = Mock()
    r.status_code = status_code
    r.content = body.encode("utf-8")
    return r


def test_gateway_error_04_returns_error_and_is_not_cached(monkeypatch):
    rf.clear_region_cache()
    monkeypatch.setattr(rf, "MOLIT_API_KEY", "dummy-key")
    err_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <OpenAPI_ServiceResponse>
      <cmmMsgHeader>
        <errMsg>HTTP_ERROR</errMsg>
        <returnAuthMsg>HTTP 에러</returnAuthMsg>
        <returnReasonCode>04</returnReasonCode>
      </cmmMsgHeader>
    </OpenAPI_ServiceResponse>"""
    mock_get = Mock(return_value=_xml_resp(err_xml, 200))
    monkeypatch.setattr(rf.requests, "get", mock_get)

    names, err = rf.list_apt_names_with_status("11140", months=2)
    assert names == []
    assert err is not None and "코드 04" in err
    assert mock_get.call_count == 2

    # 실패 결과는 캐시되지 않으므로 다음 호출 시 즉시 재시도해야 한다.
    names2, err2 = rf.list_apt_names_with_status("11140", months=2)
    assert names2 == []
    assert err2 is not None
    assert mock_get.call_count == 4


def test_success_response_returns_names_and_uses_cache(monkeypatch):
    rf.clear_region_cache()
    monkeypatch.setattr(rf, "MOLIT_API_KEY", "dummy-key")
    ok_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <response>
      <header><resultCode>000</resultCode><resultMsg>OK</resultMsg></header>
      <body><items>
        <item>
          <aptNm>남산타운</aptNm><umdNm>신당동</umdNm><excluUseAr>84.88</excluUseAr>
          <floor>10</floor><buildYear>2002</buildYear><dealAmount>125,000</dealAmount>
          <dealYear>2026</dealYear><dealMonth>10</dealMonth><dealDay>5</dealDay>
        </item>
      </items></body>
    </response>"""
    mock_get = Mock(return_value=_xml_resp(ok_xml, 200))
    monkeypatch.setattr(rf.requests, "get", mock_get)

    names, err = rf.list_apt_names_with_status("11140", months=2)
    assert err is None
    assert names == ["남산타운"]
    assert mock_get.call_count == 2

    # 성공 결과는 캐시되므로 추가 HTTP 호출이 없어야 한다.
    records, err2 = rf.fetch_apt_trade_history_with_status("11140", "남산타운", months=2)
    assert err2 is None
    assert len(records) == 2
    assert records[0]["거래금액_만원"] == 125000
    assert mock_get.call_count == 2


def test_success_empty_records_returns_no_error(monkeypatch):
    rf.clear_region_cache()
    monkeypatch.setattr(rf, "MOLIT_API_KEY", "dummy-key")
    empty_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <response>
      <header><resultCode>000</resultCode><resultMsg>OK</resultMsg></header>
      <body><items></items></body>
    </response>"""
    monkeypatch.setattr(rf.requests, "get", Mock(return_value=_xml_resp(empty_xml, 200)))

    names, err = rf.list_apt_names_with_status("11140", months=1)
    assert names == []
    assert err is None


def test_http_403_invalid_key_returns_auth_error(monkeypatch):
    rf.clear_region_cache()
    monkeypatch.setattr(rf, "MOLIT_API_KEY", "dummy-key")
    err_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <OpenAPI_ServiceResponse>
      <cmmMsgHeader>
        <errMsg>SERVICE_KEY_IS_NOT_REGISTERED_ERROR</errMsg>
        <returnReasonCode>30</returnReasonCode>
      </cmmMsgHeader>
    </OpenAPI_ServiceResponse>"""
    monkeypatch.setattr(rf.requests, "get", Mock(return_value=_xml_resp(err_xml, 403)))

    names, err = rf.list_apt_names_with_status("11140", months=1)
    assert names == []
    assert err is not None and "인증 키 오류" in err
