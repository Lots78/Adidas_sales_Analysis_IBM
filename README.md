# 👟 Adidas US Sales Analysis

An end-to-end **data cleaning → analysis → interactive dashboard** project built with Python, Pandas, Plotly, and Streamlit.

---

## 📁 Project Structure

```
adidas_sales_analysis/
├── app.py                      # Streamlit dashboard (frontend)
├── analysis.py                 # Data cleaning & aggregation module
├── Adidas_US_Sales_Datasets.csv  # Dataset
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 🚀 Quick Start

### 1. Clone / open the project folder
```bash
cd adidas_sales_analysis
```

### 2. Create and activate a virtual environment (recommended)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the dashboard
```bash
streamlit run app.py
```

The app will open automatically at **http://localhost:8501**.

---

## 🧹 Data Cleaning Steps (`analysis.py`)

| # | Step | What it does |
|---|------|--------------|
| 1 | **Load raw file** | Skips the first 4 decorative/blank rows; drops the leading blank column |
| 2 | **Rename columns** | Maps raw headers → snake_case / clean names |
| 3 | **Drop blank rows** | Removes rows where every field is empty |
| 4 | **Fix data types** | Parses `Invoice_Date` as `datetime`; converts numeric columns with `pd.to_numeric` |
| 5 | **Round float noise** | Fixes values like `55.00000000000001` → `55.00` |
| 6 | **Remove duplicates** | Drops exact duplicate rows |
| 7 | **Drop critical nulls** | Removes rows missing Retailer, Date, Price, Units, or Product |
| 8 | **Recalculate Sales** | `Total_Sales = Units_Sold × Price_per_Unit` (corrects source rounding errors) |
| 9 | **Derive time columns** | Adds `Year`, `Month`, `Month_Name`, `Year_Month` |

---

## 📊 Analysis Performed

| Analysis | Description |
|----------|-------------|
| **Summary KPIs** | Total revenue, units sold, profit, avg order value, avg margin |
| **By Retailer** | Revenue, units, transaction count, avg margin per retailer |
| **By Product** | Revenue, units, avg price, avg margin per product category |
| **By Region** | Revenue, units, avg margin per US region |
| **By Sales Method** | In-store vs Online vs Outlet breakdown |
| **Monthly Trend** | Revenue and profit by month/year |
| **Geographic** | Top 10 states + US choropleth heatmap |
| **Data Quality** | Null counts, dtypes, before/after row counts, descriptive stats |

---

## 🖥️ Dashboard Tabs

| Tab | Content |
|-----|---------|
| 📊 **Overview** | 8 KPI cards, revenue by sales method (donut), revenue by region (bar) |
| 🏪 **Retailers** | Revenue, units, and margin bar charts + summary table |
| 👟 **Products** | Revenue & profit horizontal bars, price × units bubble chart |
| 🗺️ **Geography** | Region pie, top-10 states bar, interactive US choropleth map |
| 📈 **Trends** | Monthly line chart by year, grouped profit bars, channel trend line |
| 🧹 **Data Quality** | Cleaning report, null counts, dtypes, descriptive statistics, data preview |

---

## 🔧 Key Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| `streamlit` | ≥ 1.32 | Web dashboard framework |
| `pandas` | ≥ 2.1 | Data loading, cleaning, aggregation |
| `numpy` | ≥ 1.26 | Numeric operations |
| `plotly` | ≥ 5.20 | Interactive charts & maps |

---

## 💡 Business Insights (sample findings)

- **Men's Street Footwear** consistently generates the highest revenue.
- **In-store** sales dominate overall, but **Online** is the fastest-growing channel.
- The **Northeast** and **West** regions contribute the most revenue.
- **Operating margins** are highest for footwear categories (~35–50%) vs apparel (~25–30%).
- Sales peak in **Q1 and Q3** each year.

---

## 📌 Notes

- The raw CSV has 4 header rows and a leading blank column — the cleaning script handles this automatically.
- `Total_Sales` is **recalculated** from `Units_Sold × Price_per_Unit` to correct floating-point rounding errors present in the source data.
- All sidebar filters (Year, Region, Retailer, Sales Method) apply globally across every chart on every tab.
