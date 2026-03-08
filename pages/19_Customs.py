# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(title="관세/무역", icon="🚢", default_query="한국 수출입 무역 글로벌 관세 동향")
