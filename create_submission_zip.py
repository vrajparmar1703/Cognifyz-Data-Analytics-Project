import os
from pathlib import Path
import zipfile

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_ZIP = PROJECT_ROOT / "outputs" / "Cognifyz_Data_Analytics_Submission.zip"

INCLUDE = [
    "Level_1",
    "Level_2",
    "data",
    "reports",
    "src",
    "outputs",
    "requirements.txt",
    "README.md",
    "Cognifyz_Data_Analytics.xlsx",
    "AUTHORS.md",
]

EXCLUDE_DIRS = {" .git", ".venv", "venv", "__pycache__", ".github"}


def should_exclude(path: Path):
    parts = {p for p in path.parts}
    return any(e in parts for e in EXCLUDE_DIRS)


def create_zip():
    OUT_ZIP.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for item in INCLUDE:
            p = PROJECT_ROOT / item
            if not p.exists():
                continue
            if p.is_file():
                arcname = p.relative_to(PROJECT_ROOT)
                z.write(p, arcname)
            else:
                for root, dirs, files in os.walk(p):
                    root_path = Path(root)
                    # filter dirs in-place to skip excludes
                    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
                    if should_exclude(root_path):
                        continue
                    for f in files:
                        fp = root_path / f
                        if should_exclude(fp):
                            continue
                        arcname = fp.relative_to(PROJECT_ROOT)
                        z.write(fp, arcname)

    print(f"Created submission ZIP: {OUT_ZIP}")


if __name__ == "__main__":
    create_zip()
