@echo off
cd /d "%~dp0"
streamlit run Dashboard.py --server.port 8502
