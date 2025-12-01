import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import streamlit_shadcn_ui as ui
from utilities import initialize_page

# Page setup
initialize_page()

st.title("Inventory Management Dashboard")

# Sample inventory data

categories = ['Electronics', 'Furniture', 'Clothing', 'Food', 'Books']
products = ['Item A', 'Item B', 'Item C', 'Item D',
            'Item E', 'Item F', 'Item G', 'Item H']

sample_inventory = pd.DataFrame({
    'product_id': [f'PROD-{i:03d}' for i in range(1, 51)],
    'product_name': np.random.choice(products, 50),
    'category': np.random.choice(categories, 50),
    'quantity': np.random.randint(0, 500, 50),
    'unit_price': np.random.uniform(10, 500, 50).round(2),
    'reorder_level': np.random.randint(20, 100, 50),
})

sample_inventory['total_value'] = sample_inventory['quantity'] * \
    sample_inventory['unit_price']
sample_inventory['status'] = sample_inventory.apply(
    lambda row: 'Low Stock' if row['quantity'] < row['reorder_level'] else 'In Stock',
    axis=1
)

# Metrics
total_items = len(sample_inventory)
total_value = sample_inventory['total_value'].sum()
low_stock_items = len(
    sample_inventory[sample_inventory['status'] == 'Low Stock'])
avg_quantity = sample_inventory['quantity'].mean()

st.markdown("""<h3 class="sub">Inventory Overview</h3>""",
            unsafe_allow_html=True)
cols = st.columns(4)

with cols[0]:
    ui.metric_card("Total Items", total_items)

with cols[1]:
    ui.metric_card("Total Value", f"${total_value:,.2f}")

with cols[2]:
    ui.metric_card("Low Stock Items", low_stock_items)

with cols[3]:
    ui.metric_card("Avg Quantity", f"{avg_quantity:.0f}")

st.divider()

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Inventory by Category")
    category_counts = sample_inventory.groupby(
        'category')['quantity'].sum().reset_index()
    fig = px.bar(category_counts, x='category', y='quantity',
                 title='Inventory Quantity by Category')
    fig.update_xaxis(tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Stock Status Distribution")
    status_counts = sample_inventory['status'].value_counts().reset_index()
    status_counts.columns = ['status', 'count']
    fig = px.pie(status_counts, names='status',
                 values='count', title='Items by Stock Status')
    st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Low Stock Alert")
low_stock = sample_inventory[sample_inventory['status']
                             == 'Low Stock'].sort_values('quantity')
if not low_stock.empty:
    st.dataframe(
        low_stock[['product_name', 'category', 'quantity', 'reorder_level']],
        use_container_width=True
    )
else:
    st.info("No items are currently low in stock.")

st.divider()

# Data table
with st.expander("📦 View Full Inventory Data"):
    st.dataframe(sample_inventory)
