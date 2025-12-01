import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit_shadcn_ui as ui
from utilities import initialize_page

# Page setup
initialize_page()

st.title("Revenue Tracking Dashboard")

# Sample revenue data

months = pd.date_range(start='2024-01-01', end='2024-12-01', freq='MS')
channels = ['Online', 'Retail', 'Wholesale', 'Direct Sales']

revenue_data = []
for month in months:
    for channel in channels:
        revenue_data.append({
            'month': month,
            'channel': channel,
            'revenue': np.random.uniform(50000, 200000, 1)[0],
            'orders': np.random.randint(100, 500, 1)[0],
        })

df_revenue = pd.DataFrame(revenue_data)
df_revenue['avg_order_value'] = df_revenue['revenue'] / df_revenue['orders']

# Calculate metrics
total_revenue = df_revenue['revenue'].sum()
avg_monthly_revenue = df_revenue.groupby('month')['revenue'].sum().mean()
total_orders = df_revenue['orders'].sum()
top_channel = df_revenue.groupby('channel')['revenue'].sum().idxmax()

st.markdown("""<h3 class="sub">Revenue Metrics</h3>""", unsafe_allow_html=True)
cols = st.columns(4)

with cols[0]:
    ui.metric_card("Total Revenue", f"${total_revenue:,.0f}")

with cols[1]:
    ui.metric_card("Avg Monthly Revenue", f"${avg_monthly_revenue:,.0f}")

with cols[2]:
    ui.metric_card("Total Orders", f"{total_orders:,}")

with cols[3]:
    ui.metric_card("Top Channel", top_channel)

st.divider()

# Monthly revenue trend
st.subheader("Monthly Revenue Trend")
monthly_revenue = df_revenue.groupby('month')['revenue'].sum().reset_index()
fig = px.line(
    monthly_revenue,
    x='month',
    y='revenue',
    title='Revenue Over Time',
    markers=True
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# Revenue by channel
col1, col2 = st.columns(2)

with col1:
    st.subheader("Revenue by Channel")
    channel_revenue = df_revenue.groupby(
        'channel')['revenue'].sum().reset_index()
    fig = px.bar(channel_revenue, x='channel', y='revenue',
                 title='Total Revenue by Channel')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Channel Distribution")
    fig = px.pie(channel_revenue, names='channel',
                 values='revenue', title='Revenue Share by Channel')
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Average order value by channel
st.subheader("Average Order Value by Channel")
channel_aov = df_revenue.groupby(
    'channel')['avg_order_value'].mean().reset_index()
fig = px.bar(channel_aov, x='channel', y='avg_order_value',
             title='Average Order Value')
st.plotly_chart(fig, use_container_width=True)

st.divider()

# Data table
with st.expander("💰 View Revenue Data"):
    st.dataframe(df_revenue)
