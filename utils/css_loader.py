"""Custom CSS loader for Streamlit."""
import streamlit as st


def apply_custom_css():
    st.markdown("""
    <style>
    .block-container { padding-top: 1rem; }
    .stMetric { background: #1a1a2e; border-radius: 10px; padding: 15px; }
    .stMetric label { color: #8892b0; }
    h1 { color: #64ffda; }
    h2 { color: #8892b0; }
    h3 { color: #ccd6f6; }
    .info-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 12px; padding: 20px; margin: 10px 0;
        border-left: 4px solid #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)
