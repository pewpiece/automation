import requests
import pandas as pd
import joblib
import json
from pathlib import Path
from datetime import datetime
from prefect import flow, task, get_run_logger
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

# ── Paths ─────────────────────────────────────────────────────
BASE       = Path("automation_projects")
DATA_FILE  = BASE / "project3_csv/cleaned_sales.csv"
MODEL_DIR  = BASE / "project5_ml/models"
REPORT_DIR = BASE / "project7_prefect/reports"

API_URL    = (
    "https://restcountries.com/v3.1/all"
    "?fields=name,capital,region,subregion,"
    "population,area,landlocked,languages,"
    "currencies,flags"
)

FEATURES = [
    "units_sold", "unit_price",
    "item_type_encoded", "sales_channel_encoded",
    "order_priority_encoded", "order_month"
]

# ── Task 1: Fetch country data ────────────────────────────────
@task(retries=3, retry_delay_seconds=10, name="Fetch Country Data")
def fetch_countries() -> int:
    logger = get_run_logger()
    logger.info("Fetching country data from API...")

    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()
    countries = response.json()

    # Save raw
    raw_path = BASE / "project3_api/data/countries_raw.json"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(json.dumps(countries, indent=2))

    logger.info(f"Fetched and saved {len(countries)} countries")
    return len(countries)


# ── Task 2: Retrain model ─────────────────────────────────────
@task(retries=2, retry_delay_seconds=5, name="Retrain Revenue Model")
def retrain_model() -> dict:
    logger = get_run_logger()
    logger.info("Loading sales data...")

    df = pd.read_csv(DATA_FILE)

    # Feature engineering
    df["order_date"]  = pd.to_datetime(df["order_date"])
    df["order_month"] = df["order_date"].dt.month

    le_item     = LabelEncoder()
    le_channel  = LabelEncoder()
    le_priority = LabelEncoder()

    df["item_type_encoded"]      = le_item.fit_transform(df["item_type"])
    df["sales_channel_encoded"]  = le_channel.fit_transform(df["sales_channel"])
    df["order_priority_encoded"] = le_priority.fit_transform(df["order_priority"])

    X = df[FEATURES]
    y = df["total_revenue"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    r2  = r2_score(y_test, predictions)

    logger.info(f"Model trained — R²: {r2:.4f} | MAE: ${mae:,.2f}")

    # Save model + encoders
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model,       MODEL_DIR / "revenue_model.pkl")
    joblib.dump(le_item,     MODEL_DIR / "le_item.pkl")
    joblib.dump(le_channel,  MODEL_DIR / "le_channel.pkl")
    joblib.dump(le_priority, MODEL_DIR / "le_priority.pkl")

    metrics = {
        "trained_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "features":   FEATURES,
        "target":     "total_revenue",
        "mae":        round(mae, 2),
        "r2_score":   round(r2, 4),
        "train_rows": len(X_train),
        "test_rows":  len(X_test),
    }

    (MODEL_DIR / "metadata.json").write_text(
        json.dumps(metrics, indent=2)
    )

    logger.info("Model and metadata saved")
    return metrics


# ── Task 3: Save run report ───────────────────────────────────
@task(name="Save Run Report")
def save_report(countries_fetched: int, model_metrics: dict) -> None:
    logger = get_run_logger()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    report = {
        "run_timestamp":      datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "countries_fetched":  countries_fetched,
        "model_r2":           model_metrics["r2_score"],
        "model_mae":          model_metrics["mae"],
        "model_trained_on":   model_metrics["trained_on"],
        "status":             "success",
    }

    report_path = REPORT_DIR / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path.write_text(json.dumps(report, indent=2))

    logger.info(f"Run report saved: {report_path.name}")


# ── Flow ──────────────────────────────────────────────────────
@flow(name="Automation Pipeline", log_prints=True)
def automation_pipeline():
    logger = get_run_logger()

    logger.info("=" * 40)
    logger.info("AUTOMATION PIPELINE STARTING")
    logger.info("=" * 40)

    # Run tasks in sequence
    countries_fetched = fetch_countries()
    model_metrics     = retrain_model()
    save_report(countries_fetched, model_metrics)

    logger.info("=" * 40)
    logger.info(f"PIPELINE COMPLETE")
    logger.info(f"Countries : {countries_fetched}")
    logger.info(f"R² Score  : {model_metrics['r2_score']}")
    logger.info(f"MAE       : ${model_metrics['mae']:,.2f}")
    logger.info("=" * 40)


# ── Entry point ───────────────────────────────────────────────
if __name__ == "__main__":
    automation_pipeline.serve(
        name     = "daily-automation-pipeline",
        cron     = "*/2 * * * *",   # every 2 minutes — for testing
        tags     = ["automation", "daily"],
    )