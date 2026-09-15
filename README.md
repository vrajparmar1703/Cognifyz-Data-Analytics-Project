# Cognifyz Data Analysis Internship Project

This project contains a complete, reproducible analysis for the Cognifyz Data Analysis internship assignment. The pipeline loads the original dataset, performs cleaning, executes Level 1 and Level 2 analyses, saves CSV results and charts, creates an interactive map, and writes a consolidated Excel workbook.

Quick start

1. Place the dataset file `DOC-20260811-WA0010.csv` into `data/`.
2. (Recommended) Create and activate a virtual environment.
3. Install dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

4. Run the analysis:

```powershell
python src/analysis.py
```

Outputs

- `data/Cognifyz_Restaurant_Cleaned.csv` — cleaned dataset.
- `Level_1/` — Level 1 CSVs and charts.
- `Level_2/` — Level 2 CSVs, charts, and `L2_T3_interactive_map.html`.
- `Cognifyz_Data_Analytics.xlsx` — Excel workbook with separate sheets for each analysis.
- `reports/Final_Project_Report.md` — Final report (generated).

Notes

- The script is idempotent and will overwrite the output files each run.
- Tweak analysis parameters (thresholds, bin widths) in `src/analysis.py`.

If you want, I can export `reports/Final_Project_Report.md` to PDF or prepare a short slide deck of the key charts.

Author: Vraj Parmar
Institution: Drs. Kiran and Pallvai Patel Global University
Internship period: 11 August 2026 — 11 September 2026
Contact: vrajparmar1707@gmail.com

About the author: I am a Computer Engineering student, passionate about data analytics and Python automation. I have skills in data analysis and automation using Python and related libraries.
