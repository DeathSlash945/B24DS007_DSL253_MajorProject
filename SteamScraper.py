import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

try:
    import msvcrt
except ImportError:
    msvcrt = None

class SteamScraper:
    def __init__(self, storage_file="steam_catalog.csv"):
        self.storage_file = storage_file
        self.api_url = "https://store.steampowered.com/api/appdetails"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        if os.path.exists(self.storage_file):
            self.df = pd.read_csv(self.storage_file)
            # Ensure app_id is integer for comparison
            self.df['app_id'] = self.df['app_id'].astype(int)
        else:
            self.df = pd.DataFrame()
        
        self.total_scraped_this_session = 0

    def fetch_search_page(self, start=0, sort_by="released_desc"):
        """
        sort_by options: 
        - 'released_desc': Newest releases (Best for getting thousands of games)
        - 'topsellers': What you used before
        - 'revenue_desc': Global Top Sellers
        """
        url = f"https://store.steampowered.com/search/?sort_by={sort_by}&start={start}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            found = []
            for row in soup.select('a.search_result_row'):
                appid = row.get('data-ds-appid')
                if appid:
                    # Some entries have multiple IDs (bundles), we take the first
                    appid = appid.split(',')[0]
                    found.append(int(appid))
            return found
        except Exception as e:
            print(f"Error fetching search page: {e}")
            return []

    def get_detailed_info(self, app_id):
        try:
            res = requests.get(self.api_url, params={"appids": app_id, "l": "english"}, timeout=10)
            # Handle rate limiting (429)
            if res.status_code == 429:
                print("Rate limited! Sleeping for 30 seconds...")
                time.sleep(30)
                return None
                
            data = res.json()
            if not data or not data.get(str(app_id), {}).get('success'):
                return None
            
            info = data[str(app_id)]['data']
            
            # Filter out non-games (DLC, hardware, etc)
            if info.get("type") != "game":
                return None

            return {
                "app_id": app_id,
                "name": info.get("name"),
                "type": info.get("type"),
                "is_free": info.get("is_free"),
                "price": info.get("price_overview", {}).get("final", 0) / 100 if not info.get("is_free") else 0,
                "currency": info.get("price_overview", {}).get("currency", "USD"),
                "genres": "|".join([g['description'] for g in info.get("genres", [])]),
                "tags": "|".join([t['description'] for t in info.get("categories", [])]),
                "developer": info.get("developers", ["Unknown"])[0],
                "release_date": info.get("release_date", {}).get("date"),
                "header_image": info.get("header_image"),
                "short_description": info.get("short_description")
            }
        except:
            return None

    def check_for_quit(self):
        if msvcrt:
            if msvcrt.kbhit():
                key = msvcrt.getch().decode('utf-8').lower()
                if key == 'q':
                    return True
        return False

    def update_catalog(self, target_count=5000):
        current_start = 0
        session_count = 0
        
        print(f"\nTARGET: {target_count} new games.")

        try:
            while session_count < target_count:
                if self.check_for_quit():
                    print("\n'q' detected! Saving and exiting...")
                    break

                print(f"\n--- Searching Deep Catalog (Index: {current_start}) ---")
                app_ids = self.fetch_search_page(current_start, sort_by="released_desc")
                
                if not app_ids:
                    print("Reached end of Steam listings.")
                    break

                new_entries = []
                for aid in app_ids:
                    if self.check_for_quit(): break

                    # Skip if we already have it
                    if not self.df.empty and aid in self.df['app_id'].values:
                        continue
                    
                    print(f"  > New AppID found: {aid}")
                    details = self.get_detailed_info(aid)
                    
                    if details:
                        new_entries.append(details)
                        session_count += 1
                        self.total_scraped_this_session += 1
                        # Save every 10 games just in case of a crash
                        if len(new_entries) >= 10:
                            self._save_batch(new_entries)
                            new_entries = []
                    
                    # 1.5s sleep is safer for 'indefinite' runs to avoid IP bans
                    time.sleep(1.5) 

                if new_entries:
                    self._save_batch(new_entries)
                
                # Move to next page
                current_start += 50 

        except KeyboardInterrupt:
            print("\nForce stopped.")
        
        print(f"\n--- Session Summary ---")
        print(f"Added: {self.total_scraped_this_session} | Total DB: {len(self.df)}")

    def _save_batch(self, entries):
        new_df = pd.DataFrame(entries)
        self.df = pd.concat([self.df, new_df], ignore_index=True)
        self.df.to_csv(self.storage_file, index=False)
        print(f"Checkpoint: {len(self.df)} total records saved.")