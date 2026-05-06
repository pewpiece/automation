from pathlib import Path
import pandas as pd

# ── Load CSV ──────────────────────────────────────────────────
csv_path = Path(__file__).parent / "combined_sales.csv"
df = pd.read_csv(csv_path)
df.columns = df.columns.str.strip()   # defensive clean

# =====================================================
# Exercise 1 — Inspector
# =====================================================
print("\n" + "=" * 50)
print("EXERCISE 1 — INSPECTOR")
print("=" * 50)

print(f"Shape            : {df.shape[0]} rows × {df.shape[1]} columns")

print(f"\nColumns          : {df.columns.tolist()}")

print(f"\nNull values:")
nulls = df.isnull().sum()
print(nulls[nulls > 0] if nulls.any() else "  None — clean dataset ✅")

print(f"\nDuplicate rows   : {df.duplicated().sum()}")

print(f"\nTotal Revenue stats:")
print(f"  Min  : ${df['Total Revenue'].min():>15,.2f}")
print(f"  Max  : ${df['Total Revenue'].max():>15,.2f}")
print(f"  Mean : ${df['Total Revenue'].mean():>15,.2f}")

# =====================================================
# Exercise 2 — Filter and sort
# =====================================================
print("\n" + "=" * 50)
print("EXERCISE 2 — FILTER AND SORT (Online only, Top 5)")
print("=" * 50)

top_5_online = (
    df[df["Sales Channel"] == "Online"]
    .sort_values("Total Revenue", ascending=False)
    [["Region", "Country", "Item Type", "Total Revenue", "Total Profit"]]
    .head(5)
    .reset_index(drop=True)
)

print(top_5_online.to_string())

# =====================================================
# Exercise 3 — New column
# =====================================================
print("\n" + "=" * 50)
print("EXERCISE 3 — PROFIT MARGIN % (Top 5)")
print("=" * 50)

df["Profit Margin %"] = (
    (df["Total Profit"] / df["Total Revenue"]) * 100
).round(2)

top_margin = (
    df.sort_values("Profit Margin %", ascending=False)
    [["Region", "Country", "Item Type", "Total Revenue", "Profit Margin %"]]
    .head(5)
    .reset_index(drop=True)
)

print(top_margin.to_string())

# =====================================================
# Exercise 4 — Group by
# =====================================================
print("\n" + "=" * 50)
print("EXERCISE 4 — GROUP BY REGION")
print("=" * 50)

grouped = (
    df.groupby("Region")
    .agg(
        total_revenue    = ("Total Revenue", "sum"),
        average_profit   = ("Total Profit",  "mean"),
        number_of_orders = ("Country",       "count"),
    )
    .reset_index()
    .sort_values("total_revenue", ascending=False)
)

# Format for readable output
grouped["total_revenue"]  = grouped["total_revenue"].map("${:,.2f}".format)
grouped["average_profit"] = grouped["average_profit"].map("${:,.2f}".format)

print(grouped.to_string(index=False))