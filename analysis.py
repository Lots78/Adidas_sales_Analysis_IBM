"""
analysis.py
-----------
Adidas US Sales – Data Cleaning & Analysis Module
All heavy pandas/numpy work lives here so app.py stays thin.
"""

import pandas as pd
import numpy as np
import os

# ─────────────────────────────────────────────
# 1. LOAD & CLEAN
# ─────────────────────────────────────────────

def load_and_clean(filepath: str) -> pd.DataFrame:
    """
    Loads the raw Adidas CSV (which has 4 junk header rows),
    cleans column names, fixes dtypes, removes duplicates/nulls,
    recalculates Total Sales = Units Sold × Price per Unit,
    and returns a tidy DataFrame.
    """
    # --- Step 1: Read raw file, skip the first 4 decorative rows ---
    raw = pd.read_csv(filepath, header=None, skiprows=4, dtype=str)

    # The first column is always blank (leading comma in CSV); drop it
    raw = raw.drop(columns=[0])

    # Assign proper column names from row 0 (which is the real header row)
    raw.columns = raw.iloc[0].str.strip()
    raw = raw.iloc[1:].reset_index(drop=True)

    # Rename columns for consistency
    rename_map = {
        "Retailer":          "Retailer",
        "Retailer ID":       "Retailer_ID",
        "Invoice Date":      "Invoice_Date",
        "Region":            "Region",
        "State":             "State",
        "City":              "City",
        "Product":           "Product",
        "Price per Unit":    "Price_per_Unit",
        "Units Sold":        "Units_Sold",
        "Total Sales":       "Total_Sales_Raw",
        "Operating Profit":  "Operating_Profit",
        "Operating Margin":  "Operating_Margin",
        "Sales Method":      "Sales_Method",
    }
    raw = raw.rename(columns=rename_map)

    # Keep only the columns we care about
    keep = list(rename_map.values())
    df = raw[[c for c in keep if c in raw.columns]].copy()

    # --- Step 2: Drop fully blank rows ---
    df.replace("", np.nan, inplace=True)
    df.dropna(how="all", inplace=True)

    # --- Step 3: Fix dtypes ---
    df["Invoice_Date"] = pd.to_datetime(df["Invoice_Date"], errors="coerce")

    for col in ["Price_per_Unit", "Units_Sold", "Total_Sales_Raw",
                "Operating_Profit", "Operating_Margin"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Round floating-point noise from source data
    df["Price_per_Unit"]   = df["Price_per_Unit"].round(2)
    df["Total_Sales_Raw"]  = df["Total_Sales_Raw"].round(2)
    df["Operating_Profit"] = df["Operating_Profit"].round(2)

    # --- Step 4: Remove duplicates ---
    df.drop_duplicates(inplace=True)

    # --- Step 5: Drop rows with missing critical fields ---
    df.dropna(subset=["Retailer", "Invoice_Date", "Price_per_Unit",
                      "Units_Sold", "Product"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # --- Step 6: Recalculate Total Sales = Quantity × Unit Price ---
    # (corrects any rounding errors in the raw "Total Sales" column)
    df["Total_Sales"] = (df["Units_Sold"] * df["Price_per_Unit"]).round(2)

    # --- Step 7: Derived time columns ---
    df["Year"]  = df["Invoice_Date"].dt.year
    df["Month"] = df["Invoice_Date"].dt.month
    df["Month_Name"] = df["Invoice_Date"].dt.strftime("%b")
    df["Year_Month"]  = df["Invoice_Date"].dt.to_period("M").astype(str)

    # Strip extra whitespace from string columns
    str_cols = ["Retailer", "Region", "State", "City", "Product", "Sales_Method"]
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].str.strip()

    return df


# ─────────────────────────────────────────────
# 2. SUMMARY STATISTICS
# ─────────────────────────────────────────────

def summary_stats(df: pd.DataFrame) -> dict:
    return {
        "total_revenue":      round(df["Total_Sales"].sum(), 2),
        "total_units":        int(df["Units_Sold"].sum()),
        "total_profit":       round(df["Operating_Profit"].sum(), 2),
        "num_transactions":   len(df),
        "avg_order_value":    round(df["Total_Sales"].mean(), 2),
        "avg_margin":         round(df["Operating_Margin"].mean() * 100, 2),
        "num_retailers":      df["Retailer"].nunique(),
        "num_products":       df["Product"].nunique(),
        "date_range_start":   str(df["Invoice_Date"].min().date()),
        "date_range_end":     str(df["Invoice_Date"].max().date()),
    }


# ─────────────────────────────────────────────
# 3. AGGREGATIONS
# ─────────────────────────────────────────────

def sales_by_retailer(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Retailer")
          .agg(Total_Sales=("Total_Sales", "sum"),
               Units_Sold=("Units_Sold", "sum"),
               Transactions=("Total_Sales", "count"),
               Avg_Margin=("Operating_Margin", "mean"))
          .round(2)
          .sort_values("Total_Sales", ascending=False)
          .reset_index()
    )


def sales_by_product(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Product")
          .agg(Total_Sales=("Total_Sales", "sum"),
               Units_Sold=("Units_Sold", "sum"),
               Avg_Price=("Price_per_Unit", "mean"),
               Avg_Margin=("Operating_Margin", "mean"))
          .round(2)
          .sort_values("Total_Sales", ascending=False)
          .reset_index()
    )


def sales_by_region(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Region")
          .agg(Total_Sales=("Total_Sales", "sum"),
               Units_Sold=("Units_Sold", "sum"),
               Avg_Margin=("Operating_Margin", "mean"))
          .round(2)
          .sort_values("Total_Sales", ascending=False)
          .reset_index()
    )


def sales_by_method(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Sales_Method")
          .agg(Total_Sales=("Total_Sales", "sum"),
               Units_Sold=("Units_Sold", "sum"),
               Transactions=("Total_Sales", "count"))
          .round(2)
          .sort_values("Total_Sales", ascending=False)
          .reset_index()
    )


def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    trend = (
        df.groupby(["Year", "Month", "Month_Name"])
          .agg(Total_Sales=("Total_Sales", "sum"),
               Units_Sold=("Units_Sold", "sum"),
               Operating_Profit=("Operating_Profit", "sum"))
          .round(2)
          .reset_index()
          .sort_values(["Year", "Month"])
    )
    trend["Period"] = trend["Month_Name"] + " " + trend["Year"].astype(str)
    return trend


def top_states(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return (
        df.groupby("State")
          .agg(Total_Sales=("Total_Sales", "sum"),
               Units_Sold=("Units_Sold", "sum"))
          .round(2)
          .sort_values("Total_Sales", ascending=False)
          .head(n)
          .reset_index()
    )


def profit_by_product(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Product")
          .agg(Total_Profit=("Operating_Profit", "sum"),
               Avg_Margin=("Operating_Margin", "mean"))
          .round(2)
          .sort_values("Total_Profit", ascending=False)
          .reset_index()
    )
