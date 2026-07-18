@echo off
cd /d "%~dp0"
py -3.14 -m streamlit run Dashboard.py --server.port 8502
