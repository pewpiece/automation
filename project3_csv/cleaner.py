import pandas as pd
import json
from pathlib import Path
from datetime import date

# ── Config ────────────────────────────────────────────────────
INPUT_FILE  = Path("automation_projects/project3_csv/messy_sales.csv")
OUTPUT_FILE = Path("automation_projects/project3_csv/cleaned_sales.csv")
REPORT_FILE = Path("automation_projects/project3_csv/cleaning_report.json")

NUMERIC_COLS = ["units_sold", "unit_price", "total_revenue", "total_profit"]
TEXT_COLS    = ["region", "country", "item_type", "sales_channel", "order_priority"]
DATE_COLS    = ["order_date"]

# ── Phase 1: Load ─────────────────────────────────────────────
def load(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"  📥 Loaded  : {path.name}")
    print(f"     Shape   : {df.shape}")
    return df

# ── Phase 2: Detect ───────────────────────────────────────────
def detect(df: pd.DataFrame) -> dict:
    report = {
        "file":           INPUT_FILE.name,
        "cleaned_on":     str(date.today()),
        "original_shape": {"rows": df.shape[0], "cols": df.shape[1]},
        "issues_found":   {},
        "fixes_applied":  [],
        "final_shape":    {},
    }

    # Null counts — only columns that actually have nulls
    null_counts = df.isnull().sum()
    report["issues_found"]["null_counts"] = {
        col: int(count)
        for col, count in null_counts.items()
        if count > 0
    }

    # Duplicate rows
    report["issues_found"]["duplicate_rows"] = int(df.duplicated().sum())

    # Fully empty columns
    report["issues_found"]["empty_columns"] = (
        df.columns[df.isnull().all()].tolist()
    )

    # Column names that need cleaning
    report["issues_found"]["messy_col_names"] = [
        col for col in df.columns
        if col != col.strip()
        or " " in col.strip()
        or col != col.lower()
    ]

    return report

# ── Phase 3: Clean ────────────────────────────────────────────
def clean(df: pd.DataFrame, report: dict) -> pd.DataFrame:

    # ── Step 1: Fix column names ──────────────────────────────
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )
    report["fixes_applied"].append("Standardized column names")

    # ── Step 2: Drop fully empty columns ──────────────────────
    empty_cols = df.columns[df.isnull().all()].tolist()
    if empty_cols:
        df = df.drop(columns=empty_cols)
        report["fixes_applied"].append(
            f"Dropped empty columns: {empty_cols}"
        )

    # ── Step 3: Remove duplicates ─────────────────────────────
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)
    if removed:
        report["fixes_applied"].append(
            f"Removed {removed} duplicate rows"
        )

    # ── Step 4: Fix numeric columns ───────────────────────────
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)                          # force to string first
                .str.replace("$", "", regex=False)   # remove $
                .str.replace(",", "", regex=False)   # remove ,
                .str.strip()                          # remove whitespace
                .replace("nan", float("nan"))         # restore real NaN
                .astype(float)                        # convert to float
            )
            median = df[col].median()
            nulls  = df[col].isnull().sum()
            df[col] = df[col].fillna(median)
            if nulls:
                report["fixes_applied"].append(
                    f"Filled {nulls} nulls in '{col}' with median ({median:.2f})"
                )

    report["fixes_applied"].append("Cleaned numeric columns")

    # ── Step 5: Fix text columns ──────────────────────────────
    for col in TEXT_COLS:
        if col in df.columns:
            nulls     = df[col].isnull().sum()
            df[col]   = df[col].fillna("Unknown")
            df[col]   = df[col].str.strip().str.title()
            if nulls:
                report["fixes_applied"].append(
                    f"Filled {nulls} nulls in '{col}' with 'Unknown'"
                )

    report["fixes_applied"].append("Standardized text columns")

    # ── Step 6: Fix date columns ──────────────────────────────
    for col in DATE_COLS:
        if col in df.columns:
            df[col] = pd.to_datetime(
                df[col],
                format="mixed",    # ← handles both dd/mm/yyyy and yyyy-mm-dd
                dayfirst=True      # ← when ambiguous, treat first number as day
            )
        df[col] = df[col].dt.strftime("%Y-%m-%d")

    # ── Step 7: Add profit margin column ─────────────────────
    if "total_revenue" in df.columns and "total_profit" in df.columns:
        df["profit_margin_%"] = (
            (df["total_profit"] / df["total_revenue"]) * 100
        ).round(2)
        report["fixes_applied"].append(
            "Added derived column: profit_margin_%"
        )

    return df

# ── Phase 4: Export ───────────────────────────────────────────
def export(df: pd.DataFrame, report: dict) -> None:
    report["final_shape"] = {
        "rows": df.shape[0],
        "cols": df.shape[1]
    }

    # Save clean CSV
    df.to_csv(OUTPUT_FILE, index=False)

    # Save JSON report
    with open(REPORT_FILE, "w") as f:
        json.dump(report, f, indent=4)

    print(f"  📄 Clean CSV : {OUTPUT_FILE.name}")
    print(f"  📊 Report    : {REPORT_FILE.name}")

# ── Phase 5: Print Summary ────────────────────────────────────
def print_summary(report: dict) -> None:
    issues  = report["issues_found"]
    orig    = report["original_shape"]
    final   = report["final_shape"]

    print(f"\n{'─' * 50}")
    print(f"  📋 CLEANING SUMMARY")
    print(f"{'─' * 50}")
    print(f"  Original shape   : {orig['rows']} rows × {orig['cols']} cols")
    print(f"  Final shape      : {final['rows']} rows × {final['cols']} cols")
    print(f"  Rows removed     : {orig['rows'] - final['rows']}")
    print(f"  Cols removed     : {orig['cols'] - final['cols']}")

    print(f"\n  Issues detected:")
    print(f"    Duplicate rows : {issues['duplicate_rows']}")
    print(f"    Empty columns  : {issues['empty_columns']}")
    print(f"    Messy colnames : {issues['messy_col_names']}")

    if issues["null_counts"]:
        print(f"    Nulls found:")
        for col, count in issues["null_counts"].items():
            print(f"      {col:25} : {count}")

    print(f"\n  Fixes applied ({len(report['fixes_applied'])}):")
    for fix in report["fixes_applied"]:
        print(f"    ✅ {fix}")

    print(f"{'─' * 50}")

# ── Main ──────────────────────────────────────────────────────
def main() -> None:
    print("\n" + "═" * 50)
    print("  🧹 AUTOMATED DATA CLEANER")
    print("═" * 50)

    df     = load(INPUT_FILE)
    report = detect(df)
    df     = clean(df, report)
    export(df, report)
    print_summary(report)

    print("\n  ✅ Done — files saved to:")
    print(f"     {OUTPUT_FILE.resolve()}")
    print(f"     {REPORT_FILE.resolve()}")
    print("═" * 50)

if __name__ == "__main__":
    main()