import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration (Wide layout for a professional look)
st.set_page_config(page_title="Sales Operations Dashboard", layout="wide")

st.title("📊 Sales Operations & Revenue Trend Dashboard")
st.markdown("### Strategic Business Analytics & Performance Portfolio")

# 2. Data Loading
@st.cache_data
def load_data():
    df = pd.read_csv("SuperMarket Analysis-selected-columns.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    return df

try:
    df = load_data()

    # 3. Sidebar Filter Mechanics
    st.sidebar.header("Filter Settings")
    
    # Product line selection
    all_product_lines = ["All Categories"] + sorted(df["Product line"].unique().tolist())
    selected_product_line = st.sidebar.selectbox("Product Line", all_product_lines)
    
    # Branch selection
    all_branches = ["All Branches"] + sorted(df["Branch"].unique().tolist())
    selected_branch = st.sidebar.selectbox("Branch", all_branches)

    # Apply Filters
    filtered_df = df.copy()
    if selected_product_line != "All Categories":
        filtered_df = filtered_df[filtered_df["Product line"] == selected_product_line]
    if selected_branch != "All Branches":
        filtered_df = filtered_df[filtered_df["Branch"] == selected_branch]

    # 4. Executive KPI Metrics
    total_sales = filtered_df["Sales"].sum()
    total_quantity = filtered_df["Quantity"].sum()
    avg_unit_price = filtered_df["Unit price"].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Gross Revenue", f"${total_sales:,.2f}")
    col2.metric("Total Units Sold", f"{total_quantity:,}")
    col3.metric("Average Unit Price", f"${avg_unit_price:,.2f}")

    st.markdown("---")

    # 5. Trend Analysis (Time-series chart using Plotly)
    st.subheader("🗓️ Daily Revenue Performance (Trend)")
    if not filtered_df.empty:
        # Aggregate revenue by Date
        trend_df = filtered_df.groupby("Date")["Sales"].sum().reset_index()
        # Create line chart with clean business labels
        fig_trend = px.line(trend_df, x="Date", y="Sales", labels={"Sales": "Revenue ($)", "Date": "Date"})
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("No data available for the selected filters. Please adjust your criteria.")

    # 6. Segment Analysis (Product Line & Regional Distribution)
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("🛍️ Revenue by Product Line")
        prod_sales = filtered_df.groupby("Product line")["Sales"].sum().reset_index()
        # Sort for clearer hierarchical insights
        prod_sales = prod_sales.sort_values("Sales", ascending=True)
        fig_prod = px.bar(prod_sales, x="Sales", y="Product line", orientation='h', color="Product line",
                          labels={"Sales": "Revenue ($)", "Product line": "Product Line"})
        st.plotly_chart(fig_prod, use_container_width=True)
        
    with col_right:
        st.subheader("🌆 Revenue Share by City")
        city_sales = filtered_df.groupby("City")["Sales"].sum().reset_index()
        fig_city = px.pie(city_sales, values="Sales", names="City", hole=0.4)
        st.plotly_chart(fig_city, use_container_width=True)

    # 7. Data Transparency (Raw Data Preview)
    with st.expander("📄 View Filtered Source Data (Top 100 Rows)"):
        st.dataframe(filtered_df.head(100))

except Exception as e:
    st.warning("Failed to load the dataset. Please verify the CSV file path and column names.")
    st.error(f"Error details: {e}")