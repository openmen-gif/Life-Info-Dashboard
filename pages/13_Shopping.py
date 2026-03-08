# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(title="쇼핑/소비", icon="🛍️", default_query="글로벌 국내 온라인 쇼핑 소비 트렌드")
