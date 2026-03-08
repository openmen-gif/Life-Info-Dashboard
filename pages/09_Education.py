# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(title="교육", icon="📚", default_query="글로벌 에듀테크 국내 입시 교육 트렌드")
