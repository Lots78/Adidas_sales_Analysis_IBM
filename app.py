"""
app.py
------
Adidas US Sales Analysis – Streamlit Dashboard
Run with:  streamlit run app.py
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from analysis import (
    load_and_clean,
    summary_stats,
    sales_by_retailer,
    sales_by_product,
    sales_by_region,
    sales_by_method,
    monthly_trend,
    top_states,
    profit_by_product,
)

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Adidas US Sales Analysis",
    page_icon="👟",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .main { background-color: #f5f7fa; }

    /* KPI card */
    .kpi-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 20px 16px;
        text-align: center;
        border: 1px solid #e0e4ea;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #1a1a2e;
        margin: 0;
    }
    .kpi-label {
        font-size: 13px;
        color: #6b7280;
        margin: 4px 0 0;
        font-weight: 500;
    }
    .kpi-icon { font-size: 28px; margin-bottom: 6px; }

    /* Section headings */
    .section-heading {
        font-size: 20px;
        font-weight: 700;
        color: #1a1a2e;
        margin: 24px 0 12px;
        border-left: 4px solid #2563eb;
        padding-left: 10px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMultiSelect label { color: #94a3b8 !important; }

    /* DataFrame tables */
    .dataframe { font-size: 13px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
DATA_FILE = os.path.join(os.path.dirname(__file__), "Adidas_US_Sales_Datasets.csv")

@st.cache_data(show_spinner="🔄  Cleaning & loading data…")
def get_data(path: str) -> pd.DataFrame:
    return load_and_clean(path)

df_full = get_data(DATA_FILE)

# ─────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 👟 Adidas Sales")
    st.markdown("### Filters")

    years = sorted(df_full["Year"].dropna().unique().tolist())
    sel_years = st.multiselect("Year", years, default=years)

    regions = sorted(df_full["Region"].dropna().unique().tolist())
    sel_regions = st.multiselect("Region", regions, default=regions)

    retailers = sorted(df_full["Retailer"].dropna().unique().tolist())
    sel_retailers = st.multiselect("Retailer", retailers, default=retailers)

    methods = sorted(df_full["Sales_Method"].dropna().unique().tolist())
    sel_methods = st.multiselect("Sales Method", methods, default=methods)

    st.markdown("---")
    st.markdown("**Dataset Info**")
    st.caption(f"📅 {df_full['Invoice_Date'].min().date()} → {df_full['Invoice_Date'].max().date()}")
    st.caption(f"📦 {len(df_full):,} transactions (after cleaning)")

# Apply filters
df = df_full.copy()
if sel_years:
    df = df[df["Year"].isin(sel_years)]
if sel_regions:
    df = df[df["Region"].isin(sel_regions)]
if sel_retailers:
    df = df[df["Retailer"].isin(sel_retailers)]
if sel_methods:
    df = df[df["Sales_Method"].isin(sel_methods)]

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div style='background:linear-gradient(90deg,#1a1a2e,#2563eb);
            padding:28px 32px; border-radius:14px; margin-bottom:24px;'>
  <h1 style='color:#ffffff; margin:0; font-size:32px;'>👟 Adidas US Sales Analysis</h1>
  <p style='color:#93c5fd; margin:6px 0 0; font-size:15px;'>
      Interactive dashboard · Data-driven insights
  </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Overview",
    "🏪 Retailers",
    "👟 Products",
    "🗺️ Geography",
    "📈 Trends",
    "🧹 Data Quality",
])

# ═══════════════════════════════════════════════
# TAB 1 – OVERVIEW
# ═══════════════════════════════════════════════
with tab1:
    stats = summary_stats(df)

    # KPI Row
    col1, col2, col3, col4 = st.columns(4)
    kpis = [
        (col1, "💰", f"${stats['total_revenue']:,.0f}", "Total Revenue"),
        (col2, "📦", f"{stats['total_units']:,}", "Units Sold"),
        (col3, "📈", f"${stats['total_profit']:,.0f}", "Operating Profit"),
        (col4, "🧾", f"{stats['num_transactions']:,}", "Transactions"),
    ]
    for col, icon, val, label in kpis:
        with col:
            st.markdown(f"""
            <div class='kpi-card'>
              <div class='kpi-icon'>{icon}</div>
              <p class='kpi-value'>{val}</p>
              <p class='kpi-label'>{label}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col5, col6, col7, col8 = st.columns(4)
    kpis2 = [
        (col5, "🛒", f"${stats['avg_order_value']:,.0f}", "Avg Order Value"),
        (col6, "📉", f"{stats['avg_margin']}%", "Avg Operating Margin"),
        (col7, "🏪", str(stats['num_retailers']), "Retailers"),
        (col8, "👟", str(stats['num_products']), "Product Categories"),
    ]
    for col, icon, val, label in kpis2:
        with col:
            st.markdown(f"""
            <div class='kpi-card'>
              <div class='kpi-icon'>{icon}</div>
              <p class='kpi-value'>{val}</p>
              <p class='kpi-label'>{label}</p>
            </div>""", unsafe_allow_html=True)

    # Overview charts side-by-side
    st.markdown("<div class='section-heading'>Revenue Breakdown</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        sm = sales_by_method(df)
        fig = px.pie(
            sm, names="Sales_Method", values="Total_Sales",
            title="Revenue by Sales Method",
            color_discrete_sequence=px.colors.qualitative.Bold,
            hole=0.45,
        )
        fig.update_traces(textinfo="percent+label")
        fig.update_layout(showlegend=False, margin=dict(t=50, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        sr = sales_by_region(df)
        fig2 = px.bar(
            sr, x="Region", y="Total_Sales",
            title="Revenue by Region",
            color="Total_Sales",
            color_continuous_scale="Blues",
            text_auto=".2s",
        )
        fig2.update_layout(coloraxis_showscale=False, margin=dict(t=50, b=10))
        st.plotly_chart(fig2, use_container_width=True)

# ═══════════════════════════════════════════════
# TAB 2 – RETAILERS
# ═══════════════════════════════════════════════
with tab2:
    st.markdown("<div class='section-heading'>Retailer Performance</div>", unsafe_allow_html=True)
    ret_df = sales_by_retailer(df)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(
            ret_df, x="Retailer", y="Total_Sales",
            title="Total Revenue by Retailer",
            color="Total_Sales",
            color_continuous_scale="Viridis",
            text_auto=".2s",
        )
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig2 = px.bar(
            ret_df, x="Retailer", y="Units_Sold",
            title="Units Sold by Retailer",
            color="Units_Sold",
            color_continuous_scale="Teal",
            text_auto=".2s",
        )
        fig2.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Avg margin comparison
    fig3 = px.bar(
        ret_df.sort_values("Avg_Margin", ascending=False),
        x="Retailer", y="Avg_Margin",
        title="Average Operating Margin by Retailer",
        color="Avg_Margin",
        color_continuous_scale="RdYlGn",
        text_auto=".2f",
    )
    fig3.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("**Retailer Summary Table**")
    ret_df_display = ret_df.copy()
    ret_df_display["Total_Sales"]   = ret_df_display["Total_Sales"].map("${:,.0f}".format)
    ret_df_display["Units_Sold"]    = ret_df_display["Units_Sold"].map("{:,}".format)
    ret_df_display["Avg_Margin"]    = ret_df_display["Avg_Margin"].map("{:.2%}".format)
    st.dataframe(ret_df_display, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════
# TAB 3 – PRODUCTS
# ═══════════════════════════════════════════════
with tab3:
    st.markdown("<div class='section-heading'>Product Analysis</div>", unsafe_allow_html=True)
    prod_df  = sales_by_product(df)
    prof_df  = profit_by_product(df)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(
            prod_df, x="Total_Sales", y="Product",
            orientation="h",
            title="Revenue by Product Category",
            color="Total_Sales",
            color_continuous_scale="Blues",
            text_auto=".2s",
        )
        fig.update_layout(coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig2 = px.bar(
            prof_df, x="Total_Profit", y="Product",
            orientation="h",
            title="Operating Profit by Product",
            color="Total_Profit",
            color_continuous_scale="Greens",
            text_auto=".2s",
        )
        fig2.update_layout(coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig2, use_container_width=True)

    # Bubble chart: price vs units sold vs margin
    st.markdown("<div class='section-heading'>Price vs Units vs Margin</div>", unsafe_allow_html=True)
    fig3 = px.scatter(
        prod_df, x="Avg_Price", y="Units_Sold",
        size="Total_Sales", color="Product",
        title="Avg Price vs Units Sold (bubble = revenue)",
        hover_name="Product",
        size_max=60,
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("**Product Summary Table**")
    disp = prod_df.copy()
    disp["Total_Sales"] = disp["Total_Sales"].map("${:,.0f}".format)
    disp["Units_Sold"]  = disp["Units_Sold"].map("{:,}".format)
    disp["Avg_Price"]   = disp["Avg_Price"].map("${:.2f}".format)
    disp["Avg_Margin"]  = disp["Avg_Margin"].map("{:.2%}".format)
    st.dataframe(disp, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════
# TAB 4 – GEOGRAPHY
# ═══════════════════════════════════════════════
with tab4:
    st.markdown("<div class='section-heading'>Geographic Performance</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        reg_df = sales_by_region(df)
        fig = px.pie(
            reg_df, names="Region", values="Total_Sales",
            title="Revenue Share by Region",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            hole=0.4,
        )
        fig.update_traces(textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        state_df = top_states(df, 10)
        fig2 = px.bar(
            state_df, x="Total_Sales", y="State",
            orientation="h",
            title="Top 10 States by Revenue",
            color="Total_Sales",
            color_continuous_scale="Oranges",
            text_auto=".2s",
        )
        fig2.update_layout(coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig2, use_container_width=True)

    # US Choropleth map using state abbreviations
    st.markdown("<div class='section-heading'>US Revenue Heatmap</div>", unsafe_allow_html=True)
    state_full = df.groupby("State")["Total_Sales"].sum().reset_index()

    # Mapping full state names → 2-letter codes
    state_abbr = {
        "Alabama":"AL","Alaska":"AK","Arizona":"AZ","Arkansas":"AR","California":"CA",
        "Colorado":"CO","Connecticut":"CT","Delaware":"DE","Florida":"FL","Georgia":"GA",
        "Hawaii":"HI","Idaho":"ID","Illinois":"IL","Indiana":"IN","Iowa":"IA","Kansas":"KS",
        "Kentucky":"KY","Louisiana":"LA","Maine":"ME","Maryland":"MD","Massachusetts":"MA",
        "Michigan":"MI","Minnesota":"MN","Mississippi":"MS","Missouri":"MO","Montana":"MT",
        "Nebraska":"NE","Nevada":"NV","New Hampshire":"NH","New Jersey":"NJ","New Mexico":"NM",
        "New York":"NY","North Carolina":"NC","North Dakota":"ND","Ohio":"OH","Oklahoma":"OK",
        "Oregon":"OR","Pennsylvania":"PA","Rhode Island":"RI","South Carolina":"SC",
        "South Dakota":"SD","Tennessee":"TN","Texas":"TX","Utah":"UT","Vermont":"VT",
        "Virginia":"VA","Washington":"WA","West Virginia":"WV","Wisconsin":"WI","Wyoming":"WY",
    }
    state_full["Code"] = state_full["State"].map(state_abbr)
    state_full = state_full.dropna(subset=["Code"])

    fig_map = px.choropleth(
        state_full, locations="Code", locationmode="USA-states",
        color="Total_Sales", scope="usa",
        color_continuous_scale="Blues",
        hover_name="State",
        title="Total Revenue by US State",
        labels={"Total_Sales": "Revenue ($)"},
    )
    st.plotly_chart(fig_map, use_container_width=True)

# ═══════════════════════════════════════════════
# TAB 5 – TRENDS
# ═══════════════════════════════════════════════
with tab5:
    st.markdown("<div class='section-heading'>Monthly Sales Trend</div>", unsafe_allow_html=True)
    trend = monthly_trend(df)

    fig = go.Figure()
    for yr in sorted(trend["Year"].unique()):
        sub = trend[trend["Year"] == yr]
        fig.add_trace(go.Scatter(
            x=sub["Month_Name"], y=sub["Total_Sales"],
            mode="lines+markers",
            name=str(yr),
            line=dict(width=2),
        ))
    fig.update_layout(
        title="Monthly Revenue by Year",
        xaxis_title="Month", yaxis_title="Revenue ($)",
        legend_title="Year",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Profit trend
    fig2 = go.Figure()
    for yr in sorted(trend["Year"].unique()):
        sub = trend[trend["Year"] == yr]
        fig2.add_trace(go.Bar(
            x=sub["Month_Name"], y=sub["Operating_Profit"],
            name=str(yr),
        ))
    fig2.update_layout(
        title="Monthly Operating Profit by Year",
        barmode="group",
        xaxis_title="Month", yaxis_title="Profit ($)",
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Sales Method trend
    st.markdown("<div class='section-heading'>Revenue by Sales Method Over Time</div>", unsafe_allow_html=True)
    method_trend = (
        df.groupby(["Year_Month", "Sales_Method"])["Total_Sales"]
          .sum().reset_index()
          .sort_values("Year_Month")
    )
    fig3 = px.line(
        method_trend, x="Year_Month", y="Total_Sales",
        color="Sales_Method",
        title="Revenue Trend by Sales Channel",
        markers=True,
    )
    fig3.update_xaxes(tickangle=45)
    st.plotly_chart(fig3, use_container_width=True)

# ═══════════════════════════════════════════════
# TAB 6 – DATA QUALITY
# ═══════════════════════════════════════════════
with tab6:
    st.markdown("<div class='section-heading'>Data Cleaning Report</div>", unsafe_allow_html=True)

    raw_path = DATA_FILE
    raw_check = pd.read_csv(raw_path, header=None, skiprows=4, dtype=str)
    raw_check = raw_check.drop(columns=[0])
    raw_check.columns = raw_check.iloc[0].str.strip()
    raw_check = raw_check.iloc[1:].reset_index(drop=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Raw Rows (before cleaning)", f"{len(raw_check):,}")
    col2.metric("Clean Rows (after cleaning)", f"{len(df_full):,}")
    col3.metric("Rows Removed", f"{len(raw_check) - len(df_full):,}")

    st.markdown("**Missing Values per Column (cleaned dataset)**")
    nulls = (
        df_full.isnull().sum()
        .rename_axis("Column")
        .reset_index(name="Missing Values")
    )
    nulls["% Missing"] = (nulls["Missing Values"] / len(df_full) * 100).round(2)
    st.dataframe(nulls, use_container_width=True, hide_index=True)

    st.markdown("**Data Types**")
    dtypes = (
        df_full.dtypes
        .rename_axis("Column")
        .reset_index(name="Data Type")
    )
    dtypes["Data Type"] = dtypes["Data Type"].astype(str)
    st.dataframe(dtypes, use_container_width=True, hide_index=True)

    st.markdown("**Descriptive Statistics (numeric columns)**")
    st.dataframe(
        df_full[["Price_per_Unit", "Units_Sold", "Total_Sales",
                 "Operating_Profit", "Operating_Margin"]].describe().round(2),
        use_container_width=True,
    )

    st.markdown("**Sample of Cleaned Data (first 50 rows)**")
    st.dataframe(
        df_full.head(50)[[
            "Retailer","Invoice_Date","Region","State","City",
            "Product","Price_per_Unit","Units_Sold","Total_Sales",
            "Operating_Profit","Operating_Margin","Sales_Method"
        ]],
        use_container_width=True, hide_index=True
    )

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#9ca3af; font-size:13px;'>"
    "Adidas US Sales Analysis Dashboard · Built with Streamlit & Plotly"
    "</p>",
    unsafe_allow_html=True,
)
