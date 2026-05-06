from fastapi import FastAPI, Query
from pydantic import BaseModel
from contextlib import asynccontextmanager
from typing import Literal
from pathlib import Path
import joblib
import json
import pandas as pd

# ── Paths ─────────────────────────────────────────────────────
MODEL_DIR = Path("automation_projects/project5_ml/models")

# ── Global model objects ──────────────────────────────────────
model       = None
le_item     = None
le_channel  = None
le_priority = None
metadata    = None

# ── Startup / shutdown ────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, le_item, le_channel, le_priority, metadata

    print("🚀 Loading model...")
    model       = joblib.load(MODEL_DIR / "revenue_model.pkl")
    le_item     = joblib.load(MODEL_DIR / "le_item.pkl")
    le_channel  = joblib.load(MODEL_DIR / "le_channel.pkl")
    le_priority = joblib.load(MODEL_DIR / "le_priority.pkl")
    metadata    = json.loads((MODEL_DIR / "metadata.json").read_text())
    print(f"✅ Model loaded — R²: {metadata['r2_score']}")
    yield
    print("👋 Shutting down")

app = FastAPI(
    title       = "Revenue Prediction API",
    description = "Predicts sales revenue using a trained Random Forest model",
    version     = "1.0.0",
    lifespan    = lifespan,
)

# ── Response models ───────────────────────────────────────────
class ModelInfo(BaseModel):
    trained_on: str
    features:   list
    r2_score:   float
    mae:        float

class PredictionResponse(BaseModel):
    predicted_revenue: float
    model_r2:          float
    model_mae:         float
    inputs:            dict

# ── Endpoints ─────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "name":    "Revenue Prediction API",
        "version": "1.0.0",
        "docs":    "/docs",
        "model":   "/model",
        "predict": "/predict",
    }

@app.get("/model", response_model=ModelInfo)
def model_info():
    return ModelInfo(
        trained_on = metadata["trained_on"],
        features   = metadata["features"],
        r2_score   = metadata["r2_score"],
        mae        = metadata["mae"],
    )

@app.get("/predict", response_model=PredictionResponse)
def predict(
    units: int = Query(
        ..., gt=0, description="Units sold"
    ),
    price: float = Query(
        ..., gt=0.0, description="Unit price per item"
    ),
    item: Literal[
        "Baby Food", "Cereal", "Clothes", "Cosmetics",
        "Fruits", "Household", "Office Supplies",
        "Personal Care", "Snacks"
    ] = Query(..., description="Item type"),
    channel: Literal["Online", "Offline"] = Query(
        ..., description="Sales channel"
    ),
    priority: Literal["H", "M", "L", "C"] = Query(
        ..., description="Order priority"
    ),
    month: int = Query(
        ..., ge=1, le=12, description="Order month (1-12)"
    ),
):
    sample = pd.DataFrame([{
        "units_sold":             units,
        "unit_price":             price,
        "item_type_encoded":      le_item.transform([item])[0],
        "sales_channel_encoded":  le_channel.transform([channel])[0],
        "order_priority_encoded": le_priority.transform([priority])[0],
        "order_month":            month,
    }])

    predicted = float(model.predict(sample)[0])

    return PredictionResponse(
        predicted_revenue = round(predicted, 2),
        model_r2          = metadata["r2_score"],
        model_mae         = metadata["mae"],
        inputs            = {
            "units":    units,
            "price":    price,
            "item":     item,
            "channel":  channel,
            "priority": priority,
            "month":    month,
        }
    )