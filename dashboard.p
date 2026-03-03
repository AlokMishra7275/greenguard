import streamlit as st
import pandas as pd
import google.generativeai as genai
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="GreenGuard AI",
    page_icon="🌍",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
body {
    background-color: #0E1117;
}
.metric-card {
    background: linear-gradient(135deg, #1f2937, #111827);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    color: white;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
}
.section-header {
    font-size: 26px;
    font-weight: 600;
    margin-top: 20px;
}
.alert-box {
    background-color: #7f1d1d;
    padding: 15px;
    border-radius: 10px;
    color: white;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.title("🌍 GreenGuard - Real-Time Air Intelligence System")

# ---------------- GEMINI SETUP ----------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-pro")

# ---------------- LOAD DATA ----------------
try:
    ranking = pd.read_csv("city_ranking.csv")
    data = pd.read_csv("aqi_data.csv")
except:
    st.error("Data not found. Ensure backend & pathway are running.")
    st.stop()

latest_data = (
    data.sort_values("Timestamp")
    .groupby("City")
    .tail(1)
)

ranking = ranking.sort_values("risk_index", ascending=False)

# ---------------- KPI SECTION ----------------
st.markdown('<div class="section-header">📊 Live Air Quality Status</div>', unsafe_allow_html=True)

cols = st.columns(len(latest_data))

for i, (_, row) in enumerate(latest_data.iterrows()):
    with cols[i]:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{row['City']}</h3>
            <h1>AQI {row['AQI']}</h1>
            <p>{row['Category']}</p>
        </div>
        """, unsafe_allow_html=True)

# ---------------- TOP POLLUTED CITY ----------------
top_city = ranking.iloc[0]
st.markdown("---")
st.markdown("### 🚨 Highest Risk City")
st.error(f"{top_city['City']} has the highest risk index: {round(top_city['risk_index'],2)}")

# ---------------- RANKING TABLE ----------------
st.markdown("---")
st.markdown("### 🏆 Live City Risk Ranking")

styled = (
    ranking.style
    .background_gradient(subset=["risk_index"], cmap="Reds")
)

st.dataframe(styled, use_container_width=True)

# ---------------- CHARTS ----------------
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Average AQI by City")
    st.bar_chart(ranking.set_index("City")["avg_aqi"])

with col2:
    st.markdown("### 📈 AQI Trend")
    selected_city = st.selectbox("Select City", data["City"].unique())
    city_data = data[data["City"] == selected_city]
    st.line_chart(city_data.set_index("Timestamp")["AQI"])

# ---------------- SEVERE ALERTS ----------------
st.markdown("---")
st.markdown("### 🚨 Severe Alerts")

severe = latest_data[latest_data["AQI"] > 200]

if not severe.empty:
    st.markdown('<div class="alert-box">⚠ Severe Pollution Detected! Immediate Action Recommended.</div>', unsafe_allow_html=True)
    st.dataframe(severe, use_container_width=True)
else:
    st.success("No severe pollution currently detected.")

# ---------------- AI ADVISORY ----------------
st.markdown("---")
st.markdown("### 🧠 AI Environmental Advisory")

if st.button("Generate AI Advisory"):

    summary = ""
    for _, row in latest_data.iterrows():
        summary += (
            f"City: {row['City']}, AQI: {row['AQI']}, "
            f"Category: {row['Category']}, Pollutant: {row['Dominant_Pollutant']}\n"
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

    try:
        response = model.generate_content(prompt)
        st.info(response.text)
    except Exception as e:
        st.warning("AI temporarily unavailable.")
        st.error(e)

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("Built with Pathway + Streamlit + Gemini AI | Hack For Green Bharat")
