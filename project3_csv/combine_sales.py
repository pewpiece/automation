import csv
import json
from pathlib import Path
from datetime import date

# ── Paths ─────────────────────────────────────────────────────
folder = Path("automation_projects/project3_csv/monthly_sales")
output = Path("automation_projects/project3_csv")

all_rows          = []
revenue_by_region = {}
revenue_by_month  = {}

# ── Phase 1: Read and combine all CSVs ────────────────────────
print("📂 Reading monthly sales files...\n")

for csv_file in sorted(folder.glob("*.csv")):
    if csv_file.name == "combined_sales.csv":
        continue

    with open(csv_file, newline="") as f:
        reader = csv.DictReader(f)
        rows   = list(reader)

    all_rows.extend(rows)

    month_revenue = sum(float(row["Total Revenue"]) for row in rows)
    revenue_by_month[csv_file.name] = month_revenue

    for row in rows:
        region  = row["Region"]
        revenue = float(row["Total Revenue"])
        revenue_by_region[region] = revenue_by_region.get(region, 0) + revenue

    print(f"  ✅ Read : {csv_file.name:25} ({len(rows)} rows"
          f"  |  ${month_revenue:>15,.2f})")

# ── Phase 2: Write combined CSV ───────────────────────────────
combined_path = output / "combined_sales.csv"

if all_rows:
    with open(combined_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=all_rows[0].keys())
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"\n  📄 Combined CSV saved : {combined_path.name}"
          f" ({len(all_rows)} total rows)")
else:
    print("⚠️  No data found.")

# ── Phase 3: Build and write summary JSON ─────────────────────
best_month    = max(revenue_by_month, key=revenue_by_month.get)
total_revenue = sum(float(row["Total Revenue"]) for row in all_rows)
total_profit  = sum(float(row["Total Profit"])  for row in all_rows)

summary = {
    "generated_on":  str(date.today()),
    "total_orders":  len(all_rows),
    "total_revenue": round(total_revenue, 2),
    "total_profit":  round(total_profit,  2),
    "best_month":    best_month,
    "revenue_by_month": {
        k: round(v, 2)
        for k, v in sorted(revenue_by_month.items())
    },
    "revenue_by_region": {
        k: round(v, 2)
        for k, v in sorted(revenue_by_region.items())
    },
}

summary_path = output / "summary_report.json"
with open(summary_path, "w") as f:
    json.dump(summary, f, indent=4)

# ── Terminal Summary ──────────────────────────────────────────
print(f"\n{'─' * 50}")
print(f"  📦 Total Orders  : {summary['total_orders']}")
print(f"  💰 Total Revenue : ${summary['total_revenue']:>15,.2f}")
print(f"  📈 Total Profit  : ${summary['total_profit']:>15,.2f}")
print(f"  🏆 Best Month    : {summary['best_month']}")
print(f"{'─' * 50}")
print(f"\n  Revenue by Region:")
for region, rev in summary["revenue_by_region"].items():
    print(f"    {region:45} : ${rev:>15,.2f}")
print(f"\n  📊 Summary JSON saved : {summary_path.name}")