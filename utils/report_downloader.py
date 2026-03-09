import streamlit as st
import requests
import datetime
import io
import math
from utils.config import API_BASE_URL, IS_API_MODE


# ═══════════════════════════════════════════════════════════════════════════════
# Expert Domain Knowledge — derived from skill_md/*.md
# ═══════════════════════════════════════════════════════════════════════════════

EXPERT_ANALYSIS = {
    "주식": {
        "icon": "📈",
        "framework": "기술적 분석 + 펀더멘털 분석",
        "metrics": ["PER", "PBR", "ROE", "EPS", "배당수익률"],
        "disclaimer": "본 분석은 투자 참고용이며, 투자 판단의 최종 책임은 투자자 본인에게 있습니다. 과거 수익률이 미래 수익률을 보장하지 않습니다.",
        "analysis_fn": "_analyze_stock",
    },
    "환율": {
        "icon": "💱",
        "framework": "거시경제 환율 분석",
        "metrics": ["USD/KRW", "JPY/KRW", "CNY/KRW", "환율변동성"],
        "disclaimer": "환율은 글로벌 거시경제, 금리 정책, 지정학적 리스크 등 복합 요인에 의해 변동됩니다.",
        "analysis_fn": "_analyze_forex",
    },
    "관세": {
        "icon": "🚢",
        "framework": "무역수지 및 관세영향 분석",
        "metrics": ["수출증감률", "수입증감률", "무역수지", "관세율변동"],
        "disclaimer": "관세 및 무역 정책은 국제 협정과 정부 정책에 따라 변동될 수 있습니다.",
        "analysis_fn": "_analyze_trade",
    },
    "금융": {
        "icon": "💰",
        "framework": "가계금융 및 자산관리 분석",
        "metrics": ["기준금리", "예금금리", "대출금리", "소비자물가지수"],
        "disclaimer": "금융 상품 비교 시 수수료, 세금, 중도해지 조건을 반드시 확인하세요.",
        "analysis_fn": "_analyze_finance",
    },
    "건강": {
        "icon": "🏥",
        "framework": "헬스케어 트렌드 및 건강관리 분석",
        "metrics": ["BMI 기준", "일일권장섭취량", "운동강도지표"],
        "disclaimer": "본 분석은 전문 의료 상담을 대체하지 않습니다. 개인 건강 상태에 따라 전문의 상담을 권장합니다.",
        "analysis_fn": "_analyze_health",
    },
    "부동산": {
        "icon": "🏠",
        "framework": "부동산 시장 동향 및 가격 분석",
        "metrics": ["매매가격지수", "전세가격지수", "매매/전세비율", "청약경쟁률"],
        "disclaimer": "부동산 투자는 가격하락, 금리변동, 공실률 등의 위험을 수반합니다.",
        "analysis_fn": "_analyze_realestate",
    },
    "법률": {
        "icon": "⚖️",
        "framework": "생활법률 및 판례 분석",
        "metrics": ["관련법령", "판례동향", "소멸시효"],
        "disclaimer": "본 분석은 전문 법률 상담을 대체하지 않습니다. 대한법률구조공단(132) 무료 상담을 권장합니다.",
        "analysis_fn": "_analyze_legal",
    },
    "교육": {
        "icon": "📚",
        "framework": "에듀테크 및 학습 트렌드 분석",
        "metrics": ["수강률", "합격률", "학습효율지표"],
        "disclaimer": "",
        "analysis_fn": "_analyze_default",
    },
    "여행": {
        "icon": "✈️",
        "framework": "여행 트렌드 및 관광 분석",
        "metrics": ["항공운임지수", "관광객수", "숙박가격지수"],
        "disclaimer": "여행 전 외교부 해외안전여행 사이트에서 여행경보 단계를 확인하세요.",
        "analysis_fn": "_analyze_default",
    },
    "식생활": {
        "icon": "🍽️",
        "framework": "외식·식품 트렌드 분석",
        "metrics": ["외식물가지수", "식재료가격", "배달주문트렌드"],
        "disclaimer": "",
        "analysis_fn": "_analyze_default",
    },
    "쇼핑": {
        "icon": "🛒",
        "framework": "소비 트렌드 및 쇼핑 분석",
        "metrics": ["소비자심리지수", "온라인거래액", "카드소비동향"],
        "disclaimer": "",
        "analysis_fn": "_analyze_default",
    },
    "육아": {
        "icon": "👶",
        "framework": "육아·보육 정책 및 트렌드 분석",
        "metrics": ["합계출산율", "보육시설현황", "육아용품시장"],
        "disclaimer": "",
        "analysis_fn": "_analyze_default",
    },
    "문화": {
        "icon": "🎭",
        "framework": "문화·예술 동향 분석",
        "metrics": ["공연관람률", "전시회참관객", "한류콘텐츠수출"],
        "disclaimer": "",
        "analysis_fn": "_analyze_default",
    },
    "반려동물": {
        "icon": "🐾",
        "framework": "펫 산업 트렌드 분석",
        "metrics": ["반려동물등록수", "펫산업시장규모", "사료가격지수"],
        "disclaimer": "",
        "analysis_fn": "_analyze_default",
    },
    "화훼": {
        "icon": "🌸",
        "framework": "화훼·식물 트렌드 분석",
        "metrics": ["화훼시장규모", "플랜테리어관심도"],
        "disclaimer": "",
        "analysis_fn": "_analyze_default",
    },
    "유가": {
        "icon": "🛢️",
        "framework": "국제유가 분석",
        "metrics": ["WTI", "Brent", "Dubai유", "국내유가"],
        "disclaimer": "국제유가는 OPEC+ 감산, 지정학적 긴장, 글로벌 수요 등 복합 요인에 의해 변동됩니다.",
        "analysis_fn": "_analyze_default",
    },
    "운송": {
        "icon": "🚛",
        "framework": "물류·운송 동향 분석",
        "metrics": ["BDI(발틱건화물지수)", "컨테이너운임", "항공화물량"],
        "disclaimer": "",
        "analysis_fn": "_analyze_default",
    },
    "분쟁": {
        "icon": "🌍",
        "framework": "글로벌 지정학 리스크 분석",
        "metrics": ["지정학리스크지수", "분쟁영향권국가", "난민현황"],
        "disclaimer": "",
        "analysis_fn": "_analyze_default",
    },
    "사업": {
        "icon": "🏢",
        "framework": "창업·비즈니스 트렌드 분석",
        "metrics": ["창업건수", "폐업률", "VC투자규모"],
        "disclaimer": "",
        "analysis_fn": "_analyze_default",
    },
}


