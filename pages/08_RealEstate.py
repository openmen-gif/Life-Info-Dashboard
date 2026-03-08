# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(title="부동산", icon="🏠", default_query="국내 아파트 청약 전세 매매 부동산 동향")
