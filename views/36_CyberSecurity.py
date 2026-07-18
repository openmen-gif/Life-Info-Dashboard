# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

# ── 긴급 신고·차단 채널 ────────────────────────────────────────────────────
st.markdown("## 🛡️ 보이스피싱·스미싱 신고 채널")
st.error("⚠️ **피해 의심 시 즉시 신고**: 보이스피싱 신고 **112** · 사이버범죄 신고 **182** · KISA 침해사고 **118**")

_rc1, _rc2, _rc3, _rc4 = st.columns(4)
with _rc1:
    st.link_button("🚨 보이스피싱 신고 (112)", "https://www.police.go.kr/", use_container_width=True)
with _rc2:
    st.link_button("💻 사이버범죄 신고센터 (182)", "https://ecrm.police.go.kr/", use_container_width=True)
with _rc3:
    st.link_button("🛡️ KISA 침해사고 신고 (118)", "https://www.kisa.or.kr/", use_container_width=True)
with _rc4:
    st.link_button("🏦 금감원 불법사금융 (1332)", "https://www.fss.or.kr/", use_container_width=True)

# ── 점검·차단 도구 ───────────────────────────────────────────────────────
st.markdown("### 🔐 점검·차단·확인 도구")
_tc1, _tc2, _tc3, _tc4 = st.columns(4)
with _tc1:
    st.link_button("🔐 개인정보 침해신고", "https://privacy.kisa.or.kr/", use_container_width=True)
with _tc2:
    st.link_button("📱 보호나라 (스미싱)", "https://www.boho.or.kr/", use_container_width=True)
with _tc3:
    st.link_button("🌐 후이즈 URL 확인", "https://whois.kisa.or.kr/", use_container_width=True)
with _tc4:
    st.link_button("📞 명의도용 차단 (M-safer)", "https://www.msafer.or.kr/", use_container_width=True)

# ── 자가 점검 체크리스트 ──────────────────────────────────────────────────
with st.expander("✅ 의심 문자·전화 즉시 점검 체크리스트 (펼쳐서 확인)", expanded=False):
    st.markdown("""
**📞 전화로 의심되는 경우**
- 검찰·경찰·금감원을 자처하면 **무조건 끊고 112** 직접 전화
- "당신의 계좌가 범죄에 연루됐다"는 말은 **100% 보이스피싱**
- 앱 설치·원격제어 요구 → **즉시 끊고 단말기 재부팅**

**📱 문자(스미싱)로 의심되는 경우**
- 택배·청첩장·과태료 등에서 **단축 URL(bit.ly, http) 클릭 금지**
- APK 파일 설치 안내 → **무조건 삭제**
- 가족·지인 명의 송금 요구 → **반드시 본인 음성통화로 확인**

**🔐 계정·금융 보안 기본**
- 2단계 인증(OTP) 필수
- 동일 비밀번호 재사용 금지
- 공용 Wi-Fi에서 금융 거래 금지
- 한 달에 한 번 [Have I Been Pwned](https://haveibeenpwned.com/)에서 이메일 유출 점검
    """)

st.markdown("---")

render_expert_page(
    title="사이버보안",
    icon="🛡️",
    default_query="보이스피싱 스미싱 신종 사기 개인정보 유출 해킹",
    auto_news_query="보이스피싱 스미싱 사기 개인정보 유출 해킹",
    sub_topics=[
        ("📞", "보이스피싱/스미싱", "보이스피싱 스미싱 메신저피싱 신종수법"),
        ("🔐", "개인정보 유출", "개인정보 유출 해킹 데이터 유출 사고"),
        ("💻", "랜섬웨어/해킹", "랜섬웨어 해킹 사이버 공격 침해 사고"),
        ("📲", "스마트폰/앱 보안", "스마트폰 앱 보안 악성앱 모바일 보안"),
        ("🏦", "금융사기/계좌탈취", "금융사기 계좌탈취 카드 부정사용 피싱"),
    ],
    external_links=[
        ("🛡️ KISA 인터넷진흥원", "https://www.kisa.or.kr/"),
        ("📞 보이스피싱 신고 (112)", "https://www.police.go.kr/"),
        ("🔐 개인정보 침해신고", "https://privacy.kisa.or.kr/"),
        ("💻 보호나라", "https://www.boho.or.kr/"),
    ],
)
