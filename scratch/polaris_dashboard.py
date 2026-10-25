import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. UI Configuration
st.set_page_config(page_title="POLARIS | Energy Optimizer", layout="wide", initial_sidebar_state="collapsed")
st.title("POLARIS N6: Arctic Microgrid Receding Horizon Control")
st.markdown("Annual Simulation: Nuolja, Sweden | **100% Critical Uptime Maintained**")

# 2. Executive KPI Ribbon
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Total Diesel Consumed", value="693 Liters", delta="-68,306 L vs Baseline", delta_color="normal")
col2.metric(label="Fuel Cost Avoided", value="~€122,950", delta="99.0% Reduction", delta_color="normal")
col3.metric(label="Generator Wear (Run Hours)", value="91 Hours", delta="-6,853 hours", delta_color="inverse")
col4.metric(label="System Blackouts (Unmet Load)", value="0.00 kWh", delta="100% Reliability", delta_color="off")
st.markdown("---")

# 3. Load the Continuous Data Engine
@st.cache_data
def load_data():
    df = pd.read_csv("scratch/ui_dashboard_continuous_rhc.csv")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

df = load_data()

st.subheader("Interactive Annual Dispatch Telemetry")
st.markdown("Drag to zoom in on specific months. Notice how diesel (red) only fires to protect the 20% battery floor during prolonged Arctic winter darkness.")

# 4. Build the Interactive Plotly Hero Chart
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Blue Area: Battery SOC
fig.add_trace(
    go.Scatter(
        x=df['timestamp'], y=df['battery_soc_pct'],
        name="Battery State of Charge (%)",
        fill='tozeroy',
        line=dict(color='rgba(59, 130, 246, 0.8)', width=1),
        fillcolor='rgba(59, 130, 246, 0.2)'
    ),
    secondary_y=False,
)

# Red Bars: Diesel Generator Dispatch
fig.add_trace(
    go.Bar(
        x=df['timestamp'], y=df['diesel_kw'],
        name="Diesel Output (kW)",
        marker_color='rgba(239, 68, 68, 0.9)'
    ),
    secondary_y=True,
)

# Format the UI
fig.update_layout(
    height=500,
    margin=dict(l=0, r=0, t=10, b=0),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode="x unified"
)
fig.update_yaxes(title_text="Battery SOC (%)", range=[0, 100], secondary_y=False)
fig.update_yaxes(title_text="Diesel Power (kW)", range=[0, 100], secondary_y=True, showgrid=False)

st.plotly_chart(fig, use_container_width=True)
