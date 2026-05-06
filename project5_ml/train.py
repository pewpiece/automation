import pandas as pd
import joblib
import json
import argparse
from pathlib import Path
from datetime import datetime
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

# ── Config ────────────────────────────────────────────────────
DATA_FILE = Path("automation_projects/project3_csv/cleaned_sales.csv")
MODEL_DIR = Path("automation_projects/project5_ml/models")
LOG_DIR = Path("automation_projects/project5_ml/logs")

FEATURES = [
    "units_sold",
    "unit_price",
    "item_type_encoded",
    "sales_channel_encoded",
    "order_priority_encoded",
    "order_month",
]
TARGET = "total_revenue"


# ── Step 1: Load ──────────────────────────────────────────────
def load(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"  📥 Loaded : {path.name} ({len(df)} rows)")
    return df


# ── Step 2: Prepare features ──────────────────────────────────
def prepare(df: pd.DataFrame) -> tuple:
    # Extract month
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["order_month"] = df["order_date"].dt.month

    # Encode text columns — keep encoders to use later for prediction
    le_item = LabelEncoder()
    le_channel = LabelEncoder()
    le_priority = LabelEncoder()

    df["item_type_encoded"] = le_item.fit_transform(df["item_type"])
    df["sales_channel_encoded"] = le_channel.fit_transform(df["sales_channel"])
    df["order_priority_encoded"] = le_priority.fit_transform(df["order_priority"])

    X = df[FEATURES]
    y = df[TARGET]

    print(f"  ✅ Features : {FEATURES}")
    print(f"  ✅ Target   : {TARGET}")

    return X, y, le_item, le_channel, le_priority


# ── Step 3: Train ─────────────────────────────────────────────
def train(X, y, n_estimators: int = 100, test_size: float = 0.2) -> tuple:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42
    )

    model = RandomForestRegressor(n_estimators=n_estimators, random_state=42)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    r2  = r2_score(y_test, predictions)

    print(f"  📊 MAE      : ${mae:,.2f}")
    print(f"  📊 R² Score : {r2:.4f}")
    print(f"  📊 Train    : {len(X_train)} rows")
    print(f"  📊 Test     : {len(X_test)} rows")

    return model, mae, r2, X_test, y_test


# ── Step 4: Save ──────────────────────────────────────────────
def save(
    model, mae, r2,
    le_item, le_channel, le_priority
) -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    # Save model
    joblib.dump(model, MODEL_DIR / "revenue_model.pkl")

    # Save encoders — needed to make predictions later
    joblib.dump(le_item, MODEL_DIR / "le_item.pkl")
    joblib.dump(le_channel, MODEL_DIR / "le_channel.pkl")
    joblib.dump(le_priority, MODEL_DIR / "le_priority.pkl")

    # Save metadata
    metadata = {
        "trained_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "features": FEATURES,
        "target": TARGET,
        "mae": round(mae, 2),
        "r2_score": round(r2, 4),
    }

    (MODEL_DIR / "metadata.json").write_text(
        json.dumps(metadata, indent=2)
    )

    print(f"  💾 Model saved    : {MODEL_DIR}/revenue_model.pkl")
    print(f"  💾 Metadata saved : {MODEL_DIR}/metadata.json")


# ── Step 5: Predict ───────────────────────────────────────────
def predict_sample(
    model, le_item, le_channel, le_priority
) -> None:
    sample = pd.DataFrame([{
        "units_sold": 500,
        "unit_price": 250.0,
        "item_type_encoded": le_item.transform(["Cosmetics"])[0],
        "sales_channel_encoded": le_channel.transform(["Online"])[0],
        "order_priority_encoded": le_priority.transform(["H"])[0],
        "order_month": 6,
    }])

    predicted = model.predict(sample)[0]

    print(f"\n  🔮 Sample prediction:")
    print(f"     Units    : 500")
    print(f"     Price    : $250.00")
    print(f"     Channel  : Online")
    print(f"     Month    : June")
    print(f"     ──────────────────")
    print(f"     Predicted Revenue: ${predicted:,.2f}")



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train revenue prediction model on sales CSV"
    )
    parser.add_argument(
        "--input",
        type    = str,
        default = str(DATA_FILE),
        help    = "Path to cleaned sales CSV"
    )
    parser.add_argument(
        "--estimators",
        type    = int,
        default = 100,
        help    = "Number of trees in Random Forest (default: 100)"
    )
    parser.add_argument(
        "--test-size",
        type    = float,
        default = 0.2,
        help    = "Test split ratio (default: 0.2)"
    )
    parser.add_argument(
        "--dry-run",
        action  = "store_true",
        help    = "Train and evaluate but do not save model"
    )
    return parser.parse_args()

def main() -> None:
    args = parse_args()

    print("\n" + "═" * 50)
    print("  🤖 ML TRAINING PIPELINE")
    if args.dry_run:
        print("  MODE: DRY RUN — model will not be saved")
    print("═" * 50)

    df                                     = load(Path(args.input))
    X, y, le_item, le_channel, le_priority = prepare(df)

    # Pass CLI args into train()
    model, mae, r2, X_test, y_test = train(
        X, y,
        n_estimators = args.estimators,
        test_size    = args.test_size,
    )

    if args.dry_run:
        print("\n  🚫 Dry run — skipping save")
    else:
        save(model, mae, r2, le_item, le_channel, le_priority)
        predict_sample(model, le_item, le_channel, le_priority)

    print("\n" + "═" * 50)
    print("  ✅ Training complete")
    print("═" * 50)


if __name__ == "__main__":
    main()