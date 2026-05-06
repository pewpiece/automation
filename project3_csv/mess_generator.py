import pandas as pd
import numpy as np
from pathlib import Path

# Load clean base
clean = pd.read_csv(
    Path("automation_projects/project3_csv/combined_sales.csv")
)

messy = clean.copy()

# 1. Inconsistent column name casing and spaces
messy.columns = [
    "Region ", "Country", "item type", "Sales Channel",
    "Order Priority", "Order Date", "Units Sold",
    " Unit Price", "Total Revenue", "Total Profit"
]

# 2. Inconsistent region casing and whitespace
messy.loc[0:10,  "Region "] = messy.loc[0:10,  "Region "].str.upper()
messy.loc[11:20, "Region "] = messy.loc[11:20, "Region "].str.lower()
messy.loc[21:30, "Region "] = messy.loc[21:30, "Region "] + "  "

# 3. Inject missing values
np.random.seed(42)
for col in ["item type", "Units Sold", " Unit Price"]:
    null_idx = np.random.choice(messy.index, size=6, replace=False)
    messy.loc[null_idx, col] = np.nan

# 4. Inject duplicate rows
dupes = messy.iloc[0:5].copy()
messy = pd.concat([messy, dupes], ignore_index=True)

# 5. Corrupt some numeric values as strings
messy["Total Revenue"] = messy["Total Revenue"].astype(object)
messy.loc[5:8, "Total Revenue"] = messy.loc[5:8, "Total Revenue"].apply(
    lambda x: f"${float(x):,.2f}"
)

# 6. Mixed date formats — FIXED
messy.loc[0:15, "Order Date"] = pd.to_datetime(
    messy.loc[0:15, "Order Date"],
    format="mixed",
    dayfirst=False
).dt.strftime("%d/%m/%Y")

# 7. Add a fully empty column
messy["Notes"] = np.nan

# Save
output = Path("automation_projects/project3_csv/messy_sales.csv")
messy.to_csv(output, index=False)

print(f"✅ Messy dataset created: {output}")
print(f"   Shape  : {messy.shape}")
print(f"   Nulls  :\n{messy.isnull().sum()}")
print(f"   Dupes  : {messy.duplicated().sum()}")