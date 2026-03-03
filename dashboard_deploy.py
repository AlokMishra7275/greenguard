import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="GreenGuard Industrial Monitor",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------------------------------------
# CUSTOM CSS (Corporate Industrial Theme)
# --------------------------------------------------
st.markdown("""
<style>

body {
    background-color: #F8FAFC;
}

.main-title {
    font-size: 34px;
    font-weight: 700;
    color: #0F172A;
}

.sub-title {
    font-size: 16px;
    color: #64748B;
}

.kpi-card {
    background: white;
    padding: 20px;
    border-radius: 14px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
}

.alert-box {
    padding: 15px;
    border-radius: 10px;
    font-weight: 500;
}

.safe {
    background-color: #DCFCE7;
    color: #166534;
}

.warning {
    background-color: #FEF3C7;
    color: #92400E;
}

.danger {
    background-color: #FEE2E2;
    color: #991B1B;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------
col1, col2 = st.columns([4,1])

with col1:
    st.markdown('<div class="main-title">🏭 GreenGuard Industrial Monitor</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Real-Time CO₂ Emission & AQI Compliance Intelligence</div>', unsafe_allow_html=True)

with col2:
    st.success("🟢 System Active")
    st.caption(f"Last Updated: {datetime.now().strftime('%H:%M:%S')}")

st.markdown("---")

# --------------------------------------------------
# SIMULATED REAL-TIME DATA (Replace with Pathway output)
# --------------------------------------------------
plants = ["Plant A", "Plant B", "Plant C", "Plant D"]

co2_values = np.random.randint(380, 480, size=4)
aqi_values = np.random.randint(80, 220, size=4)

avg_co2 = int(np.mean(co2_values))
avg_aqi = int(np.mean(aqi_values))

# --------------------------------------------------
# KPI SECTION
# --------------------------------------------------
k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown('<div class="kpi-card">🏭 <b>Active Plants</b><br><h3>4</h3></div>', unsafe_allow_html=True)

with k2:
    st.markdown(f'<div class="kpi-card">🌍 <b>Avg CO₂ (ppm)</b><br><h3>{avg_co2}</h3></div>', unsafe_allow_html=True)

with k3:
    st.markdown(f'<div class="kpi-card">🌫 <b>Avg AQI</b><br><h3>{avg_aqi}</h3></div>', unsafe_allow_html=True)

with k4:
    change = np.random.uniform(-5, 5)
    st.markdown(f'<div class="kpi-card">📉 <b>Emission Change</b><br><h3>{change:.2f}%</h3></div>', unsafe_allow_html=True)

with k5:
    risk = "Low" if avg_aqi < 100 else "Medium" if avg_aqi < 180 else "High"
    st.markdown(f'<div class="kpi-card">⚠ <b>Compliance Risk</b><br><h3>{risk}</h3></div>', unsafe_allow_html=True)

st.markdown("---")

# --------------------------------------------------
# TREND CHARTS
# --------------------------------------------------
time_series = pd.date_range(end=datetime.now(), periods=20, freq="T")
co2_trend = np.random.randint(390, 470, size=20)
aqi_trend = np.random.randint(90, 200, size=20)

col1, col2 = st.columns(2)

with col1:
    fig1 = px.line(
        x=time_series,
        y=co2_trend,
        labels={"x": "Time", "y": "CO₂ ppm"},
        title="CO₂ Emission Trend"
    )
    fig1.update_layout(template="plotly_white")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.line(
        x=time_series,
        y=aqi_trend,
        labels={"x": "Time", "y": "AQI"},
        title="AQI Trend"
    )
    fig2.update_layout(template="plotly_white")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# --------------------------------------------------
# PLANT COMPARISON
# --------------------------------------------------
df = pd.DataFrame({
    "Plant": plants,
    "CO₂ ppm": co2_values,
    "AQI": aqi_values
})

col1, col2 = st.columns(2)

with col1:
    fig3 = px.bar(df, x="Plant", y="CO₂ ppm", title="Plant-wise CO₂ Emission")
    fig3.update_layout(template="plotly_white")
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    fig4 = px.bar(df, x="Plant", y="AQI", title="Plant-wise AQI Level")
    fig4.update_layout(template="plotly_white")
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# --------------------------------------------------
# ALERT SECTION
# --------------------------------------------------
st.subheader("🚨 Compliance & Risk Alerts")

if avg_aqi > 180:
    st.markdown('<div class="alert-box danger">High Risk: AQI exceeded safe industrial threshold.</div>', unsafe_allow_html=True)
elif avg_aqi > 120:
    st.markdown('<div class="alert-box warning">Moderate Risk: AQI approaching compliance limit.</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="alert-box safe">All Plants Operating Within Safe Environmental Limits.</div>', unsafe_allow_html=True)
