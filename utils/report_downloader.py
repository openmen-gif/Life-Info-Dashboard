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


def _add_hyperlink(paragraph, text, url):
    """Add a hyperlink to a python-docx paragraph."""
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    import docx.shared

    part = paragraph.part
    r_id = part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)

    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)

    new_run = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "0563C1")
    rPr.append(color)
    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    rPr.append(u)
    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), "20")
    rPr.append(sz)
    new_run.append(rPr)
    new_run.text = text
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)
    return paragraph


def _make_trend_chart(trend, query) -> io.BytesIO:
    """Generate a trend chart as PNG image bytes."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm

    # Try Korean font
    for fname in ["Malgun Gothic", "NanumGothic", "Noto Sans CJK KR", "AppleGothic"]:
        try:
            plt.rcParams["font.family"] = fname
            break
        except Exception:
            continue
    plt.rcParams["axes.unicode_minus"] = False

    dates = [str(r.get("Date", "")) for r in trend]
    values = [r.get("Trend", 0) for r in trend]

    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.fill_between(range(len(dates)), values, alpha=0.3, color="#4CAF50")
    ax.plot(range(len(dates)), values, marker="o", color="#4CAF50", linewidth=2, markersize=6)

    for i, v in enumerate(values):
        ax.annotate(f"{v:,.0f}", (i, v), textcoords="offset points",
                    xytext=(0, 10), ha="center", fontsize=9, fontweight="bold")

    ax.set_xticks(range(len(dates)))
    ax.set_xticklabels(dates, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("트렌드 지수", fontsize=10)
    ax.set_title(f"'{query}' 최근 7일 트렌드", fontsize=12, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf


def _gen_word(query, news, web, trend, now_str) -> bytes:
    try:
        from docx import Document
        from docx.shared import Inches, Pt, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
    except ImportError:
        return _gen_text(query, news, web, trend, now_str)

    doc = Document()

    # ── Title ──
    title = doc.add_heading(f"생활정보 심층 분석 리포트", level=1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run(f"분석 키워드: {query}")
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0x4C, 0xAF, 0x50)
    run.bold = True

    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = meta.add_run(f"생성일시: {now_str}  |  자동 생성 리포트")
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

    doc.add_paragraph("")  # spacer

    # ── 1. Executive Summary ──
    doc.add_heading("1. 분석 개요 (Executive Summary)", level=2)
    total_news = len(news) if news else 0
    total_web = len(web) if web else 0
    trend_summary = ""
    if trend and len(trend) >= 2:
        first_val = trend[0].get("Trend", 0)
        last_val = trend[-1].get("Trend", 0)
        if first_val > 0:
            change_pct = ((last_val - first_val) / first_val) * 100
            direction = "상승" if change_pct > 0 else "하락"
            trend_summary = f"최근 7일간 트렌드 지수는 {first_val:,.0f} → {last_val:,.0f}으로 {abs(change_pct):.1f}% {direction}하였습니다."
        else:
            trend_summary = f"최근 7일간 트렌드 지수: {first_val:,.0f} → {last_val:,.0f}"

    summary_text = (
        f"본 리포트는 '{query}' 키워드를 기반으로 수집된 최신 데이터를 분석한 결과입니다. "
        f"총 {total_news}건의 뉴스와 {total_web}건의 웹 검색 결과를 수집하여 분석하였습니다."
    )
    if trend_summary:
        summary_text += f" {trend_summary}"

    p = doc.add_paragraph(summary_text)
    p.paragraph_format.space_after = Pt(6)

    # ── 2. Trend Chart ──
    if trend:
        doc.add_heading("2. 트렌드 분석", level=2)
        doc.add_paragraph(
            f"아래 차트는 '{query}' 관련 최근 7일간의 관심도 추이를 나타냅니다. "
            f"데이터는 검색 빈도, 뉴스 노출량, 소셜 미디어 언급량 등을 종합한 지수입니다."
        )

        try:
            chart_buf = _make_trend_chart(trend, query)
            doc.add_picture(chart_buf, width=Inches(5.5))
            last_p = doc.paragraphs[-1]
            last_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        except Exception:
            doc.add_paragraph("[차트 생성 실패 — matplotlib 미설치]")

        # Trend interpretation
        if len(trend) >= 2:
            values = [r.get("Trend", 0) for r in trend]
            max_val = max(values)
            min_val = min(values)
            max_date = trend[values.index(max_val)].get("Date", "")
            min_date = trend[values.index(min_val)].get("Date", "")
            avg_val = sum(values) / len(values)

            doc.add_paragraph(
                f"분석 기간 중 최고점은 {max_date} ({max_val:,.0f}), "
                f"최저점은 {min_date} ({min_val:,.0f})이며, "
                f"평균 지수는 {avg_val:,.1f}입니다. "
                f"전체 변동폭은 {max_val - min_val:,.0f}으로, "
                f"{'높은 변동성을 보이고 있어 관련 동향을 주시할 필요가 있습니다.' if (max_val - min_val) > avg_val * 0.3 else '비교적 안정적인 추세를 유지하고 있습니다.'}"
            )

    # ── 3. News Analysis ──
    if news:
        section_num = 3 if trend else 2
        doc.add_heading(f"{section_num}. 핵심 뉴스 분석", level=2)
        doc.add_paragraph(
            f"'{query}' 관련 최신 뉴스 {len(news)}건을 수집하여 주요 내용을 정리하였습니다. "
            f"각 뉴스의 원문 링크를 참고문헌에서 확인하실 수 있습니다."
        )

        for i, n in enumerate(news[:10]):
            title_text = n.get("title", "제목 없음")
            source = n.get("source", "출처 미상")
            published = n.get("published", "")
            link = n.get("link", "")
            snippet = n.get("snippet", "")

            # News item heading
            p = doc.add_paragraph()
            run = p.add_run(f"[{i+1}] {title_text}")
            run.bold = True
            run.font.size = Pt(11)

            # Source and date
            meta_p = doc.add_paragraph()
            run = meta_p.add_run(f"출처: {source}")
            run.font.size = Pt(9)
            run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
            if published:
                run = meta_p.add_run(f"  |  {published}")
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

            if snippet:
                doc.add_paragraph(snippet)

            # Hyperlink
            if link:
                link_p = doc.add_paragraph()
                run = link_p.add_run("→ 원문 보기: ")
                run.font.size = Pt(9)
                _add_hyperlink(link_p, link[:80] + ("..." if len(link) > 80 else ""), link)

            doc.add_paragraph("")  # spacer

    # ── 4. Web Results ──
    if web:
        section_num = (3 if not trend else 4) if not news else (4 if trend else 3)
        doc.add_heading(f"{section_num}. 웹 검색 결과 분석", level=2)
        doc.add_paragraph(
            f"'{query}' 관련 웹 검색 결과 {len(web)}건을 수집하였습니다. "
            f"블로그, 포럼, 전문 사이트 등 다양한 소스에서 수집된 정보입니다."
        )

        for i, w in enumerate(web[:10]):
            title_text = w.get("title", "제목 없음")
            link = w.get("link", "")
            snippet = w.get("snippet", "")

            p = doc.add_paragraph()
            run = p.add_run(f"[{i+1}] {title_text}")
            run.bold = True
            run.font.size = Pt(10)

            if snippet:
                doc.add_paragraph(snippet)

            if link:
                link_p = doc.add_paragraph()
                run = link_p.add_run("→ ")
                run.font.size = Pt(9)
                _add_hyperlink(link_p, link[:80] + ("..." if len(link) > 80 else ""), link)

    # ── References ──
    doc.add_heading("참고문헌 (References)", level=2)
    doc.add_paragraph(
        "본 리포트에 인용된 모든 뉴스 및 웹 검색 결과의 원문 링크입니다. "
        "각 항목을 클릭하면 원문 페이지로 이동합니다."
    )

    ref_idx = 1
    if news:
        for n in news[:10]:
            link = n.get("link", "")
            title_text = n.get("title", "")
            source = n.get("source", "")
            if link:
                p = doc.add_paragraph()
                run = p.add_run(f"[{ref_idx}] ")
                run.font.size = Pt(9)
                _add_hyperlink(p, f"{title_text} — {source}", link)
                ref_idx += 1

    if web:
        for w in web[:10]:
            link = w.get("link", "")
            title_text = w.get("title", "")
            if link:
                p = doc.add_paragraph()
                run = p.add_run(f"[{ref_idx}] ")
                run.font.size = Pt(9)
                _add_hyperlink(p, title_text, link)
                ref_idx += 1

    # ── Footer ──
    doc.add_paragraph("")
    footer = doc.add_paragraph()
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer.add_run(f"— 생활정보 분석 플랫폼 자동 생성 리포트 ({now_str}) —")
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor(0xAA, 0xAA, 0xAA)

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def _generate_local_report(report_format: str, context=None) -> bytes:
    """Generate report locally (standalone mode). context can be dict or list."""
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Master report: context is a list of dicts (one per expert domain)
    if isinstance(context, list):
        query = "전 분야 마스터 리포트"
        news = []
        web = []
        trend = []
        for item in context:
            if isinstance(item, dict):
                news.extend(item.get("news", []))
                web.extend(item.get("web", []))
                trend.extend(item.get("df", []))
    elif isinstance(context, dict):
        query = context.get("query", "생활정보")
        news = context.get("news", [])
        web = context.get("web", [])
        trend = context.get("df", [])
    else:
        query = "생활정보"
        news = []
        web = []
        trend = []

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
