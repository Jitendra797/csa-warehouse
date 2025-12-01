import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import streamlit_shadcn_ui as ui
from utilities import initialize_page

# Page setup
initialize_page()

st.title("General Analytics Dashboard")

# Sample analytics data

# User activity data
days = pd.date_range(start='2024-01-01', periods=30, freq='D')
user_activity = pd.DataFrame({
    'date': days,
    'active_users': np.random.randint(100, 1000, 30),
    'page_views': np.random.randint(1000, 10000, 30),
    'sessions': np.random.randint(500, 5000, 30),
    'bounce_rate': np.random.uniform(20, 60, 30),
})

# Device breakdown
devices = pd.DataFrame({
    'device': ['Desktop', 'Mobile', 'Tablet'],
    'users': [4500, 6200, 1300],
    'percentage': [37.5, 51.7, 10.8]
})

# Country distribution
countries = ['USA', 'UK', 'India', 'Canada',
             'Australia', 'Germany', 'France', 'Japan']
country_data = pd.DataFrame({
    'country': countries,
    'users': np.random.randint(500, 3000, len(countries)),
})

# Calculate metrics
total_users = user_activity['active_users'].sum()
avg_daily_users = user_activity['active_users'].mean()
total_page_views = user_activity['page_views'].sum()
avg_bounce_rate = user_activity['bounce_rate'].mean()

st.markdown("""<h3 class="sub">User Analytics</h3>""", unsafe_allow_html=True)
cols = st.columns(4)

with cols[0]:
    ui.metric_card("Total Users (30 days)", f"{total_users:,}")

with cols[1]:
    ui.metric_card("Avg Daily Users", f"{avg_daily_users:.0f}")

with cols[2]:
    ui.metric_card("Total Page Views", f"{total_page_views:,}")

with cols[3]:
    ui.metric_card("Avg Bounce Rate", f"{avg_bounce_rate:.1f}%")

st.divider()

# Activity trends
st.subheader("User Activity Trends")
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=user_activity['date'],
    y=user_activity['active_users'],
    mode='lines+markers',
    name='Active Users',
    line=dict(color='blue')
))

fig.add_trace(go.Scatter(
    x=user_activity['date'],
    y=user_activity['sessions'],
    mode='lines+markers',
    name='Sessions',
    line=dict(color='green')
))

fig.update_layout(
    title='Daily Activity Trends',
    xaxis_title='Date',
    yaxis_title='Count',
    hovermode='x unified'
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Users by Device")
    fig = px.pie(devices, names='device', values='users',
                 title='Device Distribution')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Top Countries")
    country_data_sorted = country_data.sort_values('users', ascending=True)
    fig = px.bar(
        country_data_sorted,
        x='users',
        y='country',
        orientation='h',
        title='Users by Country'
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Page Views vs Bounce Rate")
fig = px.scatter(
    user_activity,
    x='page_views',
    y='bounce_rate',
    size='active_users',
    hover_data=['date'],
    title='Page Views vs Bounce Rate (Size = Active Users)'
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# Data tables
col1, col2 = st.columns(2)

with col1:
    with st.expander("📈 View Activity Data"):
        st.dataframe(user_activity)

with col2:
    with st.expander("🌍 View Country Data"):
        st.dataframe(country_data)
