import pandas as pd
import time
from howlongtobeatpy import HowLongToBeat

class HLTBScraper:
    def __init__(self, catalog_file="steam_analysis.csv"):
        self.catalog_file = catalog_file
        self.hltb = HowLongToBeat()

    def get_game_times(self, game_name):
        try:
            results = self.hltb.search(game_name)
            if results:
                best_match = max(results, key=lambda element: element.similarity)
                
                # Similarity check: skip if the name is too different
                if best_match.similarity < 0.7:
                    return None

                return {
                    "main_story": best_match.main_story,
                    "main_extra": best_match.main_extra,
                    "completionist": best_match.completionist,
                    "hltb_id": best_match.game_id
                }
        except Exception as e:
            print(f"HLTB Error for {game_name}: {e}")
        return None

    def update_catalog(self):
        df = pd.read_csv(self.catalog_file)
        for col in ['main_story', 'main_extra', 'completionist']:
            if col not in df.columns:
                df[col] = 0.0

        print(f"Fetching 'Time to Beat' for {len(df)} games...")

        for index, row in df.iterrows():
            if pd.notnull(row.get('main_story')) and row['main_story'] > 0:
                continue

            print(f"Searching HLTB for: {row['name']}")
            times = self.get_game_times(row['name'])
            
            if times:
                df.at[index, 'main_story'] = times['main_story']
                df.at[index, 'main_extra'] = times['main_extra']
                df.at[index, 'completionist'] = times['completionist']
            
            time.sleep(2)
            if index % 10 == 0:
                df.to_csv(self.catalog_file, index=False)

        df.to_csv(self.catalog_file, index=False)
        print("HLTB data merged into catalog.")
if __name__ == "__main__":
    scraper = HLTBScraper()
    scraper.update_catalog()