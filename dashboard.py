import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="GreenGuard 🌍",
    page_icon="🌿",
    layout="wide"
)

# ---------------- GLOBAL CSS ----------------
st.markdown("""
<style>
/* Global background & font */
body {
    background: radial-gradient(circle at top, #e8ffe8 0, #f5f7fb 40%, #eef3ff 100%);
    font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

/* Hide default Streamlit chrome */
/* Hide default Streamlit chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
/* header {visibility: hidden;}   <-- REMOVE or comment this */

/* Main container padding */
.block-container {
    padding-top: 0.8rem;
    padding-bottom: 0.8rem;
    max-width: 1200px;
}

/* Top navbar */
.navbar {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(12px);
    border-radius: 18px;
    padding: 0.8rem 1.4rem;
    margin-bottom: 1.2rem;
    border: 1px solid rgba(0,0,0,0.04);
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 14px 45px rgba(15, 70, 15, 0.10);
}

.nav-left {
    display: flex;
    align-items: center;
    gap: 0.65rem;
}

.brand-badge {
    width: 34px;
    height: 34px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #00c853, #64dd17);
    color: #ffffff;
    font-size: 1.3rem;
    font-weight: 700;
}

.brand-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #163300;
}

.brand-sub {
    font-size: 0.78rem;
    color: #4d5b35;
}

.nav-right {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    font-size: 0.8rem;
    color: #5f6368;
}

.nav-pill {
    padding: 0.25rem 0.8rem;
    border-radius: 999px;
    border: 1px solid rgba(0, 200, 83, 0.18);
    background: rgba(200, 255, 210, 0.7);
    color: #0b8a2a;
    font-size: 0.76rem;
    font-weight: 600;
}

/* Section titles */
.section-title {
    font-size: 1.35rem;
    font-weight: 700;
    margin-bottom: 0.15rem;
    color: #111827;
}

.section-subtitle {
    font-size: 0.88rem;
    color: #6b7280;
    margin-bottom: 0.8rem;
}

/* KPI cards */
.metric-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 0.9rem 1rem;
    box-shadow: 0 10px 25px rgba(15, 23, 42, 0.06);
    border: 1px solid rgba(148, 163, 184, 0.2);
}

.metric-label {
    font-size: 0.85rem;
    color: #6b7280;
    margin-bottom: 0.2rem;
}

.metric-main {
    font-size: 1.4rem;
    font-weight: 700;
    display: flex;
    align-items: baseline;
    gap: 0.35rem;
}

.metric-status {
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* AQI colors */
.aqi-good { color: #16a34a; }
.aqi-moderate { color: #eab308; }
.aqi-unhealthy { color: #f97316; }
.aqi-hazardous { color: #b91c1c; }

.badge-dot {
    width: 0.55rem;
    height: 0.55rem;
    border-radius: 999px;
    margin-right: 0.3rem;
    display: inline-block;
}

/* Dataframe wrapper */
.df-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 0.75rem 0.9rem;
    margin-top: 0.5rem;
    box-shadow: 0 10px 25px rgba(15, 23, 42, 0.04);
    border: 1px solid rgba(148, 163, 184, 0.25);
}

/* Custom footer */
.custom-footer {
    margin-top: 1.4rem;
    font-size: 0.76rem;
    color: #6b7280;
    text-align: center;
    padding-top: 0.6rem;
    border-top: 1px dashed rgba(148, 163, 184, 0.6);
}

.custom-footer a {
    color: #0f766e;
    text-decoration: none;
    font-weight: 500;
}
.custom-footer a:hover {
    text-decoration: underline;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TOP NAVBAR ----------------
st.markdown("""
<div class="navbar">
  <div class="nav-left">
    <div class="brand-badge">G</div>
    <div>
      <div class="brand-title">GreenGuard</div>
      <div class="brand-sub">AI Environmental Intelligence · Live AQI Insights</div>
    </div>
  </div>
  <div class="nav-right">
    <span class="nav-pill">⚡ Pathway · Gemini AI</span>
    <span>Updated in near real-time</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ---------------- AQI LABEL FUNCTION ----------------
def aqi_label(aqi):
    if aqi <= 50:
        return "Good", "🟢"
    elif aqi <= 100:
        return "Moderate", "🟡"
    elif aqi <= 200:
        return "Unhealthy", "🟠"
    else:
        return "Hazardous", "🔴"

# ---------------- LOAD DATA ----------------
@st.cache_data(ttl=30)
def load_data():
    ranking = pd.read_csv("city_ranking.csv")
    data = pd.read_csv("aqi_data.csv")
    data["Timestamp"] = pd.to_datetime(data["Timestamp"])
    return ranking, data

try:
    ranking, data = load_data()
except Exception:
    st.error("⚠ Data files not found. Ensure backend is generating CSV files.")
    st.stop()

latest = (
    data.sort_values("Timestamp")
        .groupby("City")
        .tail(1)
)

ranking = ranking.sort_values("risk_index", ascending=False)

# ---------------- SIDEBAR ----------------
st.sidebar.title("🌿 GreenGuard Navigation")
page = st.sidebar.radio(
    "Go to",
    ["📊 Overview", "📈 Trends", "🏆 Ranking", "🤖 AI Advisory"]
)
st.sidebar.markdown("---")
st.sidebar.caption("Powered by Pathway + Gemini AI")

# =====================================================
# 📊 OVERVIEW PAGE
# =====================================================
if page == "📊 Overview":
    # ----- HERO HEADER -----
    st.markdown(
        """
        <div class="section-title">🌍 GreenGuard Air Quality Overview</div>
        <div class="section-subtitle">
            Live snapshot of ambient air quality across monitored Indian cities, updated continuously from the GreenGuard data pipeline.
        </div>
        """,
        unsafe_allow_html=True
    )

    # ----- SUMMARY KPI ROW -----
    total_cities = latest["City"].nunique()
    avg_aqi = latest["AQI"].mean()
    worst_row = latest.loc[latest["AQI"].idxmax()]
    worst_label, _ = aqi_label(worst_row["AQI"])

    kpi1, kpi2, kpi3 = st.columns(3)

    with kpi1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Monitored Cities</div>
                <div class="metric-main">
                    <span>{total_cities}</span>
                </div>
                <div class="metric-status aqi-good">
                    Network coverage
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with kpi2:
        status_class = (
            "aqi-good" if avg_aqi <= 50 else
            "aqi-moderate" if avg_aqi <= 100 else
            "aqi-unhealthy" if avg_aqi <= 200 else
            "aqi-hazardous"
        )
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Average AQI</div>
                <div class="metric-main {status_class}">
                    <span>{int(avg_aqi)}</span>
                </div>
                <div class="metric-status {status_class}">
                    Network health
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with kpi3:
        worst_class = (
            "aqi-good" if worst_label == "Good" else
            "aqi-moderate" if worst_label == "Moderate" else
            "aqi-unhealthy" if worst_label == "Unhealthy" else
            "aqi-hazardous"
        )
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Highest AQI City</div>
                <div class="metric-main {worst_class}">
                    <span>{worst_row['City']}</span>
                </div>
                <div class="metric-status {worst_class}">
                    <span class="badge-dot" style="background:currentColor;"></span>{worst_label} · {int(worst_row['AQI'])}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ----- CITY CARDS -----
    st.markdown(
        "<div class='section-title'>City-wise Live AQI</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='section-subtitle'>Per-city status with emoji and health banding for quick scanning.</div>",
        unsafe_allow_html=True
    )

    cols = st.columns(len(latest))

    for i, (_, row) in enumerate(latest.iterrows()):
        label, emoji = aqi_label(row["AQI"])

        if label == "Good":
            status_class = "aqi-good"
        elif label == "Moderate":
            status_class = "aqi-moderate"
        elif label == "Unhealthy":
            status_class = "aqi-unhealthy"
        else:
            status_class = "aqi-hazardous"

        with cols[i]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{row['City']}</div>
                <div class="metric-main {status_class}">
                    <span>{emoji} {int(row['AQI'])}</span>
                </div>
                <div class="metric-status {status_class}">
                    <span class="badge-dot" style="background:currentColor;"></span>{label}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ----- RAW DATA TABLE -----
    st.markdown(
        "<div class='section-title' style='margin-top:1.2rem;'>📋 Latest Raw Data</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='section-subtitle'>Underlying records for the most recent observation per city.</div>",
        unsafe_allow_html=True
    )
    st.markdown("<div class='df-card'>", unsafe_allow_html=True)
    st.dataframe(latest, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# 📈 TRENDS PAGE
# =====================================================
elif page == "📈 Trends":
    st.markdown('<div class="section-title">📈 AQI Trends Over Time</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Drill down into time-series AQI behaviour for a selected city.</div>',
        unsafe_allow_html=True
    )

    selected_city = st.selectbox(
        "Select City",
        sorted(data["City"].unique())
    )

    city_df = data[data["City"] == selected_city]

    fig = px.line(
        city_df,
        x="Timestamp",
        y="AQI",
        title=f"AQI Trend — {selected_city}",
        markers=True
    )

    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Time",
        yaxis_title="Air Quality Index",
        title_x=0.02,
        margin=dict(l=10, r=10, t=50, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# 🏆 RANKING PAGE
# =====================================================
elif page == "🏆 Ranking":
    st.markdown('<div class="section-title">🏆 Real-Time Risk Ranking</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Cities ordered by composite risk index combining AQI severity and persistence.</div>',
        unsafe_allow_html=True
    )

    st.markdown("<div class='df-card'>", unsafe_allow_html=True)
    st.dataframe(
        ranking.reset_index(drop=True),
        use_container_width=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if not ranking.empty:
        top = ranking.iloc[0]
        st.success(
            f"🔥 Highest Risk City: {top['city']} "
            f"(Risk Index: {top['risk_index']:.2f})"
        )

# =====================================================
# 🤖 AI ADVISORY PAGE
# =====================================================
elif page == "🤖 AI Advisory":
    st.markdown('<div class="section-title">🤖 AI Environmental Advisory</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Policy-grade recommendations and public health advisories generated from live AQI signals.</div>',
        unsafe_allow_html=True
    )

    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")
    except Exception:
        st.error("❌ Gemini API key not configured in Streamlit Secrets.")
        st.stop()

    if st.button("📌 Generate AI Advisory"):

        summary = "\n".join(
            [
                f"{r['City']}: AQI {r['AQI']} ({aqi_label(r['AQI'])[0]})"
                for _, r in latest.iterrows()
            ]
        )

        prompt = f"""
        You are an environmental policy expert.

        Based on this live AQI data:
        {summary}

        Provide:
        1. Public health advisory
        2. Outdoor activity safety tips
        3. Government action recommendations
        4. Alerts for children & elderly

        Keep it clear and actionable.
        """

        with st.spinner("🧠 Generating advisory..."):
            try:
                response = model.generate_content(prompt)
                st.markdown(response.text)
            except Exception as e:
                st.error(f"AI generation failed: {e}")

# ---------------- FOOTER ----------------
st.markdown("""
<div class="custom-footer">
  © 2026 GreenGuard · AI Environmental Intelligence Platform · Built with Streamlit ·
  <a href="https://aigreenguard1.streamlit.app/" target="_blank">Live dashboard</a>
</div>
""", unsafe_allow_html=True)
