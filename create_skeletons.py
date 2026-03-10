import os

PAGES_DIR = "c:/Users/openm/00_AI개발/02_생활정보/output/10_tools/dashboard/pages"

pages_to_create = {
    "05_Finance.py": ("생활금융", "💰", "재테크 저축 금리 생활금융 동향"),
    "06_Health.py": ("건강", "🏥", "최신 헬스케어 메디컬 건강관리 동향"),
    "07_Food.py": ("식생활", "🍽️", "글로벌 외식 국내 맛집 요리 트렌드"),
    "08_RealEstate.py": ("부동산", "🏠", "국내 아파트 청약 전세 매매 부동산 동향"),
    "09_Education.py": ("교육", "📚", "글로벌 에듀테크 국내 입시 교육 트렌드"),
    "10_Travel.py": ("여행", "✈️", "국내 명소 여행지 호캉스 해외 관광 항공권 추천"),
    "11_Legal.py": ("생활법률", "⚖️", "최신 생활 법률 대법원 판례 동향"),
    "12_Stock.py": ("주식 분석", "📈", "국내 코스피 코스닥 미국 증시 주식 시황 분석"),
    "13_Shopping.py": ("쇼핑/소비", "🛍️", "글로벌 국내 온라인 쇼핑 소비 트렌드"),
    "14_Parenting.py": ("육아/보육", "👶", "저출산 육아용품 글로벌 보육 정책 동향"),
    "15_Culture.py": ("문화/예술", "🎭", "전시 공연 글로벌 K-문화 예술 동향"),
    "16_Pet.py": ("반려동물", "🐾", "반려동물 사료 펫 헬스케어 트렌드"),
    "25_Tech.py": ("IT/테크", "💻", "AI 반도체 스마트폰 IT 기술 트렌드"),
    "26_Jobs.py": ("취업/채용", "💼", "채용 트렌드 취업 시장 자격증 직업 전망"),
}

template = """# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(title="{title}", icon="{icon}", default_query="{query}")
"""

for filename, (title, icon, query) in pages_to_create.items():
    filepath = os.path.join(PAGES_DIR, filename)
    if not os.path.exists(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(template.format(icon=icon, title=title, query=query))
        print(f"Created {filename}")

print("All skeletons created.")
