import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(
    page_title="Retail Business Dashboard",
    page_icon="📊",
    layout="wide"
)


st.title("📊 Retail Business Dashboard")

st.markdown(
    """
    ### Interactive Sales & Business Performance Dashboard

    This dashboard provides an interactive analysis of retail sales,
    customer segments, product categories, geographic performance,
    and sales trends.
    """
)

# Load dataset with caching to improve performance
@st.cache_data
def load_data():
    data = pd.read_csv("data/clean_dataset.csv")
    return data


df = load_data()

# Display dataset information
st.write("Dataset loaded successfully.")

st.write(
    f"Dataset contains **{df.shape[0]:,} rows** "
    f"and **{df.shape[1]} columns**."
)

# Display the first few rows of the dataset
# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("🔎 Dashboard Filters")

# Filter by Category
selected_categories = st.sidebar.multiselect(
    "Select Category",
    options=sorted(df["category"].dropna().unique()),
    default=sorted(df["category"].dropna().unique())
)

# Filter by Customer Segment
selected_segments = st.sidebar.multiselect(
    "Select Customer Segment",
    options=sorted(df["customer_segment"].dropna().unique()),
    default=sorted(df["customer_segment"].dropna().unique())
)


# Filter by Payment Status
selected_payment_status = st.sidebar.multiselect(
    "Select Payment Status",
    options=sorted(df["payment_status"].dropna().unique()),
    default=sorted(df["payment_status"].dropna().unique())
)

# Filter by City
selected_cities = st.sidebar.multiselect(
    "Select City",
    options=sorted(df["city"].dropna().unique()),
    default=sorted(df["city"].dropna().unique())
)


# Filter by Year
selected_years = st.sidebar.multiselect(
    "Select Year",
    options=sorted(df["year"].dropna().unique()),
    default=sorted(df["year"].dropna().unique())
)

# Apply filters to the dataset
filtered_df = df[
    df["category"].isin(selected_categories)
    & df["customer_segment"].isin(selected_segments)
    & df["payment_status"].isin(selected_payment_status)
    & df["city"].isin(selected_cities)
    & df["year"].isin(selected_years)
].copy()

# Display the number of records after filtering
st.info(
    f"Showing {len(filtered_df):,} records "
    f"out of {len(df):,} total records."
)

# Calculate total revenue from the filtered dataset
revenue = filtered_df["net_sales"].sum()

st.subheader("📌 Executive KPIs")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="💰 Total Revenue",
        value=f"₹{revenue:,.2f}"
    )

# Calculate total orders from the filtered dataset
total_orders = filtered_df["order_id"].nunique()

# Display total orders in the second column
with col2:
    st.metric(
        label="🧾 Total Orders",
        value=f"{total_orders:,}"
    )

# Calculate Average Order Value (AOV)
if total_orders > 0:
    aov = revenue / total_orders
else:
    aov = 0

# Display Average Order Value in the third column
with col3:
    st.metric(
        label="🛒 Average Order Value",
        value=f"₹{aov:,.2f}"
    )

# Calculate total quantity sold from the filtered dataset
total_quantity = filtered_df["quantity"].sum()

# Display total quantity sold in the fourth column
with col4:
    st.metric(
        label="📦 Total Quantity",
        value=f"{total_quantity:,.0f}"
    )


# Add a note about CAC and Churn
    st.caption(
    "CAC and Churn Rate are not directly calculated because the supplied "
    "dataset does not contain customer acquisition cost or customer "
    "activity/churn information."
)
    
# create revenue trend
    st.subheader("📈 Revenue Trend")


    monthly_revenue = (
    filtered_df
    .groupby(["year", "month", "month_name"], as_index=False)["net_sales"]
    .sum()
)
    
    monthly_revenue["period"] = pd.to_datetime(
    monthly_revenue["year"].astype(str)
    + "-"
    + monthly_revenue["month"].astype(str)
    + "-01"
)
    
    monthly_revenue = monthly_revenue.sort_values("period")

# Create an area chart for monthly revenue trend
    fig_revenue = px.area(
    monthly_revenue,
    x="period",
    y="net_sales",
    title="Monthly Revenue Trend",
    labels={
        "period": "Month",
        "net_sales": "Revenue"
    }
)
    # Update layout for better visualization
    fig_revenue.update_layout(
    xaxis_title="Month",
    yaxis_title="Revenue",
    hovermode="x unified"
)
   # Display the revenue trend chart 
    st.plotly_chart(
    fig_revenue,
    use_container_width=True
)
   # Display revenue by category 
