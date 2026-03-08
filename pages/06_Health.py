# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(title="건강", icon="🏥", default_query="최신 헬스케어 메디컬 건강관리 동향")
