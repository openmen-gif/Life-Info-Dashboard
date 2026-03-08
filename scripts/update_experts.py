import os
import re

cur_dir = r"c:\Users\openm\00_AI개발\02_생활정보\output\10_tools\dashboard\pages"

new_content_template = """# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(title="{title}", icon="{icon}", default_query="{title} 최신 동향")
"""

files = [f for f in os.listdir(cur_dir) if re.match(r'^(0[5-9]|1[0-7])_.*\.py$', f)]

for f in files:
    fpath = os.path.join(cur_dir, f)
    with open(fpath, 'r', encoding='utf-8') as file:
        content = file.read()
    
    match = re.search(r'st\.title\("([^"]+)"\)', content)
    if match:
        full_title = match.group(1)
        # Handle cases where full title is like "💰 생활금융 전문가"
        parts = full_title.split(' ', 1)
        icon = parts[0]
        title = parts[1].replace(" 전문가", "").strip() if len(parts) > 1 else "Unknown"
        
        new_text = new_content_template.format(title=title, icon=icon)
        with open(fpath, 'w', encoding='utf-8') as file:
            file.write(new_text)
            
print("Successfully updated expert pages.")
