import pandas as pd
from pathlib import Path

df = pd.read_csv(
    Path("automation_projects/project3_csv/cleaned_sales.csv")
)

print(f"Shape          : {df.shape}")
print(f"Columns        : {df.columns.tolist()}")
print(f"Nulls          : {df.isnull().sum().sum()} total")
print(f"Duplicates     : {df.duplicated().sum()}")
print(f"\nDate sample    :\n{df['order_date'].head(5).tolist()}")
print(f"\nRegion sample  :\n{df['region'].unique()}")
print(f"\nRevenue sample :\n{df['total_revenue'].head(5).tolist()}")
print(f"\nProfit Margin% :\n{df['profit_margin_%'].describe()}")