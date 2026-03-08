import streamlit as st
import requests
import datetime
import io
from utils.config import API_BASE_URL, IS_API_MODE


def _gen_text(query, news, web, trend, now_str) -> bytes:
    lines = [f"생활정보 분석 리포트 — {query}", f"생성일시: {now_str}", "=" * 60, ""]
    if trend:
        lines.append("[ 트렌드 데이터 ]")
        for row in trend:
            lines.append(f"  {row.get('Date', '')}  →  {row.get('Trend', '')}")
        lines.append("")
    if news:
        lines.append("[ 관련 뉴스 ]")
        for n in news[:10]:
            lines.append(f"  - {n.get('title', '')} ({n.get('source', '')})")
            lines.append(f"    {n.get('link', '')}")
        lines.append("")
    if web:
        lines.append("[ 웹 검색 결과 ]")
        for w in web[:10]:
            lines.append(f"  - {w.get('title', '')}")
            lines.append(f"    {w.get('link', '')}")
    return "\n".join(lines).encode("utf-8")


def _gen_excel(query, news, web, trend, now_str) -> bytes:
    try:
        import xlsxwriter
        buf = io.BytesIO()
        wb = xlsxwriter.Workbook(buf)
        bold = wb.add_format({"bold": True})
        ws1 = wb.add_worksheet("트렌드")
        ws1.write(0, 0, f"분석 키워드: {query}", bold)
        ws1.write(1, 0, f"생성일시: {now_str}")
        ws1.write(3, 0, "날짜", bold)
        ws1.write(3, 1, "트렌드", bold)
        for i, row in enumerate(trend or []):
            ws1.write(4 + i, 0, str(row.get("Date", "")))
            ws1.write(4 + i, 1, row.get("Trend", 0))
        ws2 = wb.add_worksheet("뉴스")
        ws2.write(0, 0, "제목", bold); ws2.write(0, 1, "출처", bold); ws2.write(0, 2, "링크", bold)
        for i, n in enumerate(news or []):
            ws2.write(1 + i, 0, n.get("title", ""))
            ws2.write(1 + i, 1, n.get("source", ""))
            ws2.write(1 + i, 2, n.get("link", ""))
        wb.close()
        return buf.getvalue()
    except ImportError:
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "트렌드"
        ws.append([f"분석 키워드: {query}", f"생성일시: {now_str}"])
        ws.append(["날짜", "트렌드"])
        for row in (trend or []):
            ws.append([str(row.get("Date", "")), row.get("Trend", 0)])
        buf = io.BytesIO()
        wb.save(buf)
        return buf.getvalue()


def _gen_word(query, news, web, trend, now_str) -> bytes:
    try:
        from docx import Document
        doc = Document()
        doc.add_heading(f"생활정보 분석 리포트 — {query}", level=1)
        doc.add_paragraph(f"생성일시: {now_str}")
        if trend:
            doc.add_heading("트렌드 데이터", level=2)
            table = doc.add_table(rows=1, cols=2)
            table.style = "Table Grid"
            table.rows[0].cells[0].text = "날짜"
            table.rows[0].cells[1].text = "트렌드"
            for row in trend:
                r = table.add_row()
                r.cells[0].text = str(row.get("Date", ""))
                r.cells[1].text = str(row.get("Trend", ""))
        if news:
            doc.add_heading("관련 뉴스", level=2)
            for n in news[:10]:
                doc.add_paragraph(f"{n.get('title', '')} — {n.get('source', '')}", style="List Bullet")
        if web:
            doc.add_heading("웹 검색 결과", level=2)
            for w in web[:10]:
                doc.add_paragraph(f"{w.get('title', '')} — {w.get('link', '')}", style="List Bullet")
        buf = io.BytesIO()
        doc.save(buf)
        return buf.getvalue()
    except ImportError:
        return _gen_text(query, news, web, trend, now_str)


def _generate_local_report(report_format: str, context: dict = None) -> bytes:
    """Generate report locally (standalone mode)."""
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    query = context.get("query", "생활정보") if context else "생활정보"
    news = context.get("news", []) if context else []
    web = context.get("web", []) if context else []
    trend = context.get("df", []) if context else []
    if report_format == "excel":
        return _gen_excel(query, news, web, trend, now_str)
    elif report_format == "word":
        return _gen_word(query, news, web, trend, now_str)
    else:
        return _gen_text(query, news, web, trend, now_str)


def download_report_from_api(report_format: str, context: dict = None):
    """Call the backend API to generate a report."""
    url = f"{API_BASE_URL}/report/generate"
    payload = {"report_type": report_format}
    if context:
        payload["context"] = context
    try:
        response = requests.post(url, json=payload, stream=True, timeout=10)
        response.raise_for_status()
        return response.content
    except Exception:
        return None


def render_download_buttons(context: dict = None):
    """Render report download section. Works in both API and standalone mode."""
    if context:
        if isinstance(context, list):
            st.markdown("### 📥 전 분야 마스터 리포트 다운로드")
            st.caption("전문가 최신 동향 데이터를 총망라한 마스터 리포트를 다운로드합니다.")
        else:
            st.markdown("### 📥 전문가 맞춤형 보고서 다운로드")
            st.caption(f"'{context.get('query', '분석 키워드')}'에 대한 최신 동향과 뉴스를 포함한 심층 리포트를 다운로드합니다.")
    else:
        st.markdown("### 📥 통합 보고서 다운로드")
        st.caption("현재 수집된 날씨, 뉴스, 교통 요약 리포트를 다운로드합니다.")

    cols = st.columns(3)
    formats = [
        ("Word (.docx)", "word", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "📝"),
        ("텍스트 (.txt)", "text", "text/plain", "📄"),
        ("Excel (.xlsx)", "excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "📊"),
    ]

    now_str = datetime.datetime.now().strftime('%Y%m%d_%H%M')

    for i, (label, fmt, mime_type, icon) in enumerate(formats):
        with cols[i]:
            if st.button(f"{icon} {label} 생성", key=f"btn_gen_{fmt}"):
                with st.spinner(f"{label} 생성 중..."):
                    content = None
                    if IS_API_MODE:
                        content = download_report_from_api(fmt, context)
                    if not content:
                        content = _generate_local_report(fmt, context)
                    if content:
                        ext_map = {"word": ".docx", "text": ".txt", "excel": ".xlsx"}
                        ext = ext_map.get(fmt, ".txt")
                        prefix = "Expert_Report" if context else "LifeInfo_Summary"
                        filename = f"{prefix}_{now_str}{ext}"
                        st.download_button(
                            label=f"👉 {label} 저장",
                            data=content,
                            file_name=filename,
                            mime=mime_type,
                            key=f"dl_btn_{fmt}_{now_str}"
                        )
