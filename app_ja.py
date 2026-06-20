import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ページの設定（リクルーターが見た時にプロっぽく見えるようにワイド画面に）
st.set_page_config(page_title="Sales Operations Dashboard", layout="wide")

st.title("📊 営業・売上トレンド分析ダッシュボード")
st.markdown("### Sales Operations & Business Analytics Portfolio")

# 2. データの読み込み
@st.cache_data
def load_data():
    # お手元のファイル名を指定
    df = pd.read_csv("SuperMarket Analysis-selected-columns.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    return df

try:
    df = load_data()

    # 3. サイドバーのフィルター機能
    st.sidebar.header("フィルター設定")
    
    # Product line（製品カテゴリ）の選択
    all_product_lines = ["すべて"] + sorted(df["Product line"].unique().tolist())
    selected_product_line = st.sidebar.selectbox("製品カテゴリ (Product line)", all_product_lines)
    
    # Branch（店舗・支店）の選択
    all_branches = ["すべて"] + sorted(df["Branch"].unique().tolist())
    selected_branch = st.sidebar.selectbox("店舗・支店 (Branch)", all_branches)

    # フィルターの適用
    filtered_df = df.copy()
    if selected_product_line != "すべて":
        filtered_df = filtered_df[filtered_df["Product line"] == selected_product_line]
    if selected_branch != "すべて":
        filtered_df = filtered_df[filtered_df["Branch"] == selected_branch]

    # 4. KPI（主要指標）の表示
    total_sales = filtered_df["Sales"].sum()
    total_quantity = filtered_df["Quantity"].sum()
    avg_unit_price = filtered_df["Unit price"].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("総売上 (Total Sales)", f"${total_sales:,.2f}")
    col2.metric("総販売数量 (Total Quantity)", f"{total_quantity:,}")
    col3.metric("平均単価 (Avg Unit Price)", f"${avg_unit_price:,.2f}")

    st.markdown("---")

    # 5. グラフの描画（重複とバグを削り、Plotlyの綺麗な時系列グラフに統一）
    st.subheader("🗓️ 日別売上推移（トレンド）")
    if not filtered_df.empty:
        # 日付ごとに売上を集計
        trend_df = filtered_df.groupby("Date")["Sales"].sum().reset_index()
        # Plotlyで線グラフを作成（見た目を少しスタイリッシュに）
        fig_trend = px.line(trend_df, x="Date", y="Sales", labels={"Sales": "売上高 ($)", "Date": "日付"})
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("該当するデータがありません。フィルター条件を変更してください。")

    # 6. カテゴリ別・都市別の分析（横並びで配置して見栄えを良くする）
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("🛍️ カテゴリ別売上（Product line）")
        prod_sales = filtered_df.groupby("Product line")["Sales"].sum().reset_index()
        # 売上が高い順に見やすくなるようソートを追加
        prod_sales = prod_sales.sort_values("Sales", ascending=True)
        fig_prod = px.bar(prod_sales, x="Sales", y="Product line", orientation='h', color="Product line")
        st.plotly_chart(fig_prod, use_container_width=True)
        
    with col_right:
        st.subheader("🌆 都市別売上（City）")
        city_sales = filtered_df.groupby("City")["Sales"].sum().reset_index()
        fig_city = px.pie(city_sales, values="Sales", names="City", hole=0.4)
        st.plotly_chart(fig_city, use_container_width=True)

    # 7. 実務感を出すためのデータチラ見せ機能（追加）
    with st.expander("📄 フィルター後の生データを確認（上位100件）"):
        st.dataframe(filtered_df.head(100))

except Exception as e:
    st.warning("CSVファイルを読み込むか、コード内のファイル名を修正してください。")
    st.error(f"エラー内容: {e}")