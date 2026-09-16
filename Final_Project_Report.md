# Cognifyz Data Analysis — Final Project Report

## Title

Analysis of Restaurant Data (Cognifyz Data Analysis Internship)

## Internship Overview

This project completes Level 1 and Level 2 tasks of the Cognifyz Data Analysis internship assignment using the supplied dataset `DOC-20260811-WA0010.csv`.

## Objective

Provide a reproducible data cleaning and analysis pipeline that answers the required tasks in Level 1 and Level 2, produces CSV outputs, charts, an interactive map, and a consolidated Excel workbook.

## Dataset Description

- Source file: `data/DOC-20260811-WA0010.csv`.
- Rows processed: **9,551** restaurants.
- Key fields used: `Restaurant Name`, `City`, `Cuisines`, `Longitude`, `Latitude`, `Aggregate rating`, `Votes`, `Price range`, and several binary indicators (`Has Online delivery`, `Has Table booking`, etc.).

## Tools and Technologies

- Python 3 (system environment used)
- pandas, numpy for data handling
- matplotlib, seaborn for charts
- folium for interactive maps
- openpyxl for Excel output

## Data Cleaning and Preprocessing

Key cleaning steps (implemented in `src/analysis.py`):

- Standardized column names (trimmed whitespace).
- Converted numeric fields (`Aggregate rating`, `Votes`, `Price range`, `Average Cost for two`) to numeric types; non-convertible values set to NaN.
- Standardized Yes/No fields to boolean (`Has Table booking`, `Has Online delivery`, `Is delivering now`, `Switch to order menu`).
- Normalized `Cuisines` strings by splitting on commas and trimming whitespace; empty cuisines set to NaN.
- Saved cleaned dataset: `data/Cognifyz_Restaurant_Cleaned.csv`.

Data quality outputs:

- `data_quality_summary.csv` — missing values and unique counts per column.
- `data_dictionary.csv` — minimal data dictionary (column names with placeholders for descriptions).

All cleaning decisions are non-destructive and recorded in `src/analysis.py` so they are reproducible.

## Level 1 Analysis

### Task 1 — Top Cuisines

- Method: Split `Cuisines` by comma, explode into individual cuisines, count occurrences, then compute percentage of total restaurants.
- Result (top 3):
	- `North Indian`: 3,960 restaurants (41.46%)
	- `Chinese`: 2,735 restaurants (28.64%)
	- `Fast Food`: 1,986 restaurants (20.79%)
- Files: `Level_1/L1_T1_top_cuisines.csv`, `Level_1/L1_T1_top_cuisines.png`.

### Task 2 — City Analysis

- Method: Count restaurants per `City`; compute average `Aggregate rating` for cities using available ratings. To prevent misleading results from cities with very few restaurants, analyses that identify the highest-average-rating use a minimum-restaurant threshold (default: 5).
- Result:
	- City with most restaurants: **New Delhi** — 5,473 restaurants.
	- Highest average rating among cities with ≥5 restaurants (default): **London** — average rating 4.535 (20 restaurants in dataset).
- Files: `Level_1/L1_T2_city_analysis.csv`, `Level_1/L1_T2_top_cities.png`, `Level_1/L1_T2_average_rating_by_city.png`.

### Task 3 — Price Range Distribution

- Method: Count `Price range` values; compute percentages against total restaurants.
- Result summary:
	- Price Range 1: 4,444 restaurants (46.53%)
	- Price Range 2: 3,113 restaurants (32.59%)
	- Price Range 3: 1,408 restaurants (14.74%)
	- Price Range 4: 586 restaurants (6.14%)
- Files: `Level_1/L1_T3_price_range_distribution.csv`, `Level_1/L1_T3_price_range_distribution.png`.

### Task 4 — Online Delivery

- Method: Compare restaurants where `Has Online delivery` is `True` vs `False`. Compute counts, percentages, and average `Aggregate rating` for each group.
- Results:
	- Online delivery offered: 2,451 restaurants (25.66%).
	- Average rating with online delivery: 3.25
	- Average rating without online delivery: 2.47
- Files: `Level_1/L1_T4_online_delivery_percentage.csv`, `Level_1/L1_T4_online_delivery_rating_comparison.csv`, `Level_1/L1_T4_online_delivery.png`.

## Level 2 Analysis

### Task 1 — Restaurant Ratings

