from pathlib import Path

folder = Path("automation_projects/project1_rename/downloads")

for file in folder.iterdir():
    if file.is_file():
        stem = file.stem
        suffix = file.suffix

        # Clean the stem — step by step
        new_stem = stem.lower()
        new_stem = new_stem.replace("(", "").replace(")", "")  # remove parentheses
        new_stem = new_stem.replace(" ", "_")                  # spaces to underscores

        # Collapse multiple underscores: "data___export" → "data_export"
        while "__" in new_stem:
            new_stem = new_stem.replace("__", "_")

        new_stem = new_stem.strip("_")   # clean up any leading/trailing underscores

        # Rebuild filename
        new_name = new_stem + suffix
        new_path = folder / new_name

        # Skip if already clean
        if new_name == file.name:
            print(f"  SKIP : {file.name}")
            continue

        file.rename(new_path)
        print(f"  ✅ {file.name:40} → {new_name}")