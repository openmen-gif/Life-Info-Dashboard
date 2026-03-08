# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(title="화훼/식물", icon="🌷", default_query="플랜테리어 다육식물 화훼 트렌드")
