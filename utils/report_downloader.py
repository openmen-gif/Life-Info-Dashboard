import streamlit as st
import requests
import datetime
import os
from utils.config import API_BASE_URL, IS_API_MODE

def download_report_from_api(report_format: str):
    """Call the backend API to generate a report and prompt download."""
    url = f"{API_BASE_URL}/report/generate"
    payload = {"report_type": report_format}
    
    try:
        response = requests.post(url, json=payload, stream=True)
        response.raise_for_status()
        
        # Streamlit st.download_button handles the downloaded content
        return response.content
    except requests.exceptions.RequestException as e:
        st.error(f"보고서 생성 실패: 서버에 연결할 수 없거나 내부 오류가 발생했습니다. ({e})")
        return None

def render_download_buttons():
    """Render a unified report download section."""
    if not IS_API_MODE:
        st.warning("⚠️ API 모드가 비활성화되어 리포트 다운로드를 사용할 수 없습니다.")
        return
        
    st.markdown("### 📥 통합 보고서 다운로드")
    st.caption("현재 수집된 날씨, 뉴스, 교통 요약 리포트를 다운로드합니다.")
    
    cols = st.columns(3)
    formats = [
        ("Word 문서 (.docx)", "word", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "📝"),
        ("PDF 문서 (.pdf)", "pdf", "application/pdf", "📄"),
        ("Excel 통합문서 (.xlsx)", "excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "📊")
    ]
    
    now_str = datetime.datetime.now().strftime('%Y%m%d_%H%M')
    
    for i, (label, fmt, mime_type, icon) in enumerate(formats):
        with cols[i]:
            if st.button(f"{icon} {label} 생성", key=f"btn_gen_{fmt}"):
                with st.spinner(f"{label} 생성 중..."):
                    content = download_report_from_api(fmt)
                    if content:
                        ext = ".docx" if fmt == "word" else (".pdf" if fmt == "pdf" else ".xlsx")
                        filename = f"LifeInfo_Summary_{now_str}{ext}"
                        # Need to trigger a download using st.download_button workaround or show it immediately
                        # Because Streamlit's st.download_button requires the data upfront, which blocks until generated.
                        # Instead, if generation was fast, we can save to a temp file or just provide the data.
                        st.download_button(
                            label=f"👉 여기를 눌러 {fmt.upper()} 저장",
                            data=content,
                            file_name=filename,
                            mime=mime_type,
                            key=f"dl_btn_{fmt}_{now_str}"
                        )
