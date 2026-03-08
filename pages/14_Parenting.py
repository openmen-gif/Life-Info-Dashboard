# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(title="육아/보육", icon="👶", default_query="저출산 육아용품 글로벌 보육 정책 동향")
