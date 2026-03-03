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
    
    # Ensure timestamp is datetime
    data["Timestamp"] = pd.to_datetime(data["Timestamp"])
    
    return ranking, data

try:
    ranking, data = load_data()
except Exception:
    st.error("⚠ Data files not found. Ensure backend is generating CSV files.")
    st.stop()

# Get latest AQI per city
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
    st.title("🌍 Live Air Quality Overview")

    cols = st.columns(len(latest))

    for i, (_, row) in enumerate(latest.iterrows()):
        label, emoji = aqi_label(row["AQI"])

        with cols[i]:
            st.metric(
                label=row["City"],
                value=f"{emoji} {row['AQI']}",
                delta=label
            )

    st.markdown("---")
    st.subheader("📋 Latest Raw Data")
    st.dataframe(latest, use_container_width=True)

# =====================================================
# 📈 TRENDS PAGE
# =====================================================
elif page == "📈 Trends":
    st.title("📈 AQI Trends Over Time")

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
        yaxis_title="Air Quality Index"
    )

    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# 🏆 RANKING PAGE
# =====================================================
elif page == "🏆 Ranking":
    st.title("🏆 Real-Time Risk Ranking")

    st.dataframe(
        ranking.reset_index(drop=True),
        use_container_width=True
    )

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
    st.title("🤖 AI Environmental Advisory")

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
st.markdown("---")
st.markdown(
    "<p style='text-align:center; font-size:12px;'>© 2026 GreenGuard | AI Environmental Intelligence Platform</p>",
    unsafe_allow_html=True
)
