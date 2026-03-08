# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(title="환율 분석", icon="💱", default_query="달러 엔화 글로벌 환율 경제 동향")
