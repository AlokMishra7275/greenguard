import streamlit as st
import pandas as pd
from google import genai

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
@st.cache_data(ttl=10)
def load_data():
    ranking = pd.read_csv("city_ranking.csv")
    data = pd.read_csv("aqi_data.csv")
    return ranking, data

try:
    ranking, data = load_data()
except Exception as e:
    st.error("⚠ Data not available. Run backend & Pathway pipeline.")
    st.write(e)
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

    st.subheader("📊 Live AQI Status")

    cols = st.columns(len(latest_data))

    for i, (_, row) in enumerate(latest_data.iterrows()):
        with cols[i]:
            st.metric(
                label=row["City"],
                value=f"AQI {row['AQI']}",
                delta=row["Category"]
            )

    severe = latest_data[latest_data["AQI"] > 200]

    st.markdown("---")

    if not severe.empty:
        st.error("🚨 Severe Pollution Detected")
        st.dataframe(severe, width="stretch")
    else:
        st.success("No severe pollution detected.")

    st.markdown("---")
    st.subheader("📈 AQI Trend")

    selected_city = st.selectbox("Select City", data["City"].unique())
    city_data = data[data["City"] == selected_city]

    st.line_chart(city_data.set_index("Timestamp")["AQI"])

# ==========================================================
# 🔹 SECTION 2: CITY RANKING
# ==========================================================
elif section == "City Ranking":

    st.subheader("🏆 Real-Time Risk Ranking")
    st.dataframe(ranking, width="stretch")

    top_city = ranking.iloc[0]
    st.success(f"Highest Risk City: {top_city['city']}")

# ==========================================================
# 🔹 SECTION 3: AI ADVISORY
# ==========================================================
elif section == "AI Advisory":

    st.subheader("🧠 AI Environmental Advisory")

    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    except Exception as e:
        st.error("Gemini API key not configured.")
        st.write(e)
        st.stop()

    if st.button("Generate Advisory"):

        summary = ""
        for _, row in latest_data.iterrows():
            summary += (
                f"City: {row['City']}, "
                f"AQI: {row['AQI']}, "
                f"Category: {row['Category']}\n"
            )

        prompt = f"""
        Based on this AQI data:
        {summary}

        Provide:
        - Health advisory
        - Outdoor safety suggestions
        - Government action recommendations
        - Warning for children and elderly
        """

        with st.spinner("Generating advisory..."):
            try:
                response = client.models.generate_content(
                    model="gemini-1.0-pro",
                    contents=prompt,
                )

                st.success(response.text)

            except Exception as e:
                st.error("AI generation failed")
                st.write(e)
# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("© GreenGuard | Hackathon Edition | Real-Time AI Environmental Intelligence Platform")