- Method: Use 0.5-wide bins to produce a rating distribution; compute summary statistics (count, average rating, median rating, average votes).
- Results:
	- Average rating: ~2.666
	- Median rating: 3.2
	- Average votes per restaurant: ~156.91
	- Most common rating bin: `3.0–3.5` (2,490 restaurants, 26.07%)
- Files: `Level_2/L2_T1_rating_distribution.csv`, `Level_2/L2_T1_rating_distribution.png`, `Level_2/L2_T1_average_votes.csv`.

### Task 2 — Cuisine Combination

- Method: Treat the normalized full cuisine string as the combination key (e.g., `North Indian, Chinese`). Count exact combination occurrences and compute average rating per combination. For rating comparisons, use a minimum-count threshold (default 5).
- Top combinations (sample):
	- `North Indian` (as single token): 936 restaurants, avg rating 1.67
	- `North Indian, Chinese`: 511 restaurants, avg rating 2.42
	- `Chinese`: 354 restaurants, avg rating 2.04
- Files: `Level_2/L2_T2_cuisine_combinations.csv`, `Level_2/L2_T2_top_combinations.png`.

### Task 3 — Geographic Analysis

- Method: Use `Longitude` and `Latitude` to create a static scatter and an interactive Folium map with clustered markers. Save coordinates for downstream use.
- Outputs:
	- `Level_2/L2_T3_restaurant_coordinates.csv` (Restaurant Name, City, Longitude, Latitude, Aggregate rating)
	- `Level_2/L2_T3_geographic_distribution.png` (static plot)
	- `Level_2/L2_T3_interactive_map.html` (interactive map)

### Task 4 — Restaurant Chains

- Method: Use repeated `Restaurant Name` values as a proxy for chains. For each repeated name, compute number of locations, average rating, total votes, and average votes.
- Example top names (proxy chains): `Cafe Coffee Day` (83 locations), `Domino's Pizza` (79 locations), `Subway` (63 locations).
- Files: `Level_2/L2_T4_restaurant_chains.csv`, `Level_2/L2_T4_top_chains.png`.

## Key Findings

- The dataset is large (9,551 restaurants), with a strong concentration in a few cities (New Delhi has 5,473 entries).
- North Indian, Chinese, and Fast Food dominate cuisine counts.
- Restaurants offering online delivery have higher average ratings on the dataset (3.25 vs 2.47), a finding that could indicate higher engagement or selection bias; further causal claims require more controlled data.

## Business Insights

- For a platform or delivery partner: focusing on partnerships with restaurants offering online delivery may yield higher average satisfaction scores (as measured here) and better customer experience signals.
- For market expansion: Price Range 1 and 2 represent ~79% of the dataset; discount or value-focused products will address the largest segment.

## Limitations

- Chain identification is name-based and may misclassify independently owned restaurants that share names.
- Average ratings may be skewed by low vote counts in some entries; consider weighting averages by `Votes` for robustness.
- Geographic patterns shown are descriptive; they do not control for sampling bias in the dataset.

## Conclusion

The analysis delivers reproducible outputs for the required Level 1 and Level 2 tasks. All numeric outputs are derived directly from the provided dataset and saved as CSVs and charts for easy review.

## Files / Outputs Generated

See the project `Level_1/` and `Level_2/` folders for all CSVs and charts. The consolidated Excel workbook `Cognifyz_Data_Analytics.xlsx` includes each analysis as a sheet.


<<<<<<< HEAD
=======
1. Place `DOC-20260811-WA0010.csv` in `data/`.
2. Install dependencies (`pip install -r requirements.txt`).
3. Run `python src/analysis.py`.

---

## Author and Contact

- **Name:** Vraj Parmar
- **Institution:** Drs. Kiran and Pallvai Patel Global University
- **Internship period:** 11 August 2026 — 11 September 2026
- **Email:** vrajparmar1707@gmail.com
- **GitHub:** vrajparmar1703

About the author: I am a Computer Engineering student, passionate about data analytics and Python automation. I have skills in data analysis and automation using Python and related libraries.

---

Prepared by `Vraj Parmar` for the Cognifyz Data Analysis Internship.
## Notes for interview / defense

- Be prepared to explain why cuisines were split by commas (to count each cuisine separately) and why a minimum-city threshold was used when comparing average ratings (to avoid one-restaurant distortions).
- Mention that chain detection uses name repetition as a heuristic and its limitations.

---
Generated by `src/analysis.py`. For any edits (visual style, thresholds, or additional tables), update the script and re-run.
>>>>>>> 635ea74 (Add author details and AUTHORS.md)
