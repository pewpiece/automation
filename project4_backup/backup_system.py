import shutil
import json
from pathlib import Path
from datetime import datetime

# ── Config ────────────────────────────────────────────────────
SOURCE_DIR  = Path("automation_projects")
BACKUP_DIR  = Path("backups")
LOG_FILE    = BACKUP_DIR / "backup_log.json"
MAX_BACKUPS = 3

# ── Helper: total folder size in bytes ────────────────────────
def folder_size(path: Path) -> int:
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())

# ── Helper: load existing log ─────────────────────────────────
def load_log() -> list:
    if LOG_FILE.exists():
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return []

# ── Helper: save log ──────────────────────────────────────────
def save_log(log: list) -> None:
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=4)

# ── Helper: enforce max backup limit ──────────────────────────
def enforce_limit(backup_dir: Path, max_keep: int) -> list:
    all_backups = sorted(backup_dir.glob("backup_*.zip"))
    deleted     = []

    for old in all_backups[:-max_keep] if len(all_backups) > max_keep else []:
        old.unlink()
        deleted.append(old.name)

    return deleted

# ── Helper: print section divider ─────────────────────────────
def divider(char: str = "─", length: int = 50) -> None:
    print(char * length)

# ── Main backup function ───────────────────────────────────────
def run_backup() -> None:
    BACKUP_DIR.mkdir(exist_ok=True)

    divider("═")
    print("  🗂️  AUTOMATIC BACKUP SYSTEM")
    divider("═")

    # ── Source check ──────────────────────────────────────────
    if not SOURCE_DIR.exists():
        print(f"  ❌ Source folder not found: {SOURCE_DIR.resolve()}")
        return

    print(f"  📂 Source  : {SOURCE_DIR.resolve()}")
    print(f"  📁 Backups : {BACKUP_DIR.resolve()}")
    divider()

    # ── Change detection ──────────────────────────────────────
    current_size = folder_size(SOURCE_DIR)
    log          = load_log()

    if log:
        last_size = log[-1].get("source_size_bytes", 0)
        if current_size == last_size:
            print("  ⏭️  No changes detected since last backup.")
            print("  ✅ Nothing to do — exiting cleanly.")
            divider("═")
            return

    # ── Capture timestamp once ────────────────────────────────
    now          = datetime.now()
    archive_name = f"backup_{now.strftime('%Y-%m-%d_%H-%M-%S')}"
    archive_path = BACKUP_DIR / f"{archive_name}.zip"

    print(f"  📦 Creating : {archive_name}.zip")

    # ── Create zip archive ────────────────────────────────────
    shutil.make_archive(
        str(BACKUP_DIR / archive_name),
        "zip",
        SOURCE_DIR,
    )

    size_kb  = round(archive_path.stat().st_size / 1024, 2)
    size_mb  = round(size_kb / 1024, 2)
    size_str = f"{size_mb} MB" if size_mb >= 1 else f"{size_kb} KB"

    # ── Enforce backup limit ──────────────────────────────────
    deleted = enforce_limit(BACKUP_DIR, MAX_BACKUPS)

    # ── Build and save log entry ──────────────────────────────
    entry = {
        "timestamp":         now.strftime("%Y-%m-%d %H:%M:%S"),
        "archive":           archive_path.name,
        "size_kb":           size_kb,
        "source_size_bytes": current_size,
        "status":            "success",
    }

    log.append(entry)
    save_log(log)

    # ── How many backups remain ───────────────────────────────
    remaining = sorted(BACKUP_DIR.glob("backup_*.zip"))

    # ── Terminal summary ──────────────────────────────────────
    divider()
    print(f"  ✅ Archive       : {archive_name}.zip")
    print(f"  💾 Size          : {size_str}")
    print(f"  📅 Timestamp     : {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  📋 Total runs    : {len(log)}")
    print(f"  🗃️  Kept backups  : {len(remaining)}/{MAX_BACKUPS}")

    if deleted:
        divider()
        print(f"  🗑️  Pruned old backups:")
        for name in deleted:
            print(f"       - {name}")

    divider()
    print(f"  📂 Backup log    : {LOG_FILE}")
    divider("═")

# ── Entry point ───────────────────────────────────────────────
if __name__ == "__main__":
    run_backup()