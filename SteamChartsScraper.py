import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

class SteamChartsScraper:
    def __init__(self, catalog_file="steam_catalog.csv"):
        self.catalog_file = catalog_file
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def get_player_data(self, app_id):
        url = f"https://steamcharts.com/app/{app_id}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            stats = soup.find_all('span', class_='num')
            
            return {
                "avg_players_30d": stats[0].text.strip().replace(',', '') if len(stats) > 0 else 0,
                "peak_players_30d": stats[1].text.strip().replace(',', '') if len(stats) > 1 else 0,
                "all_time_peak": stats[2].text.strip().replace(',', '') if len(stats) > 2 else 0
            }
        except Exception as e:
            print(f"Error scraping player data for {app_id}: {e}")
            return None

    def update_catalog(self):
        df = pd.read_csv(self.catalog_file)
        for col in ['avg_players_30d', 'peak_players_30d', 'all_time_peak']:
            if col not in df.columns:
                df[col] = 0.0

        print(f"Updating player stats for {len(df)} games...")
        
        for index, row in df.iterrows():
            if pd.notnull(row['avg_players_30d']) and row['avg_players_30d'] > 0:
                continue

            app_id = row['app_id']
            print(f"Fetching stats for {row['name']} ({app_id})...")
            
            stats = self.get_player_data(app_id)
            if stats:
                df.at[index, 'avg_players_30d'] = stats['avg_players_30d']
                df.at[index, 'peak_players_30d'] = stats['peak_players_30d']
                df.at[index, 'all_time_peak'] = stats['all_time_peak']
            
            time.sleep(2.0) 
            
            if index % 5 == 0:
                df.to_csv(self.catalog_file, index=False)
        df.to_csv(self.catalog_file, index=False)
        print(f"Finished! Updated data saved to {self.catalog_file}")