import os

PAGES_DIR = "c:/Users/openm/00_AI개발/02_생활정보/output/10_tools/dashboard/pages"

pages_to_create = {
    "05_Finance.py": ("생활금융", "💰"),
    "06_Health.py": ("건강", "🏥"),
    "07_Food.py": ("식생활", "🍽️"),
    "08_RealEstate.py": ("부동산", "🏠"),
    "09_Education.py": ("교육", "📚"),
    "10_Travel.py": ("여행", "✈️"),
    "11_Legal.py": ("생활법률", "⚖️"),
    "12_Stock.py": ("주식 분석", "📈"),
    "13_Shopping.py": ("쇼핑/소비", "🛍️"),
    "14_Parenting.py": ("육아/보육", "👶"),
    "15_Culture.py": ("문화/예술", "🎭"),
    "16_Pet.py": ("반려동물", "🐾"),
}

template = """# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css

apply_custom_css()

st.title("{icon} {title} 전문가")
st.markdown("---")

st.info("💡 준비 중입니다. 조만간 {title} 관련 데이터 수집 및 분석 AI가 연동될 예정입니다.")
"""

for filename, (title, icon) in pages_to_create.items():
    filepath = os.path.join(PAGES_DIR, filename)
    if not os.path.exists(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(template.format(icon=icon, title=title))
        print(f"Created {filename}")

print("All skeletons created.")
