import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="GreenGuard 🌍",
    page_icon="🌿",
    layout="wide"
)

# 🔎 AQI COLOR UTIL
def aqi_label(aqi):
    if aqi <= 50: return ("Good", "🟢")
    if aqi <= 100: return ("Moderate", "🟡")
    if aqi <= 200: return ("Unhealthy", "🟠")
    return ("Hazardous", "🔴")

# ---------------- LOAD DATA ----------------
@st.cache_data(ttl=15)
def load_data():
    ranking = pd.read_csv("city_ranking.csv")
    data = pd.read_csv("aqi_data.csv")
    return ranking, data

try:
    ranking, data = load_data()
except Exception as e:
    st.error("⚠ Data missing. Please ensure backend is running.")
    st.stop()

latest = data.sort_values("Timestamp").groupby("City").tail(1)
ranking = ranking.sort_values("risk_index", ascending=False)

# ---------------- SIDEBAR ----------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("", ["📊 Overview", "📈 Trends", "🏆 Ranking", "🤖 AI Advisory"])
st.sidebar.markdown("---")
st.sidebar.caption("Powered by Pathway + Gemini AI")

# =======================
# 📊 LIVE OVERVIEW
# =======================
if page == "📊 Overview":
    st.header("🌍 Live Air Quality Index (AQI) — At a Glance")

    cols = st.columns(len(latest))
    for i, (_, row) in enumerate(latest.iterrows()):
        label, emoji = aqi_label(row["AQI"])
        with cols[i]:
            st.markdown(f"""
                <div style="background:#1f2937; padding: 15px; border-radius:12px; text-align:center; color:white;">
                  <h3>{row['City']}</h3>
                  <h1 style="font-size:32px;">{emoji} {row['AQI']}</h1>
                  <p>{label}</p>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📋 Raw Latest Data")
    st.dataframe(latest, use_container_width=True)

# =======================
# 📈 AQI TRENDS
# =======================
elif page == "📈 Trends":
    st.header("📈 AQI Trends Over Time")

    selected_city = st.selectbox("Select City", data["City"].unique())
    city_df = data[data["City"] == selected_city]

    fig = px.line(
        city_df,
        x="Timestamp",
        y="AQI",
        title=f"AQI Trend — {selected_city}",
        labels={"AQI": "Air Quality Index", "Timestamp": "Time"},
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)

# =======================
# 🏆 RISK RANKING
# =======================
elif page == "🏆 Ranking":
    st.header("🏅 Real-Time City Risk Ranking")

    st.dataframe(ranking.reset_index(drop=True), use_container_width=True)

    top = ranking.iloc[0]
    st.success(f"🔥 Highest Risk: {top['city']} (Risk Index: {top['risk_index']:.1f})")

# =======================
# 🤖 AI ADVISORY
# =======================
elif page == "🤖 AI Advisory":
    st.header("🤖 AI Environmental Advisory")

    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    except Exception:
        st.error("❌ Gemini API key not configured in Secrets.")
        st.stop()

    st.write("Click the button to generate contextual environmental advisory:")

    if st.button("📌 Generate AI Advisory"):
        summary = ""
        for _, r in latest.iterrows():
            summary += f"{r['City']}: AQI {r['AQI']} ({aqi_label(r['AQI'])[0]})\n"

        prompt = f"""
        You are an environmental expert. Based on this live AQI data:
        {summary}

        Provide:
        - Health advisory for the public
        - Outdoor activity safety tips
        - Government action recommendations
        - Warnings for children & elderly
        """

        with st.spinner("🧠 Generating advisory..."):
            try:
                model = genai.GenerativeModel("gemini-pro")
                response = model.generate_content(prompt)
                st.markdown(response.text)

            except Exception as e:
                st.error(f"AI generation failed: {e}")

# =======================
# FOOTER
# =======================
st.markdown("---")
st.markdown(
    "<p style='text-align:center; font-size:12px;'>© 2026 GreenGuard | Real-Time AI Environmental Intelligence Platform</p>",
    unsafe_allow_html=True
)