st.subheader("📊 Revenue by Category")

category_revenue = (
    filtered_df
    .groupby("category", as_index=False)["net_sales"]
    .sum()
    .sort_values("net_sales", ascending=False)
)

# Create a bar chart for revenue by product category
fig_category = px.bar(
    category_revenue,
    x="category",
    y="net_sales",
    title="Revenue by Product Category",
    labels={
        "category": "Category",
        "net_sales": "Revenue"
    }
)

# Update layout for better visualization
st.plotly_chart(
    fig_category,
    use_container_width=True
)

# Display revenue by customer segment
st.subheader("👥 Revenue by Customer Segment")

segment_revenue = (
    filtered_df
    .groupby("customer_segment", as_index=False)["net_sales"]
    .sum()
    .sort_values("net_sales", ascending=False)
)

fig_segment = px.bar(
    segment_revenue,
    x="customer_segment",
    y="net_sales",
    title="Revenue by Customer Segment",
    labels={
        "customer_segment": "Customer Segment",
        "net_sales": "Revenue"
    }
)


st.plotly_chart(
    fig_segment,
    use_container_width=True
)


# Display revenue by geographic location
st.subheader("🌍 Geographic Revenue Analysis")

city_revenue = (
    filtered_df
    .groupby("city", as_index=False)["net_sales"]
    .sum()
    .sort_values("net_sales", ascending=False)
)

fig_city = px.bar(
    city_revenue.head(15),
    x="net_sales",
    y="city",
    orientation="h",
    title="Top 15 Cities by Revenue",
    labels={
        "net_sales": "Revenue",
        "city": "City"
    }
)

st.plotly_chart(
    fig_city,
    use_container_width=True
)


# Display revenue distribution across cities using a treemap
fig_geo = px.treemap(
    city_revenue,
    path=["city"],
    values="net_sales",
    title="Revenue Distribution Across Cities"
)
# Update layout for better visualization
st.plotly_chart(
    fig_geo,
    use_container_width=True
)


st.subheader("🔍 Category → Customer Segment Drill-Down")

drill_category = st.selectbox(
    "Select a Category for Drill-Down",
    options=sorted(filtered_df["category"].dropna().unique())
)


# Filter the dataset based on the selected category
drill_df = filtered_df[
    filtered_df["category"] == drill_category
]
# Calculate revenue by customer segment for the selected category
drill_segment = (
    drill_df
    .groupby("customer_segment", as_index=False)["net_sales"]
    .sum()
    .sort_values("net_sales", ascending=False)
)

# Create a bar chart for customer segment revenue within the selected category

fig_drill = px.bar(
    drill_segment,
    x="customer_segment",
    y="net_sales",
    title=f"Customer Segment Revenue — {drill_category}",
    labels={
        "customer_segment": "Customer Segment",
        "net_sales": "Revenue"
    }
)

# Update layout for better visualization

st.plotly_chart(
    fig_drill,
    use_container_width=True
)


st.subheader("📅 Temporal Drill-Down")

# Select Year for temporal drill-down

drill_year = st.selectbox(
    "Select Year",
    options=sorted(filtered_df["year"].dropna().unique())
)

# Filter the dataset based on the selected year

year_df = filtered_df[
    filtered_df["year"] == drill_year
]

# Calculate monthly revenue for the selected year

year_monthly = (
    year_df
    .groupby(["month", "month_name"], as_index=False)["net_sales"]
    .sum()
    .sort_values("month")
)

# Create a bar chart for monthly revenue within the selected year

fig_year_month = px.bar(
    year_monthly,
    x="month_name",
    y="net_sales",
    title=f"Monthly Revenue — {drill_year}",
    labels={
        "month_name": "Month",
        "net_sales": "Revenue"
    }
)

# Update layout for better visualization
st.plotly_chart(
    fig_year_month,
    use_container_width=True
)


# Display filtered transaction data
st.subheader("📋 Filtered Transaction Data")

with st.expander("View filtered records"):
    st.dataframe(
        filtered_df,
        use_container_width=True
    )



csv_data = filtered_df.to_csv(index=False).encode("utf-8") 

st.download_button(
    label="⬇️ Download Filtered Data",
    data=csv_data,
    file_name="filtered_retail_data.csv",
    mime="text/csv"
)

st.markdown("---")

st.caption(
    "Retail Business Dashboard | Built using Python, Streamlit and Plotly"
)


