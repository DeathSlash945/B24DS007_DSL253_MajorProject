import pandas as pd
import numpy as np

def calculate_advanced_success(input_file="steam_analysis.csv"):
    df = pd.read_csv(input_file)
    df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0)
    df['avg_players_30d'] = pd.to_numeric(df['avg_players_30d'], errors='coerce').fillna(1)
    df['all_time_peak'] = pd.to_numeric(df['all_time_peak'], errors='coerce').fillna(1)
    df['main_story'] = pd.to_numeric(df['main_story'], errors='coerce').fillna(1)
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    df['release_month'] = df['release_date'].dt.month.fillna(0).astype(int)
    
    # We use log1p (log of x+1) to handle zeros and normalize massive outliers
    log_peak = np.log1p(df['all_time_peak'])
    log_engagement = np.log1p(df['avg_players_30d'] * df['main_story'] *0.5)
    def normalize(series):
        if series.max() == series.min(): return 0
        return (series - series.min()) / (series.max() - series.min())

    # Intensity: Raw popularity
    intensity = normalize(log_peak)
    # Quality: Do players actually finish/stay in the game?
    quality = normalize(log_engagement)
    # ROI Factor: Success relative to price 
    # (Higher score for cheaper games with same player count)
    roi_factor = normalize(np.log1p((df['avg_players_30d']*0.5) / (df['price'] + 1)))
    # Weights: 40% Intensity, 40% Quality, 20% ROI
    df['overall_success_score'] = (
        (intensity * 0.3) + 
        (quality * 0.3) + 
        (roi_factor * 0.4)
    ) * 100

    # Adding a 'Tier' column for the dashboard to show AAA vs Indie vs Hobbyist
    df['success_tier'] = "Niche/Emerging" # Set default value first
    df.loc[df['overall_success_score'] >= 60, 'success_tier'] = "Mainstream"
    df.loc[df['overall_success_score'] >= 90, 'success_tier'] = "Market Leader"
    df.to_csv("steam_analysis.csv", index=False)