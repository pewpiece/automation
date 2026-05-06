# Automation Projects

This repository contains a set of Python automation exercises covering file handling, CSV processing, backups, machine learning, and API workflows.

## Setup

1. Create and activate a virtual environment from the repository root.
2. Install the common dependencies:

```bash
pip install pandas scikit-learn joblib fastapi uvicorn requests prefect
```

3. Run commands from the `automation_projects/` root so the relative paths in the scripts resolve correctly.

## Project List

- `project1_rename/` - rename files in the `downloads/` folder by normalizing file names
- `project2_mover/` - move mixed file types into organized subfolders
- `project3_api/` - stores raw country data pulled from an API
- `project3_csv/` - combine, clean, and analyze sales CSV data
- `project4_backup/` - create timestamped zip backups with rotation and logging
- `project5_ml/` - train and use a revenue prediction model
- `project6_api/` - FastAPI app that serves the trained model
- `project7_prefect/` - Prefect flow that fetches country data and retrains the model

## Run Instructions

### `project1_rename`

Normalize the file names inside `project1_rename/downloads/`:

```bash
python project1_rename/renamefiles.py
```

### `project2_mover`

Organize the files inside `project2_mover/mixed_files/` into type-based folders:

```bash
python project2_mover/file_organizer.py
```

### `project3_csv`

Combine the monthly sales files, then clean and inspect the data:

```bash
python project3_csv/combine_sales.py
python project3_csv/cleaner.py
python project3_csv/sales_exercises.py
```

`combine_sales.py` writes `combined_sales.csv` and `summary_report.json`. `cleaner.py` reads `messy_sales.csv` and produces `cleaned_sales.csv` plus `cleaning_report.json`.

### `project4_backup`

Create a timestamped zip backup of the `automation_projects/` folder and update the backup log:

```bash
python project4_backup/backup_system.py
```

### `project5_ml`

Train the revenue model on the cleaned sales data:

```bash
python project5_ml/train.py
```

Run a prediction from the saved model:

```bash
python project5_ml/predict.py --units 500 --price 250 --item "Cosmetics" --channel Online --priority H --month 6
```

You can also run `python project5_ml/predict.py` with no arguments to see sample predictions.

### `project6_api`

Start the FastAPI app with Uvicorn:

```bash
uvicorn project6_api.api:app --reload
```

Then open:

- `http://127.0.0.1:8000/` for the API root
- `http://127.0.0.1:8000/docs` for interactive API docs

### `project7_prefect`

Run the Prefect flow:

```bash
python project7_prefect/pipeline.py
```

The flow fetches country data, retrains the model, and writes a run report under `project7_prefect/reports/`.

## Notes

- Generated caches and local virtual environments are ignored via `.gitignore`.
- The ML and API projects expect the model files in `project5_ml/models/`.
- If you change any input CSVs, rerun the CSV pipeline before retraining the model.