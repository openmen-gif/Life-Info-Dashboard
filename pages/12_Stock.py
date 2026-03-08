# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(title="주식 분석", icon="📈", default_query="국내 코스피 코스닥 미국 증시 주식 시황 분석")
