# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(title="반려동물", icon="🐾", default_query="반려동물 사료 펫 헬스케어 트렌드")
