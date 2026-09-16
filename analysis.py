"""
Main analysis script for Cognifyz Data Analysis internship project.

Usage:
    python src/analysis.py

It expects the dataset at: data/DOC-20260811-WA0010.csv

The script will:
- Load and clean the data
- Run Level 1 and Level 2 analyses
- Save CSVs, charts, an interactive map, and an Excel workbook

"""
import os
import sys
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import MarkerCluster

# Excel writing
from openpyxl import load_workbook

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, 'data')
LEVEL1_DIR = os.path.join(BASE_DIR, 'Level_1')
LEVEL2_DIR = os.path.join(BASE_DIR, 'Level_2')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
OUTPUT_EXCEL = os.path.join(BASE_DIR, 'Cognifyz_Data_Analytics.xlsx')
CLEANED_CSV = os.path.join(DATA_DIR, 'Cognifyz_Restaurant_Cleaned.csv')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LEVEL1_DIR, exist_ok=True)
os.makedirs(LEVEL2_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

INPUT_CSV = os.path.join(DATA_DIR, 'DOC-20260811-WA0010.csv')


def load_data(path=INPUT_CSV):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found at {path}. Please place DOC-20260811-WA0010.csv in the data/ folder.")
    df = pd.read_csv(path)
    return df


def data_overview(df):
    summary = {
        'shape': df.shape,
        'columns': df.columns.tolist(),
        'dtypes': df.dtypes.astype(str).to_dict(),
        'missing_values': df.isna().sum().to_dict(),
        'duplicates': int(df.duplicated().sum())
    }
    return summary


def clean_data(df):
    df = df.copy()
    # Standardize column names (strip)
    df.columns = [c.strip() for c in df.columns]

    # Numeric conversions
    for col in ['Aggregate rating', 'Votes', 'Price range', 'Average Cost for two']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Standardize Yes/No fields
    yn_cols = ['Has Table booking', 'Has Online delivery', 'Is delivering now', 'Switch to order menu']
    for c in yn_cols:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip().str.lower().map({
                'yes': True, 'no': False, '1': True, '0': False, 'true': True, 'false': False
            })

    # Cuisines: keep as string, but standardize spacing
    if 'Cuisines' in df.columns:
        df['Cuisines'] = df['Cuisines'].fillna('').astype(str).apply(lambda x: ', '.join([s.strip() for s in x.split(',') if s.strip()]))
        df.loc[df['Cuisines']=='', 'Cuisines'] = np.nan

    # Keep original copy
    df.to_csv(CLEANED_CSV, index=False)

    # Data dictionary and quality summary
    dq = []
    for col in df.columns:
        dq.append({'column': col, 'dtype': str(df[col].dtype), 'missing': int(df[col].isna().sum()), 'unique': int(df[col].nunique(dropna=True))})
    pd.DataFrame(dq).to_csv(os.path.join(BASE_DIR, 'data_quality_summary.csv'), index=False)

    # Minimal data dictionary
    dd = []
    for col in df.columns:
        dd.append({'column': col, 'description': ''})
    pd.DataFrame(dd).to_csv(os.path.join(BASE_DIR, 'data_dictionary.csv'), index=False)

    return df


# LEVEL 1 - TASK 1: TOP CUISINES
def analyze_top_cuisines(df, top_n=3):
    # Split cuisines and count each cuisine separately
    cuisines_series = df['Cuisines'].dropna().str.split(',')
    cuisines_exploded = cuisines_series.explode().str.strip().value_counts()
    total_restaurants = len(df)
    top = cuisines_exploded.head(top_n).rename_axis('Cuisine').reset_index(name='Restaurant Count')
    top['Percentage of Restaurants'] = (top['Restaurant Count'] / total_restaurants * 100).round(2)

    out_csv = os.path.join(LEVEL1_DIR, 'L1_T1_top_cuisines.csv')
    out_png = os.path.join(LEVEL1_DIR, 'L1_T1_top_cuisines.png')
    top.to_csv(out_csv, index=False)

    # Plot
    plt.figure(figsize=(8,6))
    sns.barplot(data=top, x='Restaurant Count', y='Cuisine', palette='viridis')
    plt.title('Top Cuisines by Restaurant Count')
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()
    return top


# LEVEL 1 - TASK 2: CITY ANALYSIS
def analyze_cities(df, min_restaurants_threshold=5):
    city_counts = df['City'].value_counts().rename_axis('City').reset_index(name='Restaurant Count')
    # Average aggregate rating per city (exclude NaN)
    city_ratings = df.dropna(subset=['Aggregate rating']).groupby('City')['Aggregate rating'].mean().reset_index(name='Average Rating')
    city_summary = city_counts.merge(city_ratings, on='City', how='left')

    # Identify city with highest number of restaurants
    top_city = city_summary.sort_values('Restaurant Count', ascending=False).head(1)

    # Identify city with highest average rating, using threshold
    city_for_rating = city_summary[city_summary['Restaurant Count'] >= min_restaurants_threshold]
    if city_for_rating.empty:
        # lower threshold
        city_for_rating = city_summary
    top_avg_city = city_for_rating.sort_values('Average Rating', ascending=False).head(1)

    out_csv = os.path.join(LEVEL1_DIR, 'L1_T2_city_analysis.csv')
    out_png = os.path.join(LEVEL1_DIR, 'L1_T2_top_cities.png')
    # Save
    city_summary.to_csv(out_csv, index=False)

    # Plot top cities by count
    plt.figure(figsize=(10,6))
    top10 = city_summary.sort_values('Restaurant Count', ascending=False).head(10)
    sns.barplot(data=top10, x='Restaurant Count', y='City', palette='magma')
    plt.title('Top 10 Cities by Number of Restaurants')
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()

    # Optional average rating by city plot
    out_png2 = os.path.join(LEVEL1_DIR, 'L1_T2_average_rating_by_city.png')
    plt.figure(figsize=(10,6))
    top10r = city_summary.dropna(subset=['Average Rating']).sort_values('Average Rating', ascending=False).head(10)
    sns.barplot(data=top10r, x='Average Rating', y='City', palette='coolwarm')
    plt.title('Top 10 Cities by Average Rating')
    plt.tight_layout()
    plt.savefig(out_png2)
    plt.close()

    return city_summary, top_city, top_avg_city


# LEVEL 1 - TASK 3: PRICE RANGE DISTRIBUTION
def analyze_price_range(df):
    pr = df['Price range'].fillna(-1).astype(int)
    pr_counts = pr.value_counts().sort_index().rename_axis('Price Range').reset_index(name='Restaurant Count')
    total = len(df)
    pr_counts['Percentage'] = (pr_counts['Restaurant Count'] / total * 100).round(2)
    out_csv = os.path.join(LEVEL1_DIR, 'L1_T3_price_range_distribution.csv')
    out_png = os.path.join(LEVEL1_DIR, 'L1_T3_price_range_distribution.png')
    pr_counts.to_csv(out_csv, index=False)

    plt.figure(figsize=(8,6))
    sns.barplot(data=pr_counts, x='Price Range', y='Restaurant Count', palette='cubehelix')
    plt.title('Price Range Distribution')
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()
    return pr_counts


# LEVEL 1 - TASK 4: ONLINE DELIVERY
def analyze_online_delivery(df):
    df2 = df.copy()
    df2['Has Online delivery'] = df2['Has Online delivery'].fillna(False)
    counts = df2['Has Online delivery'].value_counts().rename_axis('Has Online Delivery').reset_index(name='Restaurant Count')
    total = len(df2)
    counts['Percentage'] = (counts['Restaurant Count'] / total * 100).round(2)

    # Average rating comparison
    ratings = df2.groupby('Has Online delivery')['Aggregate rating'].agg(['count','mean']).reset_index()
    ratings = ratings.rename(columns={'count':'Restaurant Count', 'mean':'Average Rating'})
    ratings['Average Rating'] = ratings['Average Rating'].round(2)

    out_csv1 = os.path.join(LEVEL1_DIR, 'L1_T4_online_delivery_percentage.csv')
    out_csv2 = os.path.join(LEVEL1_DIR, 'L1_T4_online_delivery_rating_comparison.csv')
    out_png = os.path.join(LEVEL1_DIR, 'L1_T4_online_delivery.png')
    counts.to_csv(out_csv1, index=False)
    ratings.to_csv(out_csv2, index=False)

    # Plot
    plt.figure(figsize=(8,6))
    sns.barplot(data=counts, x='Has Online Delivery', y='Restaurant Count', palette='Set2')
    plt.title('Restaurants Offering Online Delivery')
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()
    return counts, ratings


# LEVEL 2 - TASK 1: RATING DISTRIBUTION
def analyze_rating_distribution(df, bin_width=0.5):
    ratings = df['Aggregate rating'].dropna()
    bins = np.arange(0, 5+bin_width, bin_width)
    hist = pd.cut(ratings, bins=bins, right=False)
    dist = hist.value_counts().sort_index().rename_axis('Rating Range').reset_index(name='Restaurant Count')
    total = len(df)
    dist['Percentage'] = (dist['Restaurant Count'] / total * 100).round(2)

    stats = {
        'Number of restaurants': int(df.shape[0]),
        'Average rating': float(ratings.mean()) if len(ratings)>0 else np.nan,
        'Median rating': float(ratings.median()) if len(ratings)>0 else np.nan,
        'Average votes': float(df['Votes'].dropna().mean()) if 'Votes' in df.columns else np.nan
    }

    out_csv = os.path.join(LEVEL2_DIR, 'L2_T1_rating_distribution.csv')
    out_png = os.path.join(LEVEL2_DIR, 'L2_T1_rating_distribution.png')
    out_csv_stats = os.path.join(LEVEL2_DIR, 'L2_T1_average_votes.csv')
    dist.to_csv(out_csv, index=False)
    pd.DataFrame([stats]).to_csv(out_csv_stats, index=False)

    plt.figure(figsize=(8,6))
    sns.barplot(data=dist, x='Rating Range', y='Restaurant Count', palette='Blues')
    plt.xticks(rotation=45)
    plt.title('Rating Distribution')
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()

    return dist, stats


# LEVEL 2 - TASK 2: CUISINE COMBINATION
def analyze_cuisine_combinations(df, min_count_threshold=5):
    combos = df['Cuisines'].dropna().value_counts().rename_axis('Cuisine Combination').reset_index(name='Restaurant Count')
    combos['Average Rating'] = combos['Cuisine Combination'].apply(lambda comb: df[df['Cuisines']==comb]['Aggregate rating'].dropna().mean())
    combos['Average Rating'] = combos['Average Rating'].round(2)
    combos_sorted = combos.sort_values('Restaurant Count', ascending=False)

    out_csv = os.path.join(LEVEL2_DIR, 'L2_T2_cuisine_combinations.csv')
    out_png = os.path.join(LEVEL2_DIR, 'L2_T2_top_combinations.png')
    combos_sorted.to_csv(out_csv, index=False)

    topn = combos_sorted.head(10)
    plt.figure(figsize=(10,6))
    sns.barplot(data=topn, x='Restaurant Count', y='Cuisine Combination', palette='Spectral')
    plt.title('Top Cuisine Combinations')
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()

    # For rating analysis, filter by threshold
    combos_filtered = combos[combos['Restaurant Count'] >= min_count_threshold]

    return combos_sorted, combos_filtered


# LEVEL 2 - TASK 3: GEOGRAPHIC ANALYSIS
def analyze_geography(df):
    coords = df[['Restaurant Name','City','Longitude','Latitude','Aggregate rating']].dropna(subset=['Longitude','Latitude'])
    coords.to_csv(os.path.join(LEVEL2_DIR, 'L2_T3_restaurant_coordinates.csv'), index=False)

    # Static scatter
    out_png = os.path.join(LEVEL2_DIR, 'L2_T3_geographic_distribution.png')
    plt.figure(figsize=(10,6))
    plt.scatter(coords['Longitude'], coords['Latitude'], c=coords['Aggregate rating'].fillna(0), cmap='viridis', s=20)
    plt.colorbar(label='Aggregate Rating')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Geographic Distribution of Restaurants')
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()

    # Interactive map
    map_center = [coords['Latitude'].mean(), coords['Longitude'].mean()] if not coords.empty else [0,0]
    fmap = folium.Map(location=map_center, zoom_start=11)
    marker_cluster = MarkerCluster().add_to(fmap)
    for _, row in coords.iterrows():
        folium.Marker(location=[row['Latitude'], row['Longitude']], popup=f"{row['Restaurant Name']} ({row['City']}) - Rating: {row['Aggregate rating']}").add_to(marker_cluster)
    map_file = os.path.join(LEVEL2_DIR, 'L2_T3_interactive_map.html')
    fmap.save(map_file)

    return coords


# LEVEL 2 - TASK 4: RESTAURANT CHAINS
def analyze_restaurant_chains(df, min_locations=2):
    name_counts = df['Restaurant Name'].value_counts().rename_axis('Restaurant Name').reset_index(name='Number of Locations')
    chains = name_counts[name_counts['Number of Locations'] >= min_locations]
    # compute avg rating, total votes, avg votes
    rows = []
    for _, r in chains.iterrows():
        name = r['Restaurant Name']
        sub = df[df['Restaurant Name']==name]
        rows.append({
            'Restaurant Name': name,
            'Number of Locations': int(r['Number of Locations']),
            'Average Rating': round(sub['Aggregate rating'].dropna().mean(),2) if sub['Aggregate rating'].dropna().size>0 else np.nan,
            'Total Votes': int(sub['Votes'].dropna().sum()) if 'Votes' in sub.columns else np.nan,
            'Average Votes': round(sub['Votes'].dropna().mean(),2) if 'Votes' in sub.columns and sub['Votes'].dropna().size>0 else np.nan
        })
    chains_df = pd.DataFrame(rows).sort_values('Number of Locations', ascending=False)
    out_csv = os.path.join(LEVEL2_DIR, 'L2_T4_restaurant_chains.csv')
    out_png = os.path.join(LEVEL2_DIR, 'L2_T4_top_chains.png')
    chains_df.to_csv(out_csv, index=False)

    topn = chains_df.head(10)
    plt.figure(figsize=(10,6))
    sns.barplot(data=topn, x='Number of Locations', y='Restaurant Name', palette='cubehelix')
    plt.title('Top Restaurant Names by Number of Locations (Proxy for Chains)')
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()

    return chains_df


def save_to_excel(all_dfs_dict, excel_path=OUTPUT_EXCEL):
    # all_dfs_dict: {sheet_name: df}
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        for sheet, df in all_dfs_dict.items():
            df.to_excel(writer, sheet_name=sheet, index=False)
    return excel_path


def main():
    try:
        df = load_data()
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)

    overview = data_overview(df)
    print('Data overview:', overview['shape'])

    df_clean = clean_data(df)

    # Level 1
    top_cuisines = analyze_top_cuisines(df_clean)
    city_summary, top_city, top_avg_city = analyze_cities(df_clean, min_restaurants_threshold=5)
    price_dist = analyze_price_range(df_clean)
    online_counts, online_ratings = analyze_online_delivery(df_clean)

    # Level 2
    rating_dist, rating_stats = analyze_rating_distribution(df_clean)
    combos_all, combos_filtered = analyze_cuisine_combinations(df_clean, min_count_threshold=5)
    coords = analyze_geography(df_clean)
    chains = analyze_restaurant_chains(df_clean, min_locations=2)

    # Save Excel
    sheets = {
        'Data Quality': pd.read_csv(os.path.join(BASE_DIR,'data_quality_summary.csv')),
        'Top Cuisines': top_cuisines,
        'City Analysis': city_summary,
        'Price Range': price_dist,
        'Online Delivery': online_ratings,
        'Rating Distribution': rating_dist,
        'Cuisine Combinations': combos_all,
        'Geographic Analysis': coords,
        'Restaurant Chains': chains,
        'Summary': pd.DataFrame([{'Summary': 'Generated by analysis.py'}])
    }
    save_to_excel(sheets, OUTPUT_EXCEL)

    print('Analysis complete. Outputs saved under Level_1/, Level_2/, data/, and Cognifyz_Data_Analytics.xlsx')


if __name__ == '__main__':
    main()
