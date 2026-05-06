import pandas as pd
import argparse
import joblib
import json
from pathlib import Path

# ── Config ────────────────────────────────────────────────────
MODEL_DIR = Path("automation_projects/project5_ml/models")

# ── Load model + encoders + metadata ─────────────────────────
def load_model() -> tuple:
    model       = joblib.load(MODEL_DIR / "revenue_model.pkl")
    le_item     = joblib.load(MODEL_DIR / "le_item.pkl")
    le_channel  = joblib.load(MODEL_DIR / "le_channel.pkl")
    le_priority = joblib.load(MODEL_DIR / "le_priority.pkl")
    metadata    = json.loads((MODEL_DIR / "metadata.json").read_text())

    print(f"  ✅ Model loaded — trained on {metadata['trained_on']}")
    print(f"  ✅ R² Score     : {metadata['r2_score']}")
    print(f"  ✅ MAE          : ${metadata['mae']:,.2f}")

    return model, le_item, le_channel, le_priority

# ── Make prediction ───────────────────────────────────────────
def predict(
    model,
    le_item,
    le_channel,
    le_priority,
    units:    int,
    price:    float,
    item:     str,
    channel:  str,
    priority: str,
    month:    int,
) -> float:

    sample = pd.DataFrame([{
        "units_sold":             units,
        "unit_price":             price,
        "item_type_encoded":      le_item.transform([item])[0],
        "sales_channel_encoded":  le_channel.transform([channel])[0],
        "order_priority_encoded": le_priority.transform([priority])[0],
        "order_month":            month,
    }])

    return model.predict(sample)[0]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Predict sales revenue using trained model"
    )
    parser.add_argument("--units",    type=int,   help="Units sold")
    parser.add_argument("--price",    type=float, help="Unit price")
    parser.add_argument("--item",     type=str,   help="Item type")
    parser.add_argument("--channel",  type=str,   choices=["Online", "Offline"])
    parser.add_argument("--priority", type=str,   choices=["H", "M", "L", "C"])
    parser.add_argument("--month",    type=int,   choices=range(1, 13))
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print("\n" + "═" * 50)
    print("  🔮 REVENUE PREDICTOR")
    print("═" * 50)

    model, le_item, le_channel, le_priority = load_model()

    # ── Single prediction mode — all args provided ────────────
    if all([args.units, args.price, args.item, args.channel,
            args.priority, args.month]):

        predicted = predict(
            model, le_item, le_channel, le_priority,
            units    = args.units,
            price    = args.price,
            item     = args.item,
            channel  = args.channel,
            priority = args.priority,
            month    = args.month,
        )

        print(f"\n  🔮 Prediction:")
        print(f"  {'─' * 40}")
        print(f"    Units     : {args.units:,}")
        print(f"    Price     : ${args.price:,.2f}")
        print(f"    Item      : {args.item}")
        print(f"    Channel   : {args.channel}")
        print(f"    Priority  : {args.priority}")
        print(f"    Month     : {args.month}")
        print(f"  {'─' * 40}")
        print(f"    💰 Predicted Revenue : ${predicted:,.2f}")
        print(f"  {'─' * 40}")

    # ── Demo mode — no args, run sample predictions ───────────
    else:
        print(f"\n  Valid item types  : {list(le_item.classes_)}")
        print(f"  Valid channels    : {list(le_channel.classes_)}")
        print(f"  Valid priorities  : {list(le_priority.classes_)}")

        samples = [
            {"units": 500,  "price": 250.0, "item": "Cosmetics",      "channel": "Online",  "priority": "H", "month": 6},
            {"units": 1000, "price": 150.0, "item": "Baby Food",       "channel": "Offline", "priority": "M", "month": 1},
            {"units": 200,  "price": 650.0, "item": "Office Supplies", "channel": "Online",  "priority": "L", "month": 11},
            {"units": 9000, "price": 10.0,  "item": "Fruits",          "channel": "Offline", "priority": "C", "month": 3},
        ]

        print(f"\n{'─' * 50}")
        print(f"  {'Units':>6}  {'Price':>8}  {'Item':<18} {'Ch':<8} {'Pri'}  {'Month':>5}  {'Predicted Revenue':>18}")
        print(f"{'─' * 50}")

        for s in samples:
            predicted = predict(
                model, le_item, le_channel, le_priority,
                units    = s["units"],
                price    = s["price"],
                item     = s["item"],
                channel  = s["channel"],
                priority = s["priority"],
                month    = s["month"],
            )
            print(
                f"  {s['units']:>6}  "
                f"${s['price']:>7.2f}  "
                f"{s['item']:<18} "
                f"{s['channel']:<8} "
                f"{s['priority']:<4} "
                f"{s['month']:>5}  "
                f"${predicted:>17,.2f}"
            )

        print(f"{'─' * 50}")
        print("\n  💡 Tip: pass --units --price --item --channel --priority --month")
        print("         for a single custom prediction")

    print("\n  ✅ Done")
    print("═" * 50)


if __name__ == "__main__":
    main()