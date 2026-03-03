import streamlit as st
import pandas as pd
import google.generativeai as genai

def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="GreenGuard AI Platform",
    page_icon="🌍",
    layout="wide"
)

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
@st.cache_data(ttl=15)
def load_data():
    ranking = pd.read_csv("city_ranking.csv")
    data = pd.read_csv("aqi_data.csv")
    return ranking, data

try:
    ranking, data = load_data()
except Exception as e:
    st.error("⚠ Data not available. Please check backend pipeline.")
    st.stop()

latest_data = (
    data.sort_values("Timestamp")
    .groupby("City")
    .tail(1)
)

ranking = ranking.sort_values("risk_index", ascending=False)

# ---------------- AQI COLOR FUNCTION ----------------
def aqi_color(aqi):
    if aqi <= 50:
        return "🟢 Good"
    elif aqi <= 100:
        return "🟡 Moderate"
    elif aqi <= 200:
        return "🟠 Unhealthy"
    else:
        return "🔴 Severe"

# ==========================================================
# 🔹 SECTION 1: LIVE DASHBOARD
# ==========================================================
if section == "Live Dashboard":

    st.subheader("📊 Live AQI Status")

    cols = st.columns(len(latest_data))

    for i, (_, row) in enumerate(latest_data.iterrows()):
        with cols[i]:
            st.metric(
                label=row["City"],
                value=f"AQI {row['AQI']}",
                delta=aqi_color(row["AQI"])
            )

    st.markdown("---")

    severe = latest_data[latest_data["AQI"] > 200]

    if not severe.empty:
        st.error("🚨 Severe Pollution Detected")
        st.dataframe(severe, use_container_width=True)
    else:
        st.success("✅ No severe pollution detected.")

    st.markdown("---")
    st.subheader("📈 AQI Trend Analysis")

    selected_city = st.selectbox("Select City", data["City"].unique())
    city_data = data[data["City"] == selected_city]

    st.line_chart(city_data.set_index("Timestamp")["AQI"])

# ==========================================================
# 🔹 SECTION 2: CITY RANKING
# ==========================================================
elif section == "City Ranking":

    st.subheader("🏆 Real-Time Risk Ranking")

    st.dataframe(ranking, use_container_width=True)

    top_city = ranking.iloc[0]
    st.success(f"🔥 Highest Risk City: {top_city['city']}")

# ==========================================================
# 🔹 SECTION 3: AI ADVISORY
# ==========================================================
elif section == "AI Advisory":

    st.subheader("🧠 AI Environmental Advisory")

    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    except Exception:
        st.error("❌ Gemini API key not configured in Streamlit Secrets.")
        st.stop()

    if st.button("Generate Smart Advisory"):

        summary = ""
        for _, row in latest_data.iterrows():
            summary += (
                f"City: {row['City']}, "
                f"AQI: {row['AQI']}, "
                f"Category: {row['Category']}\n"
            )

        prompt = f"""
        You are an environmental risk expert.

        Based on this AQI data:
        {summary}

        Provide:
        1. Public health advisory
        2. Outdoor activity recommendations
        3. Government emergency response suggestions
        4. Specific warning for children & elderly
        Keep response concise but professional.
        """

        with st.spinner("🤖 Generating AI advisory..."):
            try:
                model = genai.GenerativeModel("gemini-pro")
                response = model.generate_content(prompt)

                st.success("AI Advisory Generated")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"AI generation failed: {e}")
                st.write(e)

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("© 2026 GreenGuard | Hackathon Edition | Real-Time AI Environmental Intelligence Platform")
