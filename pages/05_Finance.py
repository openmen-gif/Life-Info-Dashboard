# -*- coding: utf-8 -*-
import streamlit as st
from utils.css_loader import apply_custom_css
from utils.expert_template import render_expert_page

apply_custom_css()

render_expert_page(title="생활금융", icon="💰", default_query="재테크 저축 금리 생활금융 동향")
