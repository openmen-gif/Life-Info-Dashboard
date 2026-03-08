import streamlit as st
import datetime
import pandas as pd
from utils.data_fetcher import fetch_web_search, fetch_news_search
from utils.report_downloader import render_download_buttons

def render_expert_page(title: str, icon: str, default_query: str):
    """
    Render a standard expert page with search, statistics, and reporting.
    """
    st.title(f"{icon} {title} 전문가")
    st.markdown("---")
    
    query = st.text_input(f"🔍 {title} 관련 검색어 입력", value=default_query)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        analyze_btn = st.button("데이터 분석 및 리포트 갱신", type="primary", use_container_width=True)
    
    # Session state key unique to this page
    state_key = f"expert_data_{title}"
    
    if analyze_btn:
        with st.spinner("최신 트렌드 및 뉴스 수집 중..."):
            web_results = fetch_web_search(query, limit=5)
            news_results = fetch_news_search(query, limit=5)
            
            # Generate context-aware statistical data
            dates = pd.date_range(end=datetime.datetime.today(), periods=7).strftime('%m-%d').tolist()
            
            # Domain-specific real-world scenario injection
            if "주식" in title or "코스피" in query:
                # User requested simulating a 6000 to 5000 point drop around Tue/Wed (which is about 4-5 days ago from today)
                # Trend index representation
                values = [6020, 6080, 5010, 4950, 5100, 5150, 5200]
            elif "환율" in title:
                # High volatility scenario
                values = [1350, 1345, 1420, 1450, 1435, 1440, 1445]
            elif "관세" in title or "무역" in title:
                # Deteriorating trend
                values = [100, 95, 80, 75, 78, 70, 68]
            else:
                # Default fallback mock using hash
                base_val = hash(query) % 50 + 20
                values = [base_val + (hash(query + d) % 30) for d in dates]
            
            df = pd.DataFrame({"Date": dates, "Trend": values})
            
            st.session_state[state_key] = {
                "query": query,
                "web": web_results,
                "news": news_results,
                "df": df,
                "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    data = st.session_state.get(state_key)
    
    if data:
        st.success(f"최근 분석 완료: {data['updated_at']}")
        
        st.markdown(f"### 📈 최근 7일 '{data['query']}' 관심도 트렌드")
        chart_data = data["df"].set_index("Date")
        st.bar_chart(chart_data)
        
        st.markdown("### 📰 핵심 관련 뉴스")
        if data["news"]:
            for n in data["news"][:3]:
                st.markdown(f"- **[{n['title']}]({n['link']})**  \n  <small>{n.get('source', '')} | {n.get('published', '')}</small>", unsafe_allow_html=True)
        else:
            st.info("관련 뉴스를 찾지 못했습니다.")
            
        st.markdown("---")
        st.markdown("### 🌐 웹 검색 결과 요약")
        if data["web"]:
            for w in data["web"][:3]:
                st.markdown(f"- **[{w['title']}]({w['link']})**  \n  <small>{w.get('snippet', '')}</small>", unsafe_allow_html=True)
        else:
             st.info("관련 웹 검색 결과를 찾지 못했습니다.")
                
        st.markdown("---")
        
        # Prepare context for report generation
        # 'df' is stored as a DataFrame, need to convert to list of dicts for JSON serialization
        trend_records = []
        if isinstance(data.get("df"), pd.DataFrame) and not data["df"].empty:
            # We assume it has "Date" and "Trend"
            trend_records = data["df"].to_dict('records')
            
        data_context = {
            "query": data["query"],
            "news": data["news"],
            "web": data["web"],
            "df": trend_records
        }
        
        render_download_buttons(context=data_context)
    else:
        st.info("상단 버튼을 눌러 데이터를 수집하고 인사이트를 확인하세요.")
