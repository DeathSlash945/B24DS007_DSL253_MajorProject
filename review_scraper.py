import pandas as pd
import requests
import time

def scrape_steam_reviews(file="steam_analysis.csv"):
    df = pd.read_csv(file)
    
    if 'app_id' not in df.columns:
        print("Error: 'app_id' column not found in CSV. Please ensure your dataset has app IDs.")
        return

    print(f"Starting review scraping for {len(df)} games...")
    
    # Initialize recommendations column if it doesn't exist
    if 'recommendations' not in df.columns:
        df['recommendations'] = 50.0

    for index, row in df.iterrows():
        # Only scrape if we don't have a value or if we want to refresh
        app_id = row['app_id']
        try:
            # Using Steam's official store API for review summaries
            url = f"https://store.steampowered.com/appreviews/{app_id}?json=1&language=all&purchase_type=all"
            response = requests.get(url, timeout=10).json()
            
            if response.get('success') and 'query_summary' in response:
                summary = response['query_summary']
                total_reviews = summary.get('total_reviews', 0)
                pos_reviews = summary.get('total_positive', 0)
                
                # Calculate percentage (0-100)
                score = (pos_reviews / total_reviews * 100) if total_reviews > 0 else 50
                df.at[index, 'recommendations'] = score
            else:
                df.at[index, 'recommendations'] = 50.0 # Neutral default
        except Exception as e:
            print(f"Failed to fetch ID {app_id}: {e}")
            df.at[index, 'recommendations'] = 50.0
        
        # Rate limiting to prevent IP blocks
        if index % 20 == 0:
            print(f"Progress: {index}/{len(df)} games processed...")
            df.to_csv(file, index=False)
            time.sleep(0.5)

    df.to_csv(file, index=False)
    print("Review scraping complete. 'recommendations' column updated.")

if __name__ == "__main__":
    scrape_steam_reviews()