def _match_expert_domain(query: str, expert_name: str = "") -> dict:
    """Match query/expert_name to the best expert domain analysis profile."""
    combined = f"{expert_name} {query}".lower()
    best_match = None
    best_score = 0
    for key, profile in EXPERT_ANALYSIS.items():
        key_lower = key.lower()
        score = 0
        if key_lower in combined:
            score = len(key_lower) * 2
        # partial keyword match
        for char in key_lower:
            if char in combined:
                score += 1
        if score > best_score:
            best_score = score
            best_match = profile
    if best_match and best_score >= 2:
        return best_match
    # Default
    return {
        "icon": "📊",
        "framework": "데이터 기반 트렌드 분석",
        "metrics": ["관심도지수", "뉴스빈도", "검색트렌드"],
        "disclaimer": "",
        "analysis_fn": "_analyze_default",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Statistical helpers
# ═══════════════════════════════════════════════════════════════════════════════

def _calc_statistics(values: list) -> dict:
    """Calculate comprehensive statistics for a trend series."""
    if not values or len(values) < 2:
        return {}
    n = len(values)
    mean_val = sum(values) / n
    variance = sum((v - mean_val) ** 2 for v in values) / (n - 1)
    std_dev = math.sqrt(variance) if variance > 0 else 0
    max_val = max(values)
    min_val = min(values)
    range_val = max_val - min_val

    # Simple moving average (3-period)
    sma3 = []
    for i in range(2, n):
        sma3.append(sum(values[i - 2:i + 1]) / 3)

    # Trend direction via linear regression slope
    x_mean = (n - 1) / 2
    numerator = sum((i - x_mean) * (v - mean_val) for i, v in enumerate(values))
    denominator = sum((i - x_mean) ** 2 for i in range(n))
    slope = numerator / denominator if denominator != 0 else 0

    # Coefficient of variation (volatility proxy)
    cv = (std_dev / mean_val * 100) if mean_val != 0 else 0

    # Change metrics
    first_val = values[0]
    last_val = values[-1]
    abs_change = last_val - first_val
    pct_change = ((last_val - first_val) / first_val * 100) if first_val != 0 else 0

    return {
        "mean": mean_val,
        "std_dev": std_dev,
        "max": max_val,
        "min": min_val,
        "range": range_val,
        "cv": cv,
        "slope": slope,
        "sma3": sma3,
        "abs_change": abs_change,
        "pct_change": pct_change,
        "first": first_val,
        "last": last_val,
        "trend_dir": "상승" if slope > 0 else ("하락" if slope < 0 else "보합"),
        "volatility": "높음" if cv > 15 else ("보통" if cv > 5 else "낮음"),
    }


def _extract_news_themes(news: list) -> list[str]:
    """Extract common themes/keywords from news titles for flow analysis."""
    if not news:
        return []
    # Simple keyword frequency
    from collections import Counter
    stop_words = {"및", "등", "위한", "대한", "관련", "통해", "따라", "에서", "으로", "이번", "최근", "올해"}
    words = []
    for n in news:
        title = _clean_text(n.get("title", ""))
        for w in title.split():
            w = w.strip(".,!?()[]\"'·…")
            if len(w) >= 2 and w not in stop_words:
                words.append(w)
    counter = Counter(words)
    return [w for w, _ in counter.most_common(8)]


def _news_flow_summary(news: list, query: str) -> str:
    """Generate a narrative flow analysis from news articles."""
    if not news:
        return ""
    themes = _extract_news_themes(news)
    n_count = len(news)

    sources = set()
    for n in news:
        s = n.get("source", "")
        if s:
            sources.add(s)

    flow = f"수집된 {n_count}건의 뉴스를 종합 분석한 결과, "
    if themes:
        flow += f"'{query}' 관련 핵심 키워드는 【{'、'.join(themes[:5])}】 등으로 나타났습니다. "
    if sources:
        flow += f"주요 보도 매체는 {', '.join(list(sources)[:4])} 등입니다. "

    # Simple sentiment heuristic from title keywords
    pos_words = ["상승", "호조", "성장", "확대", "개선", "증가", "강세", "반등", "돌파", "긍정"]
    neg_words = ["하락", "감소", "위기", "약세", "우려", "축소", "급락", "둔화", "침체", "적자"]
    pos_count = 0
    neg_count = 0
    for n in news:
        title = n.get("title", "")
        for pw in pos_words:
            if pw in title:
                pos_count += 1
        for nw in neg_words:
            if nw in title:
                neg_count += 1

    total_sentiment = pos_count + neg_count
    if total_sentiment > 0:
        pos_ratio = pos_count / total_sentiment * 100
        neg_ratio = neg_count / total_sentiment * 100
        if pos_ratio > 60:
            flow += f"전반적 논조는 긍정적(긍정 {pos_ratio:.0f}% vs 부정 {neg_ratio:.0f}%)이며, 시장/분야 전망에 대한 낙관론이 우세합니다."
        elif neg_ratio > 60:
            flow += f"전반적 논조는 부정적(부정 {neg_ratio:.0f}% vs 긍정 {pos_ratio:.0f}%)이며, 리스크 요인에 대한 경계감이 감지됩니다."
        else:
            flow += f"긍정(긍정 {pos_ratio:.0f}%)과 부정(부정 {neg_ratio:.0f}%) 논조가 혼재하며, 불확실성이 높은 상황입니다."
    else:
        flow += "뉴스 논조는 중립적이며, 주요 방향성 전환 신호는 아직 감지되지 않았습니다."

    return flow


# ═══════════════════════════════════════════════════════════════════════════════
# Chart generation
# ═══════════════════════════════════════════════════════════════════════════════

def _make_trend_chart(trend, query, stats=None) -> io.BytesIO:
    """Generate an enhanced trend chart with statistics overlay."""
    plt = _setup_korean_font()

    dates = [str(r.get("Date", "")) for r in trend]
    values = [r.get("Trend", 0) for r in trend]

    fig, ax = plt.subplots(figsize=(7.5, 4))

    # Main line + fill
    ax.fill_between(range(len(dates)), values, alpha=0.15, color="#1976D2")
    ax.plot(range(len(dates)), values, marker="o", color="#1976D2",
            linewidth=2.5, markersize=7, zorder=5, label="트렌드 지수")

    # Data labels
    for i, v in enumerate(values):
        ax.annotate(f"{v:,.0f}", (i, v), textcoords="offset points",
                    xytext=(0, 12), ha="center", fontsize=8, fontweight="bold",
                    color="#1976D2")

    # Mean line
    if stats and stats.get("mean"):
        ax.axhline(y=stats["mean"], color="#E65100", linestyle="--",
                   linewidth=1, alpha=0.7, label=f'평균: {stats["mean"]:,.1f}')

    # SMA-3 overlay
    if stats and stats.get("sma3") and len(stats["sma3"]) >= 2:
        sma_x = list(range(2, 2 + len(stats["sma3"])))
        ax.plot(sma_x, stats["sma3"], color="#4CAF50", linewidth=1.5,
                linestyle="-.", alpha=0.8, label="3일 이동평균")

    # Min/Max markers
    if len(values) >= 2:
        max_idx = values.index(max(values))
        min_idx = values.index(min(values))
        ax.annotate("▲ HIGH", (max_idx, values[max_idx]),
                    textcoords="offset points", xytext=(0, 22),
                    ha="center", fontsize=7, color="#D32F2F", fontweight="bold")
        ax.annotate("▼ LOW", (min_idx, values[min_idx]),
                    textcoords="offset points", xytext=(0, -18),
                    ha="center", fontsize=7, color="#1565C0", fontweight="bold")

    ax.set_xticks(range(len(dates)))
    ax.set_xticklabels(dates, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("트렌드 지수", fontsize=10)
    ax.set_title(f"'{query}' 최근 트렌드 추이 분석", fontsize=12, fontweight="bold")
    ax.grid(axis="y", alpha=0.2)
    ax.grid(axis="x", alpha=0.1)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="upper right", fontsize=8, framealpha=0.8)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


def _setup_korean_font():
    """Configure matplotlib to use Korean-capable font."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    available_fonts = {f.name for f in fm.fontManager.ttflist}
    for fname in ["Malgun Gothic", "NanumGothic", "Noto Sans KR", "Noto Sans CJK KR",
                   "Noto Sans CJK JP", "AppleGothic", "DejaVu Sans"]:
        if fname in available_fonts:
            plt.rcParams["font.family"] = fname
            break
    plt.rcParams["axes.unicode_minus"] = False
    return plt


def _make_keyword_freq_chart(news: list, query: str) -> io.BytesIO | None:
    """Generate keyword frequency horizontal bar chart from news titles."""
    import re
    from collections import Counter
    if not news:
        return None
    plt = _setup_korean_font()

    all_titles = " ".join(n.get("title", "") for n in news)
    words = re.findall(r"[가-힣]{2,}", all_titles)
    stopwords = {"것으로", "에서", "관련", "대한", "위한", "으로", "이번", "오늘", "내일",
                 "지난", "올해", "이후", "까지", "부터", "하는", "있는", "없는", "되는",
                 "한다", "했다", "라며", "이다", "따라", "통해", "대해"}
    words = [w for w in words if w not in stopwords]
    freq = Counter(words).most_common(12)
    if not freq:
        return None

    labels, counts = zip(*reversed(freq))
    fig, ax = plt.subplots(figsize=(7, max(3, len(labels) * 0.35)))
    colors = ["#1976D2" if i < len(labels) - 3 else "#E65100" for i in range(len(labels))]
    bars = ax.barh(range(len(labels)), counts, color=colors, height=0.6, alpha=0.85)
    for i, (bar, val) in enumerate(zip(bars, counts)):
        ax.text(val + 0.3, i, str(val), va="center", fontsize=8, fontweight="bold")
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("빈도", fontsize=10)
    ax.set_title(f"'{query}' 뉴스 핵심 키워드 빈도 분석", fontsize=11, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


def _make_sentiment_pie_chart(news: list) -> io.BytesIO | None:
    """Generate sentiment distribution pie chart."""
    if not news:
        return None
    plt = _setup_korean_font()

    pos_words = {"상승", "급등", "호재", "성장", "개선", "회복", "활황", "강세", "최고",
                 "돌파", "증가", "확대", "호조", "긍정", "수혜", "기대", "추천", "인기",
                 "혁신", "반등", "호황", "흑자"}
    neg_words = {"하락", "급락", "악재", "위축", "감소", "둔화", "약세", "최저",
                 "폭락", "축소", "부진", "우려", "경고", "위기", "리스크", "적자",
                 "침체", "하방", "손실", "붕괴", "악화", "불안", "충격", "규제"}

    pos_count = neg_count = neutral_count = 0
    for n in news:
        title = n.get("title", "")
        has_pos = any(w in title for w in pos_words)
        has_neg = any(w in title for w in neg_words)
        if has_pos and not has_neg:
            pos_count += 1
        elif has_neg and not has_pos:
            neg_count += 1
        elif has_pos and has_neg:
            pos_count += 0.5
            neg_count += 0.5
        else:
            neutral_count += 1

    values = [pos_count, neg_count, neutral_count]
    labels = [f"긍정 ({pos_count:.0f}건)", f"부정 ({neg_count:.0f}건)", f"중립 ({neutral_count:.0f}건)"]
    colors = ["#4CAF50", "#F44336", "#9E9E9E"]
    explode = (0.05, 0.05, 0)

    fig, ax = plt.subplots(figsize=(5, 4))
    wedges, texts, autotexts = ax.pie(values, labels=labels, colors=colors, explode=explode,
                                       autopct="%1.0f%%", startangle=90, pctdistance=0.75)
    for t in autotexts:
        t.set_fontsize(10)
        t.set_fontweight("bold")
    ax.set_title("뉴스 감성 분포 분석", fontsize=11, fontweight="bold", pad=15)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


def _make_source_dist_chart(news: list) -> io.BytesIO | None:
    """Generate news source distribution chart."""
    from collections import Counter
    if not news:
        return None
    plt = _setup_korean_font()

    sources = [n.get("source", "기타") or "기타" for n in news]
    freq = Counter(sources).most_common(8)
    if not freq:
        return None

    labels, counts = zip(*freq)
    colors = ["#1976D2", "#388E3C", "#F57C00", "#7B1FA2", "#C62828",
              "#00838F", "#4E342E", "#546E7A"][:len(labels)]

    fig, ax = plt.subplots(figsize=(5, 4))
    wedges, texts, autotexts = ax.pie(counts, labels=labels, colors=colors,
                                       autopct="%1.0f%%", startangle=90, pctdistance=0.8)
    for t in texts:
        t.set_fontsize(8)
    for t in autotexts:
        t.set_fontsize(8)
        t.set_fontweight("bold")
    ax.set_title("뉴스 출처 분포", fontsize=11, fontweight="bold", pad=15)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


def _make_daily_change_chart(trend: list, query: str) -> io.BytesIO | None:
    """Generate daily change rate bar chart with outlier detection."""
    if not trend or len(trend) < 3:
        return None
    plt = _setup_korean_font()

    values = [r.get("Trend", 0) for r in trend]
    dates = [str(r.get("Date", "")) for r in trend]
    changes = []
    change_dates = []
    for i in range(1, len(values)):
        if values[i - 1] != 0:
            pct = ((values[i] - values[i - 1]) / values[i - 1]) * 100
        else:
            pct = 0
        changes.append(pct)
        change_dates.append(dates[i])

    if not changes:
        return None

    # Outlier detection (beyond 1.5 * IQR)
    mean_c = sum(changes) / len(changes)
    std_c = (sum((c - mean_c) ** 2 for c in changes) / max(len(changes) - 1, 1)) ** 0.5
    threshold = 1.5 * std_c if std_c > 0 else float("inf")

    colors = []
    for c in changes:
        if abs(c - mean_c) > threshold:
            colors.append("#FF6F00")  # outlier
        elif c >= 0:
            colors.append("#4CAF50")
        else:
            colors.append("#F44336")

    fig, ax = plt.subplots(figsize=(7, 3.5))
    bars = ax.bar(range(len(changes)), changes, color=colors, alpha=0.85, width=0.6)
    for i, (bar, val) in enumerate(zip(bars, changes)):
        y_offset = 0.3 if val >= 0 else -0.3
        ax.text(i, val + y_offset, f"{val:+.1f}%", ha="center", fontsize=8, fontweight="bold",
                color=colors[i])

    ax.axhline(y=0, color="black", linewidth=0.5)
    ax.axhline(y=mean_c, color="#1976D2", linewidth=1, linestyle="--", alpha=0.6,
               label=f"평균: {mean_c:+.1f}%")
    if std_c > 0:
        ax.axhspan(mean_c - threshold, mean_c + threshold, alpha=0.05, color="#1976D2")

    ax.set_xticks(range(len(change_dates)))
    ax.set_xticklabels(change_dates, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("변화율 (%)", fontsize=10)
    ax.set_title(f"'{query}' 일별 변화율 분석 (주황=이상치)", fontsize=11, fontweight="bold")
    ax.legend(fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


def _make_comparison_bar_chart(context_list) -> io.BytesIO:
    """Generate a cross-domain comparison bar chart for master report."""
    plt = _setup_korean_font()

    names = []
    changes = []
    colors = []

    for item in context_list:
        if not isinstance(item, dict):
            continue
        trend = item.get("df", [])
        if not trend or len(trend) < 2:
            continue
        first = trend[0].get("Trend", 0)
        last = trend[-1].get("Trend", 0)
        if first == 0:
            continue
        pct = ((last - first) / first) * 100
        name = item.get("expert", item.get("query", ""))[:8]
        names.append(name)
        changes.append(pct)
        colors.append("#4CAF50" if pct >= 0 else "#F44336")

    if not names:
        return None

    fig, ax = plt.subplots(figsize=(8, max(3, len(names) * 0.4)))
    bars = ax.barh(range(len(names)), changes, color=colors, height=0.6, alpha=0.85)

    for i, (bar, val) in enumerate(zip(bars, changes)):
        offset = 1 if val >= 0 else -1
        ax.text(val + offset, i, f"{val:+.1f}%", va="center",
                fontsize=8, fontweight="bold",
                color="#4CAF50" if val >= 0 else "#F44336")

    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=9)
    ax.set_xlabel("변동률 (%)", fontsize=10)
    ax.set_title("분야별 트렌드 변동률 비교", fontsize=12, fontweight="bold")
    ax.axvline(x=0, color="black", linewidth=0.5)
    ax.grid(axis="x", alpha=0.2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


# ═══════════════════════════════════════════════════════════════════════════════
# Text cleaning helpers
# ═══════════════════════════════════════════════════════════════════════════════

def _clean_text(text: str) -> str:
    """Strip HTML tags, decode entities, clean whitespace for report output."""
    import re
    from html import unescape
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", " ", text)
    clean = unescape(clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    # Remove raw URLs masquerading as summaries
    if clean.startswith("http://") or clean.startswith("https://"):
        return ""
    return clean


# ═══════════════════════════════════════════════════════════════════════════════
# Word helper: hyperlinks & bookmarks
# ═══════════════════════════════════════════════════════════════════════════════

def _add_hyperlink(paragraph, text, url):
    """Add a clickable hyperlink to a python-docx paragraph."""
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    part = paragraph.part
    r_id = part.relate_to(url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True)

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
    sz.set(qn("w:val"), "18")
    rPr.append(sz)
    new_run.append(rPr)

    t_elem = OxmlElement("w:t")
    t_elem.set(qn("xml:space"), "preserve")
    t_elem.text = text
    new_run.append(t_elem)

    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)
    return paragraph


def _add_bookmark(paragraph, bookmark_name):
    """Add a bookmark anchor to a paragraph for internal linking."""
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    import random

    bm_id = str(random.randint(1000, 99999))
    bm_start = OxmlElement("w:bookmarkStart")
    bm_start.set(qn("w:id"), bm_id)
    bm_start.set(qn("w:name"), bookmark_name)
    paragraph._p.insert(0, bm_start)

    bm_end = OxmlElement("w:bookmarkEnd")
    bm_end.set(qn("w:id"), bm_id)
    paragraph._p.append(bm_end)


def _add_internal_link(paragraph, text, bookmark_name):
    """Add an internal hyperlink (bookmark ref) to a paragraph."""
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("w:anchor"), bookmark_name)

    new_run = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "1565C0")
    rPr.append(color)
    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    rPr.append(u)
    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), "20")
    rPr.append(sz)
    new_run.append(rPr)

    t_elem = OxmlElement("w:t")
    t_elem.set(qn("xml:space"), "preserve")
    t_elem.text = text
    new_run.append(t_elem)

    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)


def _add_toc_entry(doc, num, title_text, bookmark_name):
    """Add a TOC entry with number, dotted leader, and internal link."""
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    p = doc.add_paragraph()
    # Set tab stop with dot leader at right margin
    pPr = p._p.get_or_add_pPr()
    tabs = OxmlElement("w:tabs")
    tab = OxmlElement("w:tab")
    tab.set(qn("w:val"), "right")
    tab.set(qn("w:leader"), "dot")
    tab.set(qn("w:pos"), "9072")  # ~16cm right margin
    tabs.append(tab)
    pPr.append(tabs)

    # Section number + title as internal link
    _add_internal_link(p, f"{num}. {title_text}", bookmark_name)

    # Tab + page indicator
    tab_run = OxmlElement("w:r")
    tab_char = OxmlElement("w:tab")
    tab_run.append(tab_char)
    p._p.append(tab_run)

    # Page number placeholder
    pg_run = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), "18")
    rPr.append(sz)
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "888888")
    rPr.append(color)
    pg_run.append(rPr)
    t = OxmlElement("w:t")
    t.text = f"p.{num}"
    pg_run.append(t)
    p._p.append(pg_run)

    return p


# ═══════════════════════════════════════════════════════════════════════════════
# Individual Expert Word Report
# ═══════════════════════════════════════════════════════════════════════════════

def _gen_word(query, news, web, trend, now_str) -> bytes:
    try:
        from docx import Document
        from docx.shared import Inches, Pt, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.enum.table import WD_TABLE_ALIGNMENT
    except ImportError:
        return _gen_text(query, news, web, trend, now_str)

    domain = _match_expert_domain(query)
    doc = Document()

    # ── Title Page ──
    for _ in range(3):
        doc.add_paragraph("")
    title = doc.add_heading(f"{domain['icon']} 생활정보 심층 분석 리포트", level=1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _add_bookmark(title, "top")

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run(f"분석 키워드: {query}")
    run.font.size = Pt(16)
    run.font.color.rgb = RGBColor(0x1A, 0x23, 0x7E)
    run.bold = True

    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = meta.add_run(f"분석 프레임워크: {domain['framework']}")
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

    meta2 = doc.add_paragraph()
    meta2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = meta2.add_run(f"생성일시: {now_str}  |  자동 생성 리포트")
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

    doc.add_page_break()

    # ── Table of Contents ──
    sec_num = 1
    toc_heading = doc.add_heading("목차 (Table of Contents)", level=2)
    _add_bookmark(toc_heading, "toc")

    sections = []
    sections.append((sec_num, "분석 개요 (Executive Summary)", "sec_summary"))
    sec_num += 1
    if trend:
        sections.append((sec_num, "트렌드 분석 및 통계", "sec_trend"))
        sec_num += 1
        sections.append((sec_num, "변화율 분석 및 이상치 탐지", "sec_change_rate"))
        sec_num += 1
    if news:
        sections.append((sec_num, "뉴스 심층 분석 (감성·키워드·출처)", "sec_news_analysis"))
        sec_num += 1
        sections.append((sec_num, "주요 뉴스 목록", "sec_news_list"))
        sec_num += 1
    if web:
        sections.append((sec_num, "웹 검색 결과 분석", "sec_web"))
        sec_num += 1
    sections.append((sec_num, "전문가 종합 인사이트", "sec_expert"))
    sec_num += 1
    sections.append((sec_num, "참고문헌 (References)", "sec_refs"))

    for num, title_text, bm in sections:
        _add_toc_entry(doc, num, title_text, bm)

    doc.add_paragraph("")

    # ── Disclaimer ──
    if domain.get("disclaimer"):
        p = doc.add_paragraph()
        run = p.add_run(f"⚠ {domain['disclaimer']}")
        run.font.size = Pt(8)
        run.font.color.rgb = RGBColor(0xAA, 0x55, 0x00)
        run.italic = True

    doc.add_page_break()

    # Track section numbers for sequential numbering
    current_sec = 1

    # ══ 1. Executive Summary ══
    h = doc.add_heading(f"{current_sec}. 분석 개요 (Executive Summary)", level=2)
    _add_bookmark(h, "sec_summary")
    current_sec += 1

    total_news = len(news) if news else 0
    total_web = len(web) if web else 0

    summary_parts = [
        f"본 리포트는 '{query}' 키워드를 기반으로 최신 데이터를 수집·분석한 결과입니다.",
        f"총 {total_news}건의 뉴스와 {total_web}건의 웹 검색 결과를 수집하여 다각도로 분석하였습니다.",
    ]

    stats = None
    if trend and len(trend) >= 2:
        values = [r.get("Trend", 0) for r in trend]
        stats = _calc_statistics(values)
        summary_parts.append(
            f"최근 {len(trend)}일간 트렌드 지수는 {stats['first']:,.0f} → {stats['last']:,.0f}으로 "
            f"{abs(stats['pct_change']):.1f}% {stats['trend_dir']}하였으며, "
            f"변동성은 {stats['volatility']} 수준(CV={stats['cv']:.1f}%)입니다."
        )

    # Brief news summary (detailed flow analysis in dedicated section)
    if news:
        themes = _extract_news_themes(news)
        if themes:
            summary_parts.append(
                f"뉴스 핵심 키워드: 【{'、'.join(themes[:5])}】 — 상세 흐름 분석은 별도 섹션을 참조하세요."
            )

    for part in summary_parts:
        p = doc.add_paragraph(part)
        p.paragraph_format.space_after = Pt(4)

    # Key metrics table
    if domain.get("metrics"):
        doc.add_paragraph("")
        p = doc.add_paragraph()
        run = p.add_run("▶ 주요 분석 지표:")
        run.bold = True
        run.font.size = Pt(10)
        for m in domain["metrics"]:
            doc.add_paragraph(f"  • {m}", style="List Bullet")

    # ══ 2. Trend Analysis ══
    if trend:
        doc.add_paragraph("")
        h = doc.add_heading(f"{current_sec}. 트렌드 분석 및 통계", level=2)
        _add_bookmark(h, "sec_trend")
        current_sec += 1

        doc.add_paragraph(
            f"아래 차트는 '{query}' 관련 최근 추이를 나타냅니다. "
            f"트렌드 지수는 검색 빈도, 뉴스 노출량, 소셜 미디어 언급량 등을 종합 산출한 복합 지수입니다."
        )

        # Chart
        try:
            chart_buf = _make_trend_chart(trend, query, stats)
            doc.add_picture(chart_buf, width=Inches(5.8))
            last_p = doc.paragraphs[-1]
            last_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        except Exception as e:
            doc.add_paragraph(f"[차트 생성 실패: {e}]")

        # Statistics table
        if stats:
            doc.add_paragraph("")
            p = doc.add_paragraph()
            run = p.add_run("▶ 통계 분석 요약")
            run.bold = True
            run.font.size = Pt(11)

            table = doc.add_table(rows=8, cols=2, style="Light Shading Accent 1")
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            stat_data = [
                ("평균 (Mean)", f"{stats['mean']:,.1f}"),
                ("표준편차 (Std Dev)", f"{stats['std_dev']:,.2f}"),
                ("최고점 (High)", f"{stats['max']:,.0f}"),
                ("최저점 (Low)", f"{stats['min']:,.0f}"),
                ("변동폭 (Range)", f"{stats['range']:,.0f}"),
                ("변동계수 (CV)", f"{stats['cv']:.1f}%"),
                ("추세 방향", f"{stats['trend_dir']} (기울기: {stats['slope']:+.2f})"),
                ("기간 변동률", f"{stats['pct_change']:+.1f}%"),
            ]
            for row_idx, (label, val) in enumerate(stat_data):
                table.rows[row_idx].cells[0].text = label
                table.rows[row_idx].cells[1].text = val

            # Trend interpretation
            doc.add_paragraph("")
            p = doc.add_paragraph()
            run = p.add_run("▶ 추세 해석")
            run.bold = True

            values = [r.get("Trend", 0) for r in trend]
            max_val = max(values)
            min_val = min(values)
            max_date = trend[values.index(max_val)].get("Date", "")
            min_date = trend[values.index(min_val)].get("Date", "")

            interp = (
                f"분석 기간 중 최고점은 {max_date} ({max_val:,.0f}), "
                f"최저점은 {min_date} ({min_val:,.0f})이며, "
                f"평균 지수는 {stats['mean']:,.1f}입니다. "
            )
            if stats['cv'] > 15:
                interp += (
                    f"변동계수 {stats['cv']:.1f}%로 높은 변동성을 보이고 있어, "
                    f"관련 동향을 면밀히 주시할 필요가 있습니다. "
                    f"급격한 변동은 외부 이벤트(정책 발표, 글로벌 이슈 등)에 기인했을 가능성이 높으며, "
                    f"단기적 과매도/과매수 구간을 식별하는 것이 중요합니다."
                )
            elif stats['cv'] > 5:
                interp += (
                    f"변동계수 {stats['cv']:.1f}%로 보통 수준의 변동성을 나타내고 있습니다. "
                    f"전반적으로 {stats['trend_dir']} 추세이나, 방향성 전환 가능성을 염두에 두어야 합니다."
                )
            else:
                interp += (
                    f"변동계수 {stats['cv']:.1f}%로 안정적인 추세를 유지하고 있습니다. "
                    f"현재의 {stats['trend_dir']} 기조가 단기적으로 지속될 가능성이 높습니다."
                )
            doc.add_paragraph(interp)

    # ══ Daily Change Rate Analysis ══
    if trend and len(trend) >= 3:
        doc.add_paragraph("")
        h = doc.add_heading(f"{current_sec}. 변화율 분석 및 이상치 탐지", level=2)
        _add_bookmark(h, "sec_change_rate")
        current_sec += 1

        values = [r.get("Trend", 0) for r in trend]
        daily_changes = []
        for idx_c in range(1, len(values)):
            if values[idx_c - 1] != 0:
                pct = ((values[idx_c] - values[idx_c - 1]) / values[idx_c - 1]) * 100
            else:
                pct = 0
            daily_changes.append(pct)

        doc.add_paragraph(
            "일별 변화율을 분석하여 급격한 변동(이상치)을 탐지합니다. "
            "이상치는 1.5×표준편차를 초과하는 변화율로 정의됩니다."
        )

        # Chart
        try:
            change_buf = _make_daily_change_chart(trend, query)
            if change_buf:
                doc.add_picture(change_buf, width=Inches(5.8))
                last_p = doc.paragraphs[-1]
                last_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        except Exception:
            pass

        # Change rate stats
        if daily_changes:
            mean_dc = sum(daily_changes) / len(daily_changes)
            std_dc = (sum((c - mean_dc) ** 2 for c in daily_changes) / max(len(daily_changes) - 1, 1)) ** 0.5
            max_dc = max(daily_changes)
            min_dc = min(daily_changes)

            doc.add_paragraph("")
            cr_table = doc.add_table(rows=5, cols=2, style="Light Shading Accent 1")
            cr_table.alignment = WD_TABLE_ALIGNMENT.CENTER
            cr_data = [
                ("평균 일별 변화율", f"{mean_dc:+.2f}%"),
                ("변화율 표준편차", f"{std_dc:.2f}%"),
                ("최대 상승 변화", f"{max_dc:+.2f}%"),
                ("최대 하락 변화", f"{min_dc:+.2f}%"),
                ("이상치 탐지 기준", f"±{1.5 * std_dc:.2f}%"),
            ]
            for row_idx, (label, val) in enumerate(cr_data):
                cr_table.rows[row_idx].cells[0].text = label
                cr_table.rows[row_idx].cells[1].text = val

            # Outlier detection
            threshold = 1.5 * std_dc if std_dc > 0 else float("inf")
            outliers = [(i, c) for i, c in enumerate(daily_changes) if abs(c - mean_dc) > threshold]
            if outliers:
                doc.add_paragraph("")
                p = doc.add_paragraph()
                run = p.add_run(f"▶ 이상치 {len(outliers)}건 탐지:")
                run.bold = True
                for oi, oc in outliers:
                    date_label = trend[oi + 1].get("Date", "") if oi + 1 < len(trend) else ""
                    doc.add_paragraph(f"  ⚠ {date_label}: {oc:+.2f}% (기준 초과)")
            else:
                doc.add_paragraph("분석 기간 내 이상치는 탐지되지 않았습니다. 안정적 변동 패턴입니다.")

    # ══ News Deep Analysis (Sentiment + Keywords + Sources) ══
    if news:
        doc.add_paragraph("")
        h = doc.add_heading(f"{current_sec}. 뉴스 심층 분석 (감성·키워드·출처)", level=2)
        _add_bookmark(h, "sec_news_analysis")
        current_sec += 1

        doc.add_paragraph(
            f"수집된 {len(news)}건의 뉴스에 대해 감성 분석, 핵심 키워드 빈도, 출처 분포를 "
            f"통계적으로 분석하였습니다."
        )

        # 1) Sentiment pie chart
        doc.add_paragraph("")
        p = doc.add_paragraph()
        run = p.add_run("▶ 감성 분석 (Sentiment Analysis)")
        run.bold = True
        run.font.size = Pt(11)

        try:
            sent_buf = _make_sentiment_pie_chart(news)
            if sent_buf:
                doc.add_picture(sent_buf, width=Inches(4.0))
                last_p = doc.paragraphs[-1]
                last_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        except Exception:
            pass

        flow_text = _news_flow_summary(news, query)
        if flow_text:
            doc.add_paragraph(flow_text)

        # 2) Keyword frequency chart
        doc.add_paragraph("")
        p = doc.add_paragraph()
        run = p.add_run("▶ 핵심 키워드 빈도 분석")
        run.bold = True
        run.font.size = Pt(11)

        try:
            kw_buf = _make_keyword_freq_chart(news, query)
            if kw_buf:
                doc.add_picture(kw_buf, width=Inches(5.5))
                last_p = doc.paragraphs[-1]
                last_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        except Exception:
            pass

        themes = _extract_news_themes(news)
        if themes:
            doc.add_paragraph(
                f"상위 키워드: {'、'.join(themes[:8])} — "
                f"이들 키워드의 빈도 변화를 추적하면 향후 트렌드 선행 지표로 활용 가능합니다."
            )

        # 3) Source distribution chart
        doc.add_paragraph("")
        p = doc.add_paragraph()
        run = p.add_run("▶ 뉴스 출처 분포 분석")
        run.bold = True
        run.font.size = Pt(11)

        try:
            src_buf = _make_source_dist_chart(news)
            if src_buf:
                doc.add_picture(src_buf, width=Inches(4.0))
                last_p = doc.paragraphs[-1]
                last_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        except Exception:
            pass

        from collections import Counter as _Counter
        sources = [n.get("source", "기타") or "기타" for n in news]
        src_freq = _Counter(sources).most_common(5)
        if src_freq:
            src_text = ", ".join(f"{s} ({c}건)" for s, c in src_freq)
            doc.add_paragraph(f"주요 보도 매체: {src_text}")

        # ══ News List (compact, no duplication) ══
        doc.add_paragraph("")
        h = doc.add_heading(f"{current_sec}. 주요 뉴스 목록", level=2)
        _add_bookmark(h, "sec_news_list")
        current_sec += 1

        n_display = min(len(news), 10)
        table = doc.add_table(rows=n_display + 1, cols=4, style="Light Shading Accent 1")
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        headers = ["No.", "제목", "출처", "요약"]
        for j, header in enumerate(headers):
            cell = table.rows[0].cells[j]
            cell.text = header
            for p in cell.paragraphs:
                for run in p.runs:
                    run.bold = True

        for idx, n in enumerate(news[:n_display]):
            row = table.rows[idx + 1]
            row.cells[0].text = str(idx + 1)
            title_text = _clean_text(n.get("title", ""))
            row.cells[1].text = title_text[:60]
            row.cells[2].text = _clean_text(n.get("source", ""))
            snippet = _clean_text(n.get("snippet", ""))
            row.cells[3].text = snippet[:100] + ("..." if len(snippet) > 100 else "")

        # Hyperlinks below table (compact)
        doc.add_paragraph("")
        p = doc.add_paragraph()
        run = p.add_run("▶ 원문 링크:")
        run.bold = True
        run.font.size = Pt(9)
        for i, n in enumerate(news[:n_display]):
            link = n.get("link", "")
            title_text = _clean_text(n.get("title", ""))
            if link:
                link_p = doc.add_paragraph()
                run = link_p.add_run(f"  [{i + 1}] ")
                run.font.size = Pt(8)
                _add_hyperlink(link_p, title_text[:70] + ("..." if len(title_text) > 70 else ""), link)

    # ══ Web Results ══
    if web:
        doc.add_paragraph("")
        h = doc.add_heading(f"{current_sec}. 웹 검색 결과 분석", level=2)
        _add_bookmark(h, "sec_web")
        current_sec += 1

        doc.add_paragraph(
            f"'{query}' 관련 웹 검색 결과 {len(web)}건을 수집하였습니다. "
            f"블로그, 포럼, 전문 사이트 등 다양한 소스에서 수집된 정보입니다."
        )

        for i, w in enumerate(web[:10]):
            title_text = _clean_text(w.get("title", "제목 없음"))
            link = w.get("link", "")
            snippet = _clean_text(w.get("snippet", ""))

            p = doc.add_paragraph()
            run = p.add_run(f"[{i + 1}] {title_text}")
            run.bold = True
            run.font.size = Pt(10)

            if snippet:
                p = doc.add_paragraph()
                run = p.add_run(snippet)
                run.font.size = Pt(9)

            if link:
                link_p = doc.add_paragraph()
                run = link_p.add_run("원문: ")
                run.font.size = Pt(9)
                _add_hyperlink(link_p, title_text[:60] + ("..." if len(title_text) > 60 else ""), link)
            doc.add_paragraph("")

    # ══ Expert Comprehensive Insight ══
    doc.add_paragraph("")
    h = doc.add_heading(f"{current_sec}. 전문가 종합 인사이트", level=2)
    _add_bookmark(h, "sec_expert")
    current_sec += 1

    p = doc.add_paragraph()
    run = p.add_run(f"▶ 분석 프레임워크: {domain['framework']}")
    run.bold = True
    run.font.size = Pt(11)

    # Unique forward-looking analysis (not repeating trend/news sections)
    doc.add_paragraph(
        f"이상의 트렌드·뉴스·웹 분석 결과를 {domain['framework']} 관점에서 종합하면 다음과 같습니다."
    )

    insight_parts = []
    # Risk-opportunity matrix based on combined signals
    if stats:
        vol_label = stats["volatility"]
        trend_label = stats["trend_dir"]
        if trend_label == "상승" and vol_label == "낮음":
            insight_parts.append(
                "【기회 우위】 안정적 상승세로 진입 기회가 유효합니다. "
                "다만 외부 충격(정책 전환, 글로벌 이벤트)에 따른 급반전 가능성을 "
                "헤지 전략으로 대비하시기 바랍니다."
            )
        elif trend_label == "상승" and vol_label != "낮음":
            insight_parts.append(
                "【주의 필요】 상승세이나 변동성이 높아 과열 신호를 동반합니다. "
                f"3일 이동평균과의 괴리(현재 지수 대비)를 모니터링하고, "
                f"변동계수 {stats['cv']:.1f}%가 정상 범위로 회귀하는지 점검하세요."
            )
        elif trend_label == "하락":
            insight_parts.append(
                "【리스크 경계】 하락 추세에 있으므로 방어적 포지션을 권장합니다. "
                "반등 시그널(일별 변화율 양전환 2일 연속, 긍정 뉴스 비중 확대)을 "
                "기다린 후 전략 수정을 검토하세요."
            )
        else:
            insight_parts.append(
                "【관망 구간】 방향성이 불분명한 보합 상태입니다. "
                "정책 발표, 실적 시즌, 계절 요인 등 촉매(catalyst)에 따라 "
                "방향이 결정될 가능성이 높으므로 이벤트 일정을 주시하세요."
            )

    # Cross-signal consistency check
    if news and stats:
        # Check if news sentiment aligns with trend direction
        pos_kw = {"상승", "성장", "개선", "회복", "강세", "호조", "확대", "증가"}
        neg_kw = {"하락", "위축", "감소", "약세", "부진", "우려", "침체", "위기"}
        all_titles = " ".join(n.get("title", "") for n in news)
        p_cnt = sum(1 for w in pos_kw if w in all_titles)
        n_cnt = sum(1 for w in neg_kw if w in all_titles)
        news_dir = "긍정" if p_cnt > n_cnt else ("부정" if n_cnt > p_cnt else "중립")
        trend_dir = stats["trend_dir"]

        if (trend_dir == "상승" and news_dir == "긍정") or (trend_dir == "하락" and news_dir == "부정"):
            insight_parts.append(
                f"트렌드({trend_dir})와 뉴스 감성({news_dir})이 일치하여 "
                f"현재 방향성의 신뢰도가 높습니다."
            )
        elif (trend_dir == "상승" and news_dir == "부정") or (trend_dir == "하락" and news_dir == "긍정"):
            insight_parts.append(
                f"⚠ 트렌드({trend_dir})와 뉴스 감성({news_dir})이 상충합니다. "
                f"이는 조만간 추세 전환이 일어날 수 있는 선행 신호일 수 있으므로 "
                f"향후 1~2일간의 변화를 면밀히 관찰하세요."
            )

    # Action items
    doc.add_paragraph("")
    p = doc.add_paragraph()
    run = p.add_run("▶ 실행 권고사항 (Action Items)")
    run.bold = True
    run.font.size = Pt(11)

    actions = [
        f"1. 모니터링 지표 — {', '.join(domain.get('metrics', [])[:3])} 등을 주기적으로 점검",
        "2. 뉴스 감성 추이 — 긍정/부정 비율 변화를 주 1회 이상 체크",
    ]
    if stats and stats.get("cv", 0) > 10:
        actions.append("3. 변동성 관리 — 변동계수가 높으므로 분산 투자/접근 전략 검토")
    else:
        actions.append("3. 기회 포착 — 안정적 환경에서의 신규 진입/확대 기회 검토")
    actions.append("4. 외부 변수 — 정책, 글로벌 이슈, 계절 요인에 따른 시나리오별 대응 준비")

    for a in actions:
        doc.add_paragraph(a)

    for part in insight_parts:
        doc.add_paragraph(part)

    # ══ References ══
    doc.add_page_break()
    h = doc.add_heading(f"{current_sec}. 참고문헌 (References)", level=2)
    _add_bookmark(h, "sec_refs")

    doc.add_paragraph(
        "본 리포트에 인용된 모든 뉴스 및 웹 검색 결과의 원문 링크입니다. "
        "각 항목의 하이퍼링크를 클릭하면 원문 페이지로 이동합니다."
    )

    ref_idx = 1
    if news:
        p = doc.add_paragraph()
        run = p.add_run("■ 뉴스 출처")
        run.bold = True
        for n in news[:10]:
            link = n.get("link", "")
            title_text = n.get("title", "")
            source = n.get("source", "")
            if link:
                p = doc.add_paragraph()
                run = p.add_run(f"  [{ref_idx}] ")
                run.font.size = Pt(9)
                label = f"{title_text}"
                if source:
                    label += f" — {source}"
                _add_hyperlink(p, label[:120], link)
                ref_idx += 1

    if web:
        doc.add_paragraph("")
        p = doc.add_paragraph()
        run = p.add_run("■ 웹 검색 출처")
        run.bold = True
        for w in web[:10]:
            link = w.get("link", "")
            title_text = w.get("title", "")
            if link:
                p = doc.add_paragraph()
                run = p.add_run(f"  [{ref_idx}] ")
                run.font.size = Pt(9)
                _add_hyperlink(p, title_text[:120], link)
                ref_idx += 1

    # ── Footer ──
    doc.add_paragraph("")
    doc.add_paragraph("")
    footer = doc.add_paragraph()
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer.add_run("━" * 40)
    run.font.color.rgb = RGBColor(0xCC, 0xCC, 0xCC)
    footer2 = doc.add_paragraph()
    footer2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer2.add_run(f"생활정보 분석 플랫폼 자동 생성 리포트  |  {now_str}")
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor(0xAA, 0xAA, 0xAA)
    footer3 = doc.add_paragraph()
    footer3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer3.add_run("Powered by Life-Info Expert Analysis System")
    run.font.size = Pt(7)
    run.font.color.rgb = RGBColor(0xBB, 0xBB, 0xBB)
    run.italic = True

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════════
# Master Report (multi-expert)
# ═══════════════════════════════════════════════════════════════════════════════

def _gen_word_master(context_list, now_str) -> bytes:
    """Generate a comprehensive master Word report with per-expert sections."""
    try:
        from docx import Document
        from docx.shared import Inches, Pt, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.enum.table import WD_TABLE_ALIGNMENT
    except ImportError:
        return _gen_text_master(context_list, now_str)

    valid_items = [item for item in context_list if isinstance(item, dict)]
    doc = Document()

    # ══════════ Title Page ══════════
    for _ in range(4):
        doc.add_paragraph("")
    title = doc.add_heading("전 분야 마스터 리포트", level=1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _add_bookmark(title, "top")

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run("생활정보 전문가 시스템 종합 분석 보고서")
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0x1A, 0x23, 0x7E)

    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = meta.add_run(f"생성일시: {now_str}  |  {len(valid_items)}개 분야 종합 분석")
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

    meta2 = doc.add_paragraph()
    meta2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    total_news = sum(len(item.get("news", [])) for item in valid_items)
    total_web = sum(len(item.get("web", [])) for item in valid_items)
    run = meta2.add_run(f"수집 데이터: 뉴스 {total_news}건  |  웹 검색 {total_web}건")
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

    doc.add_page_break()

    # ══════════ Table of Contents ══════════
    toc_h = doc.add_heading("목차 (Table of Contents)", level=2)
    _add_bookmark(toc_h, "toc")

    # Section 0: Executive Overview
    _add_toc_entry(doc, "I", "총괄 분석 개요 (Executive Overview)", "sec_overview")
    _add_toc_entry(doc, "II", "분야별 트렌드 비교 차트", "sec_comparison")

    for i, item in enumerate(valid_items):
        expert_name = item.get("expert", item.get("query", f"분야 {i + 1}"))
        domain = _match_expert_domain(item.get("query", ""), expert_name)
        bm_name = f"expert_{i}"
        _add_toc_entry(doc, i + 1, f"{domain.get('icon', '📊')} {expert_name}", bm_name)

    _add_toc_entry(doc, "★", "참고문헌 (References)", "sec_master_refs")

    doc.add_page_break()

    # ══════════ I. Executive Overview ══════════
    h = doc.add_heading("I. 총괄 분석 개요 (Executive Overview)", level=2)
    _add_bookmark(h, "sec_overview")

    doc.add_paragraph(
        f"본 마스터 리포트는 {len(valid_items)}개 생활정보 분야의 최신 동향을 종합 분석한 결과입니다. "
        f"총 {total_news}건의 뉴스와 {total_web}건의 웹 검색 결과를 기반으로, "
        f"각 분야별 전문가 프레임워크를 적용하여 심층 분석하였습니다."
    )

    # Overview table
    doc.add_paragraph("")
    p = doc.add_paragraph()
    run = p.add_run("▶ 분야별 핵심 지표 요약")
    run.bold = True
    run.font.size = Pt(11)

    table = doc.add_table(rows=len(valid_items) + 1, cols=5, style="Light Shading Accent 1")
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["분야", "뉴스", "웹", "추세", "변동률"]
    for j, header in enumerate(headers):
        cell = table.rows[0].cells[j]
        cell.text = header
        for p in cell.paragraphs:
            for run in p.runs:
                run.bold = True

    for idx, item in enumerate(valid_items):
        expert_name = item.get("expert", "")[:12]
        news_cnt = len(item.get("news", []))
        web_cnt = len(item.get("web", []))
        trend_data = item.get("df", [])
        trend_dir = "-"
        change_str = "-"
        if trend_data and len(trend_data) >= 2:
            first_v = trend_data[0].get("Trend", 0)
            last_v = trend_data[-1].get("Trend", 0)
            if first_v > 0:
                pct = ((last_v - first_v) / first_v) * 100
                trend_dir = "▲" if pct > 0 else ("▼" if pct < 0 else "━")
                change_str = f"{pct:+.1f}%"

        row = table.rows[idx + 1]
        row.cells[0].text = expert_name
        row.cells[1].text = str(news_cnt)
        row.cells[2].text = str(web_cnt)
        row.cells[3].text = trend_dir
        row.cells[4].text = change_str

    # Top risers / fallers
    doc.add_paragraph("")
    ranked = []
    for item in valid_items:
        trend_data = item.get("df", [])
        if trend_data and len(trend_data) >= 2:
            first_v = trend_data[0].get("Trend", 0)
            last_v = trend_data[-1].get("Trend", 0)
            if first_v > 0:
                pct = ((last_v - first_v) / first_v) * 100
                ranked.append((item.get("expert", ""), pct))

    if ranked:
        ranked.sort(key=lambda x: x[1], reverse=True)
        p = doc.add_paragraph()
        run = p.add_run("▶ 상승 Top 3:")
        run.bold = True
        for name, pct in ranked[:3]:
            doc.add_paragraph(f"  📈 {name}: {pct:+.1f}%")

        p = doc.add_paragraph()
        run = p.add_run("▶ 하락 Top 3:")
        run.bold = True
        for name, pct in ranked[-3:]:
            doc.add_paragraph(f"  📉 {name}: {pct:+.1f}%")

    # ══════════ II. Comparison Chart ══════════
    doc.add_page_break()
    h = doc.add_heading("II. 분야별 트렌드 비교 차트", level=2)
    _add_bookmark(h, "sec_comparison")

    doc.add_paragraph(
        "아래 차트는 전 분야의 최근 트렌드 변동률을 비교한 결과입니다. "
        "양(+)의 값은 상승, 음(-)의 값은 하락을 나타내며, "
        "절대값이 클수록 변동 폭이 큰 것을 의미합니다."
    )

    try:
        comp_buf = _make_comparison_bar_chart(valid_items)
        if comp_buf:
            doc.add_picture(comp_buf, width=Inches(5.8))
            last_p = doc.paragraphs[-1]
            last_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    except Exception as e:
        doc.add_paragraph(f"[비교 차트 생성 실패: {e}]")

    # ══════════ Per-Expert Sections ══════════
    all_refs = []
    for i, item in enumerate(valid_items):
        doc.add_page_break()

        expert_name = item.get("expert", item.get("query", f"분야 {i + 1}"))
        query = item.get("query", expert_name)
        news = item.get("news", [])
        web = item.get("web", [])
        trend = item.get("df", [])
        domain = _match_expert_domain(query, expert_name)

        h = doc.add_heading(f"{i + 1}. {domain.get('icon', '📊')} {expert_name}", level=2)
        _add_bookmark(h, f"expert_{i}")

        # Back to TOC link
        p = doc.add_paragraph()
        _add_internal_link(p, "↑ 목차로 이동", "toc")

        # Framework & metrics
        p = doc.add_paragraph()
        run = p.add_run(f"분석 프레임워크: {domain['framework']}")
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
        run.italic = True

        # Summary
        total_n = len(news)
        total_w = len(web)
        summary = f"'{query}' 키워드 기반 수집 — 뉴스 {total_n}건, 웹 {total_w}건."
        stats = None
        if trend and len(trend) >= 2:
            values = [r.get("Trend", 0) for r in trend]
            stats = _calc_statistics(values)
            summary += (
                f" 트렌드: {stats['first']:,.0f} → {stats['last']:,.0f} "
                f"({stats['pct_change']:+.1f}% {stats['trend_dir']}, "
                f"변동성: {stats['volatility']})"
            )
        doc.add_paragraph(summary)

        # Chart
        if trend:
            try:
                chart_buf = _make_trend_chart(trend, query, stats)
                doc.add_picture(chart_buf, width=Inches(5.2))
                last_p = doc.paragraphs[-1]
                last_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            except Exception as e:
                doc.add_paragraph(f"[차트 생성 실패: {e}]")

            # Brief stat summary
            if stats:
                doc.add_paragraph(
                    f"  평균: {stats['mean']:,.1f}  |  "
                    f"최고: {stats['max']:,.0f}  |  최저: {stats['min']:,.0f}  |  "
                    f"변동폭: {stats['range']:,.0f}  |  CV: {stats['cv']:.1f}%"
                )

        # Expert opinion
        doc.add_paragraph("")
        p = doc.add_paragraph()
        run = p.add_run("▶ 전문가 분석 의견")
        run.bold = True

        expert_text = f"'{expert_name}' 분야는 "
        if stats:
            if stats["trend_dir"] == "상승":
                expert_text += (
                    f"최근 {stats['pct_change']:+.1f}%의 상승세를 기록하고 있습니다. "
                    f"관심도가 증가하고 있어 관련 기회 요인을 주목할 필요가 있습니다."
                )
            elif stats["trend_dir"] == "하락":
                expert_text += (
                    f"최근 {stats['pct_change']:+.1f}%의 하락세를 보이고 있어, "
                    f"하락 원인 분석 및 리스크 관리에 유의해야 합니다."
                )
            else:
                expert_text += "보합 상태로, 방향성 전환 신호를 주시해야 합니다."
        else:
            expert_text += "현재 수집된 데이터 기반으로 동향 모니터링 중입니다."

        doc.add_paragraph(expert_text)

        # Disclaimer
        if domain.get("disclaimer"):
            p = doc.add_paragraph()
            run = p.add_run(f"⚠ {domain['disclaimer']}")
            run.font.size = Pt(7)
            run.font.color.rgb = RGBColor(0xAA, 0x55, 0x00)
            run.italic = True

        # News flow
        if news:
            doc.add_paragraph("")
            p = doc.add_paragraph()
            run = p.add_run("▶ 뉴스 흐름 분석")
            run.bold = True

            flow = _news_flow_summary(news, query)
            if flow:
                doc.add_paragraph(flow)

            # News items
            p = doc.add_paragraph()
            run = p.add_run("▶ 주요 뉴스:")
            run.bold = True
            for n in news[:5]:
                title_text = _clean_text(n.get("title", ""))
                link = n.get("link", "")
                source = _clean_text(n.get("source", ""))
                snippet = _clean_text(n.get("snippet", ""))

                np_p = doc.add_paragraph()
                run = np_p.add_run(f"• {title_text}")
                run.font.size = Pt(10)
                run.bold = True

                if snippet:
                    sp = doc.add_paragraph()
                    run = sp.add_run(f"  {snippet[:120]}")
                    run.font.size = Pt(9)
                    run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

                if link:
                    lp = doc.add_paragraph()
                    run = lp.add_run("  원문: ")
                    run.font.size = Pt(8)
                    _add_hyperlink(lp, title_text[:60] + ("..." if len(title_text) > 60 else ""), link)
                    all_refs.append({"title": title_text, "source": source, "link": link, "domain": expert_name})

        # Web results
        if web:
            doc.add_paragraph("")
            p = doc.add_paragraph()
            run = p.add_run("▶ 웹 검색 결과:")
            run.bold = True
            for w in web[:3]:
                title_text = _clean_text(w.get("title", ""))
                link = w.get("link", "")
                snippet = _clean_text(w.get("snippet", ""))

                wp = doc.add_paragraph()
                run = wp.add_run(f"• {title_text}")
                run.font.size = Pt(10)

                if snippet:
                    sp = doc.add_paragraph()
                    run = sp.add_run(f"  {snippet[:120]}")
                    run.font.size = Pt(9)
                    run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

                if link:
                    lp = doc.add_paragraph()
                    run = lp.add_run("  원문: ")
                    run.font.size = Pt(8)
                    _add_hyperlink(lp, title_text[:60] + ("..." if len(title_text) > 60 else ""), link)
                    all_refs.append({"title": title_text, "source": "", "link": link, "domain": expert_name})

    # ══════════ References ══════════
    doc.add_page_break()
    h = doc.add_heading("참고문헌 (References)", level=2)
    _add_bookmark(h, "sec_master_refs")

    doc.add_paragraph(
        f"본 마스터 리포트에 인용된 총 {len(all_refs)}건의 원문 링크입니다. "
        f"각 항목의 하이퍼링크를 클릭하면 원문 페이지로 이동합니다."
    )

    # Group by domain
    from collections import defaultdict
    refs_by_domain = defaultdict(list)
    for ref in all_refs:
        refs_by_domain[ref.get("domain", "기타")].append(ref)

    ref_global_idx = 1
    for domain_name, refs in refs_by_domain.items():
        p = doc.add_paragraph()
        run = p.add_run(f"■ {domain_name}")
        run.bold = True
        run.font.size = Pt(10)

        for ref in refs:
            if ref.get("link"):
                p = doc.add_paragraph()
                run = p.add_run(f"  [{ref_global_idx}] ")
                run.font.size = Pt(8)
                label = ref.get("title", "")[:100]
                if ref.get("source"):
                    label += f" — {ref['source']}"
                _add_hyperlink(p, label, ref["link"])
                ref_global_idx += 1

    # ── Footer ──
    doc.add_paragraph("")
    doc.add_paragraph("")
    footer = doc.add_paragraph()
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer.add_run("━" * 40)
    run.font.color.rgb = RGBColor(0xCC, 0xCC, 0xCC)
    footer2 = doc.add_paragraph()
    footer2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer2.add_run(f"전 분야 마스터 리포트 — 자동 생성  |  {now_str}")
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor(0xAA, 0xAA, 0xAA)
    footer3 = doc.add_paragraph()
    footer3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer3.add_run("Powered by Life-Info Expert Analysis System")
    run.font.size = Pt(7)
    run.font.color.rgb = RGBColor(0xBB, 0xBB, 0xBB)
    run.italic = True

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════════
# Plain text generators
# ═══════════════════════════════════════════════════════════════════════════════

def _gen_text(query, news, web, trend, now_str) -> bytes:
    lines = [f"생활정보 분석 리포트 — {query}", f"생성일시: {now_str}", "=" * 60, ""]

    if trend:
        values = [r.get("Trend", 0) for r in trend]
        stats = _calc_statistics(values) if len(values) >= 2 else {}
        lines.append("[ 트렌드 데이터 ]")
        for row in trend:
            lines.append(f"  {row.get('Date', '')}  →  {row.get('Trend', '')}")
        if stats:
            lines.append(f"\n  평균: {stats['mean']:,.1f}  |  변동률: {stats['pct_change']:+.1f}%  |  추세: {stats['trend_dir']}")
        lines.append("")

    if news:
        lines.append("[ 관련 뉴스 ]")
        for n in news[:10]:
            lines.append(f"  - {n.get('title', '')} ({n.get('source', '')})")
            snippet = n.get('snippet', '')
            if snippet:
                lines.append(f"    요약: {snippet[:100]}")
            lines.append(f"    링크: {n.get('link', '')}")
        flow = _news_flow_summary(news, query)
        if flow:
            lines.append(f"\n  [흐름분석] {flow}")
        lines.append("")

    if web:
        lines.append("[ 웹 검색 결과 ]")
        for w in web[:10]:
            lines.append(f"  - {w.get('title', '')}")
            lines.append(f"    {w.get('link', '')}")
    return "\n".join(lines).encode("utf-8")


def _gen_text_master(context_list, now_str) -> bytes:
    lines = ["전 분야 마스터 리포트", f"생성일시: {now_str}", "=" * 60, ""]
    for i, item in enumerate(context_list):
        if not isinstance(item, dict):
            continue
        expert_name = item.get("expert", item.get("query", f"분야 {i + 1}"))
        query = item.get("query", expert_name)
        lines.append(f"{'─' * 40}")
        lines.append(f"■ [{i + 1}] {expert_name}")
        lines.append(f"  검색어: {query}")
        trend = item.get("df", [])
        if trend:
            values = [r.get("Trend", 0) for r in trend]
            stats = _calc_statistics(values) if len(values) >= 2 else {}
            for row in trend:
                lines.append(f"  {row.get('Date', '')} → {row.get('Trend', '')}")
            if stats:
                lines.append(f"  평균: {stats['mean']:,.1f}  |  변동률: {stats['pct_change']:+.1f}%  |  추세: {stats['trend_dir']}")
        for n in item.get("news", [])[:5]:
            lines.append(f"  뉴스: {n.get('title', '')} ({n.get('source', '')})")
            lines.append(f"        {n.get('link', '')}")
        for w in item.get("web", [])[:3]:
            lines.append(f"  웹: {w.get('title', '')}")
            lines.append(f"      {w.get('link', '')}")
        lines.append("")
    return "\n".join(lines).encode("utf-8")


# ═══════════════════════════════════════════════════════════════════════════════
# Excel generators
# ═══════════════════════════════════════════════════════════════════════════════

def _gen_excel(query, news, web, trend, now_str) -> bytes:
    try:
        import xlsxwriter
        buf = io.BytesIO()
        wb = xlsxwriter.Workbook(buf)
        bold = wb.add_format({"bold": True})
        header_fmt = wb.add_format({"bold": True, "bg_color": "#1A237E", "font_color": "white"})

        # Trend sheet
        ws1 = wb.add_worksheet("트렌드")
        ws1.write(0, 0, f"분석 키워드: {query}", bold)
        ws1.write(1, 0, f"생성일시: {now_str}")
        ws1.write(3, 0, "날짜", header_fmt)
        ws1.write(3, 1, "트렌드", header_fmt)
        for i, row in enumerate(trend or []):
            ws1.write(4 + i, 0, str(row.get("Date", "")))
            ws1.write(4 + i, 1, row.get("Trend", 0))

        # Statistics
        if trend and len(trend) >= 2:
            values = [r.get("Trend", 0) for r in trend]
            stats = _calc_statistics(values)
            r = 4 + len(trend) + 1
            ws1.write(r, 0, "통계", bold)
            stat_items = [("평균", stats['mean']), ("표준편차", stats['std_dev']),
                          ("최고", stats['max']), ("최저", stats['min']),
                          ("변동률(%)", stats['pct_change'])]
            for j, (label, val) in enumerate(stat_items):
                ws1.write(r + 1 + j, 0, label)
                ws1.write(r + 1 + j, 1, round(val, 2))

        # News sheet
        ws2 = wb.add_worksheet("뉴스")
        ws2.write(0, 0, "No.", header_fmt)
        ws2.write(0, 1, "제목", header_fmt)
        ws2.write(0, 2, "출처", header_fmt)
        ws2.write(0, 3, "요약", header_fmt)
        ws2.write(0, 4, "링크", header_fmt)
        for i, n in enumerate(news or []):
            ws2.write(1 + i, 0, i + 1)
            ws2.write(1 + i, 1, n.get("title", ""))
            ws2.write(1 + i, 2, n.get("source", ""))
            ws2.write(1 + i, 3, n.get("snippet", ""))
            ws2.write(1 + i, 4, n.get("link", ""))
        ws2.set_column(1, 1, 40)
        ws2.set_column(3, 3, 50)
        ws2.set_column(4, 4, 60)

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


def _gen_excel_master(context_list, now_str) -> bytes:
    try:
        import xlsxwriter
        buf = io.BytesIO()
        wb = xlsxwriter.Workbook(buf)
        bold = wb.add_format({"bold": True})
        header_fmt = wb.add_format({"bold": True, "bg_color": "#1A237E", "font_color": "white"})

        # Summary sheet
        ws_sum = wb.add_worksheet("총괄 요약")
        ws_sum.write(0, 0, "전 분야 마스터 리포트", bold)
        ws_sum.write(1, 0, f"생성일시: {now_str}")
        ws_sum.write(3, 0, "분야", header_fmt)
        ws_sum.write(3, 1, "검색어", header_fmt)
        ws_sum.write(3, 2, "뉴스수", header_fmt)
        ws_sum.write(3, 3, "웹수", header_fmt)
        ws_sum.write(3, 4, "추세", header_fmt)
        ws_sum.write(3, 5, "변동률", header_fmt)

        for idx, item in enumerate(context_list):
            if not isinstance(item, dict):
                continue
            r = 4 + idx
            ws_sum.write(r, 0, item.get("expert", ""))
            ws_sum.write(r, 1, item.get("query", ""))
            ws_sum.write(r, 2, len(item.get("news", [])))
            ws_sum.write(r, 3, len(item.get("web", [])))
            trend = item.get("df", [])
            if trend and len(trend) >= 2:
                first_v = trend[0].get("Trend", 0)
                last_v = trend[-1].get("Trend", 0)
                if first_v > 0:
                    pct = ((last_v - first_v) / first_v) * 100
                    ws_sum.write(r, 4, "상승" if pct > 0 else "하락")
                    ws_sum.write(r, 5, round(pct, 1))

        ws_sum.set_column(0, 0, 15)
        ws_sum.set_column(1, 1, 40)

        # Per-expert sheets
        for i, item in enumerate(context_list):
            if not isinstance(item, dict):
                continue
            name = item.get("expert", f"분야{i + 1}")[:31]
            ws = wb.add_worksheet(name)
            ws.write(0, 0, f"분야: {name}", bold)
            ws.write(1, 0, f"검색어: {item.get('query', '')}")
            ws.write(2, 0, f"생성일시: {now_str}")
            ws.write(4, 0, "날짜", header_fmt)
            ws.write(4, 1, "트렌드", header_fmt)
            for j, row in enumerate(item.get("df", [])):
                ws.write(5 + j, 0, str(row.get("Date", "")))
                ws.write(5 + j, 1, row.get("Trend", 0))
            row_offset = 5 + len(item.get("df", [])) + 1
            ws.write(row_offset, 0, "뉴스 제목", header_fmt)
            ws.write(row_offset, 1, "출처", header_fmt)
            ws.write(row_offset, 2, "요약", header_fmt)
            ws.write(row_offset, 3, "링크", header_fmt)
            for j, n in enumerate(item.get("news", [])):
                ws.write(row_offset + 1 + j, 0, n.get("title", ""))
                ws.write(row_offset + 1 + j, 1, n.get("source", ""))
                ws.write(row_offset + 1 + j, 2, n.get("snippet", ""))
                ws.write(row_offset + 1 + j, 3, n.get("link", ""))
            ws.set_column(0, 0, 30)
            ws.set_column(2, 2, 50)
            ws.set_column(3, 3, 60)
        wb.close()
        return buf.getvalue()
    except ImportError:
        return _gen_text_master(context_list, now_str)


# ═══════════════════════════════════════════════════════════════════════════════
# Main dispatcher
# ═══════════════════════════════════════════════════════════════════════════════

def _generate_local_report(report_format: str, context=None) -> bytes:
    """Generate report locally (standalone mode). context can be dict or list."""
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Master report: context is a list of dicts (one per expert domain)
    if isinstance(context, list):
        if report_format == "word":
            return _gen_word_master(context, now_str)
        elif report_format == "excel":
            return _gen_excel_master(context, now_str)
        else:
            return _gen_text_master(context, now_str)

    if isinstance(context, dict):
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
    """Render report download section. Works in both API and standalone mode.

    Pre-generates all formats on first render to avoid page scroll jump
    when download buttons appear dynamically.
    """
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

    # Compute a stable cache key from context to avoid regeneration on every rerun
    import hashlib
    ctx_hash = ""
    if context:
        try:
            ctx_str = str(context.get("query", "")) if isinstance(context, dict) else str(len(context))
            ctx_hash = hashlib.md5(ctx_str.encode()).hexdigest()[:8]
        except Exception:
            ctx_hash = "default"

    now_str = datetime.datetime.now().strftime('%Y%m%d_%H%M')
    prefix = "Master_Report" if isinstance(context, list) else ("Expert_Report" if context else "LifeInfo_Summary")

    formats = [
        ("Word (.docx)", "word", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "📝", ".docx"),
        ("텍스트 (.txt)", "text", "text/plain", "📄", ".txt"),
        ("Excel (.xlsx)", "excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "📊", ".xlsx"),
    ]

    # Use session_state to cache generated reports, avoiding regeneration + scroll jump
    cache_key = f"_report_cache_{ctx_hash}"
    if cache_key not in st.session_state:
        st.session_state[cache_key] = {}

    cached = st.session_state[cache_key]

    cols = st.columns(3)
    for i, (label, fmt, mime_type, icon, ext) in enumerate(formats):
        with cols[i]:
            filename = f"{prefix}_{now_str}{ext}"

            if fmt in cached and cached[fmt]:
                # Already generated — show download button directly (no layout shift)
                st.download_button(
                    label=f"{icon} {label} 저장",
                    data=cached[fmt],
                    file_name=filename,
                    mime=mime_type,
                    key=f"dl_{fmt}_{ctx_hash}",
                )
            else:
                # Show generate button
                if st.button(f"{icon} {label} 생성", key=f"btn_gen_{fmt}_{ctx_hash}"):
                    with st.spinner(f"{label} 생성 중..."):
                        content = None
                        if IS_API_MODE:
                            content = download_report_from_api(fmt, context)
                        if not content:
                            content = _generate_local_report(fmt, context)
                        if content:
                            cached[fmt] = content
                            st.session_state[cache_key] = cached
                            st.rerun()
