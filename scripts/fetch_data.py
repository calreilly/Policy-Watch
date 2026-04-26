import os
import nfl_data_py as nfl
import pandas as pd

def fetch_data(start_year=2000, end_year=2024, output_dir="data"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print(f"Fetching NFL Draft Data from {start_year} to {end_year}...")
    years = list(range(start_year, end_year + 1))
    
    draft_picks = nfl.import_draft_picks(years)
    draft_picks.to_csv(os.path.join(output_dir, "draft_picks.csv"), index=False)
    print(f"Saved draft_picks.csv ({len(draft_picks)} rows)")
    
    print(f"Fetching Combine Data from {start_year} to {end_year}...")
    combine_data = nfl.import_combine_data(years)
    combine_data.to_csv(os.path.join(output_dir, "combine_data.csv"), index=False)
    print(f"Saved combine_data.csv ({len(combine_data)} rows)")
    
if __name__ == "__main__":
    fetch_data()
