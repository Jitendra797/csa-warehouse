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

st.title("Sales Analytics Dashboard")

# Sample data
dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')

sample_sales = pd.DataFrame({
    'date': dates[:100],
    'sales': np.random.randint(1000, 5000, 100),
    'region': np.random.choice(['North', 'South', 'East', 'West'], 100),
    'product': np.random.choice(['Product A', 'Product B', 'Product C'], 100)
})

# Metrics
total_sales = sample_sales['sales'].sum()
avg_daily_sales = sample_sales['sales'].mean()
unique_regions = sample_sales['region'].nunique()
top_product = sample_sales.groupby('product')['sales'].sum().idxmax()

# Display metrics
st.markdown("""<h3 class="sub">Key Performance Indicators</h3>""",
            unsafe_allow_html=True)
cols = st.columns(4)

with cols[0]:
    ui.metric_card("Total Sales", f"${total_sales:,.0f}")

with cols[1]:
    ui.metric_card("Average Daily Sales", f"${avg_daily_sales:,.0f}")

with cols[2]:
    ui.metric_card("Regions", unique_regions)

with cols[3]:
    ui.metric_card("Top Product", top_product)

st.divider()

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Sales Over Time")
    fig = px.line(sample_sales, x='date', y='sales', title='Daily Sales Trend')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Sales by Region")
    region_sales = sample_sales.groupby('region')['sales'].sum().reset_index()
    fig = px.bar(region_sales, x='region', y='sales', title='Sales by Region')
    st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Product Performance")
product_sales = sample_sales.groupby('product')['sales'].sum().reset_index()
fig = px.pie(product_sales, names='product', values='sales',
             title='Sales Distribution by Product')
st.plotly_chart(fig, use_container_width=True)

st.divider()

# Data table
with st.expander("📊 View Raw Sales Data"):
    st.dataframe(sample_sales)
