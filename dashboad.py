import streamlit as st
import pandas as pd
import google.generativeai as genai
import time

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="GreenGuard AI Platform",
    page_icon="🌍",
    layout="wide"
)

# ---------------- STYLING ----------------
st.markdown("""
<style>
.main {
    background-color: #0E1117;
}
.kpi-card {
    background: linear-gradient(135deg, #1f2937, #111827);
    padding: 20px;
    border-radius: 15px;
    color: white;
    text-align: center;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.5);
}
.section-title {
    font-size: 24px;
    font-weight: 600;
    margin-top: 20px;
}
.alert-banner {
    background-color: #7f1d1d;
    padding: 15px;
    border-radius: 10px;
    color: white;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.title("🌍 GreenGuard – Real-Time Environmental Intelligence")

# ---------------- SIDEBAR ----------------
st.sidebar.title("Navigation")
section = st.sidebar.radio(
    "Go to",
    ["Live Dashboard", "City Ranking", "AI Advisory"]
)

st.sidebar.markdown("---")
st.sidebar.caption("Powered by Pathway + Gemini AI")

# ---------------- LOAD DATA ----------------
@st.cache_data(ttl=10)
def load_data():
    ranking = pd.read_csv("city_ranking.csv")
    data = pd.read_csv("aqi_data.csv")
    return ranking, data

try:
    ranking, data = load_data()
except:
    st.error("⚠ Data not available. Run backend & Pathway pipeline.")
    st.stop()

latest_data = (
    data.sort_values("Timestamp")
    .groupby("City")
    .tail(1)
)

ranking = ranking.sort_values("risk_index", ascending=False)

# ==========================================================
# 🔹 SECTION 1: LIVE DASHBOARD
# ==========================================================
if section == "Live Dashboard":

    st.markdown('<div class="section-title">📊 Live AQI Status</div>', unsafe_allow_html=True)

    cols = st.columns(len(latest_data))

    for i, (_, row) in enumerate(latest_data.iterrows()):
        with cols[i]:
            st.markdown(f"""
            <div class="kpi-card">
                <h3>{row['City']}</h3>
                <h1>AQI {row['AQI']}</h1>
                <p>{row['Category']}</p>
            </div>
            """, unsafe_allow_html=True)

    # Severe alert
    severe = latest_data[latest_data["AQI"] > 200]

    st.markdown("---")
    if not severe.empty:
        st.markdown('<div class="alert-banner">🚨 Severe Pollution Detected! Immediate Action Required.</div>', unsafe_allow_html=True)
        st.dataframe(severe, use_container_width=True)
    else:
        st.success("No severe pollution detected.")

    # Trend chart
    st.markdown("---")
    st.subheader("📈 AQI Trend")
    selected_city = st.selectbox("Select City", data["City"].unique())
    city_data = data[data["City"] == selected_city]
    st.line_chart(city_data.set_index("Timestamp")["AQI"])

# ==========================================================
# 🔹 SECTION 2: CITY RANKING
# ==========================================================
elif section == "City Ranking":

    st.markdown('<div class="section-title">🏆 Real-Time Risk Ranking</div>', unsafe_allow_html=True)

    top_city = ranking.iloc[0]
    st.error(f"Highest Risk: {top_city['City']} (Index: {round(top_city['risk_index'],2)})")

    styled = ranking.style.background_gradient(
        subset=["risk_index"], cmap="Reds"
    )

    st.dataframe(styled, use_container_width=True)

    st.markdown("---")
    st.subheader("📊 Average AQI Comparison")
    st.bar_chart(ranking.set_index("City")["avg_aqi"])

# ==========================================================
# 🔹 SECTION 3: AI ADVISORY
# ==========================================================
elif section == "AI Advisory":

    st.markdown('<div class="section-title">🧠 AI Environmental Advisory</div>', unsafe_allow_html=True)

    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")
    except:
        st.error("Gemini API key not configured properly.")
        st.stop()

    if st.button("Generate Advisory"):

        summary = ""
        for _, row in latest_data.iterrows():
            summary += (
                f"City: {row['City']}, "
                f"AQI: {row['AQI']}, "
                f"Category: {row['Category']}, "
                f"Pollutant: {row['Dominant_Pollutant']}\n"
            )

        prompt = f"""
        You are an environmental health expert.

        Based on this AQI data:
        {summary}

        Provide:
        - Health advisory
        - Outdoor safety suggestions
        - Government action recommendations
        - Warnings for children and elderly
        """

        with st.spinner("Generating AI advisory..."):
            try:
                response = model.generate_content(prompt)
                st.success(response.text)
            except Exception as e:
                st.warning("AI service temporarily unavailable.")
                st.error(e)

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("© GreenGuard | Hackathon Edition | Real-Time AI Environmental Monitoring")
