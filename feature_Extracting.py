import pandas as pd
import numpy as np

def calculate_advanced_success(input_file="steam_analysis.csv"):
    df = pd.read_csv(input_file)

    # Data Cleaning
    df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0)
    df['avg_players_30d'] = pd.to_numeric(df['avg_players_30d'], errors='coerce').fillna(10)
    df['all_time_peak'] = pd.to_numeric(df['all_time_peak'], errors='coerce').fillna(1000)
    df['main_story'] = pd.to_numeric(df['main_story'], errors='coerce').fillna(20)
    df['recommendations'] = pd.to_numeric(df['recommendations'], errors='coerce').fillna(50)
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    df['release_month'] = df['release_date'].dt.month.fillna(0).astype(int)
    
    # Normalize with log scales
    log_peak = np.log1p(df['all_time_peak'])
    log_engagement = np.log1p(df['avg_players_30d'] * (df['main_story']+0.01) *0.5)
    
    def normalize(series):
        if series.max() == series.min(): return 0
        return (series - series.min()) / (series.max() - series.min())

    intensity = normalize(log_peak)
    quality = normalize(log_engagement)
    roi_factor = normalize(np.log1p((df['avg_players_30d']*0.5) / (df['price'] + 1)))
    sentiment = normalize(df['recommendations'])

    # Updated Weights: Intensity (10%), Quality (30%), ROI (20%), Sentiment (40%)
    df['overall_success_score'] = (
        (intensity * 0.1) + 
        (quality * 0.3) + 
        (roi_factor * 0.2) +
        (sentiment * 0.4)
    ) * 100

    # Tier Classification
    df['success_tier'] = "Niche/Emerging"
    df.loc[df['overall_success_score'] >= 60, 'success_tier'] = "Mainstream"
    df.loc[df['overall_success_score'] >= 85, 'success_tier'] = "Market Leader"
    
    df.to_csv("steam_analysis.csv", index=False)