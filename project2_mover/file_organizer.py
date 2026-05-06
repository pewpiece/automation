from pathlib import Path
import shutil

# ── Constants ─────────────────────────────────────────────────
BASE_DIR = Path("automation_projects/project2_mover/mixed_files")

EXTENSION_MAP = {
    ".csv":  "csv_files",
    ".txt":  "text_files",
    ".py":   "python_files",
    ".json": "json_files",
}

# ── Main Function ─────────────────────────────────────────────
def organize_files(folder: Path) -> None:
    # Check if directory exists
    if not folder.exists():
        print("❌ Folder does not exist.")
        return

    # Collect only files (not subfolders) in one clean line
    files = [f for f in folder.iterdir() if f.is_file()]

    # Handle empty folder
    if not files:
        print("⚠️  Folder is empty. Nothing to organize.")
        return

    print(f"📂 Found {len(files)} files to organize...\n")

    moved   = 0
    skipped = 0

    for file in files:
        target_folder_name = EXTENSION_MAP.get(file.suffix)

        # Unknown extension — skip
        if target_folder_name is None:
            print(f"  ⚠️  Skipped : {file.name} (unknown extension '{file.suffix}')")
            skipped += 1
            continue

        # Build destination and create folder if needed
        dest_folder = folder / target_folder_name
        dest_folder.mkdir(exist_ok=True)

        # Move the file
        shutil.move(str(file), str(dest_folder / file.name))
        print(f"  ✅ Moved   : {file.name:30} → {target_folder_name}/")
        moved += 1

    # ── Summary ───────────────────────────────────────────────
    print(f"\n{'─' * 45}")
    print(f"  ✅ Moved   : {moved} files")
    print(f"  ⚠️  Skipped : {skipped} files")
    print(f"{'─' * 45}")

# ── Entry Point ───────────────────────────────────────────────
if __name__ == "__main__":
    organize_files(BASE_DIR)