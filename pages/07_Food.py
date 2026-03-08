# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(title="식생활", icon="🍽️", default_query="글로벌 외식 국내 맛집 요리 트렌드")
