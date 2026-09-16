import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRS = ["Level_1", "Level_2", "data", "reports"]
OUT_DIR = PROJECT_ROOT / "outputs"
PATTERNS = ["*.csv", "*.png", "*.jpg", "*.jpeg", "*.html", "*.xlsx", "*.pdf"]


def gather():
    OUT_DIR.mkdir(exist_ok=True)
    copied = 0
    for src in SRC_DIRS:
        src_path = PROJECT_ROOT / src
        if not src_path.exists():
            continue
        target_sub = OUT_DIR / src
        target_sub.mkdir(parents=True, exist_ok=True)
        for pattern in PATTERNS:
            for p in src_path.rglob(pattern):
                try:
                    dest = target_sub / p.name
                    shutil.copy2(p, dest)
                    copied += 1
                except Exception as e:
                    print(f"Failed copying {p}: {e}")
    # Also copy top-level workbook if present
    top_workbook = PROJECT_ROOT / "Cognifyz_Data_Analytics.xlsx"
    if top_workbook.exists():
        shutil.copy2(top_workbook, OUT_DIR / top_workbook.name)
        copied += 1

    print(f"Copied {copied} files into {OUT_DIR}")


if __name__ == "__main__":
    gather()
