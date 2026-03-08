# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(title="생활법률", icon="⚖️", default_query="최신 생활 법률 대법원 판례 동향")
