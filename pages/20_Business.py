# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(title="사업/창업", icon="🏢", default_query="스타트업 창업 지원 비즈니스 매크로 동향")
