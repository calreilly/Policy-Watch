import requests
import pandas as pd
import time
import os

API_KEY = "LDxMtk3ML2DDrc4GzNipilXCwWQRlo8ElTZ179hSg+8QaVAnKzW56UePruFUhj4L"

def fetch_cfbd_ppa(start_year=2008, end_year=2023, output_dir="data"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "accept": "application/json"
    }

    print("Fetching Player PPA from CFBD API...")
    all_ppa = []
    
    for year in range(start_year, end_year + 1):
        try:
            print(f"Fetching {year}...", end=" ")
            url = f"https://api.collegefootballdata.com/ppa/players/season?year={year}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"Got {len(data)} players")
                for player in data:
                    # Flatten the JSON structure for PPA
                    flat_player = {
                        "season": player["season"],
                        "name": player["name"],
                        "position": player["position"],
                        "team": player["team"],
                    }
                    if player.get("averagePPA"):
                        flat_player["avg_PPA_all"] = player["averagePPA"].get("all")
                        flat_player["avg_PPA_pass"] = player["averagePPA"].get("pass")
                        flat_player["avg_PPA_rush"] = player["averagePPA"].get("rush")
                    
                    if player.get("totalPPA"):    
                        flat_player["total_PPA_all"] = player["totalPPA"].get("all")
                        
                    all_ppa.append(flat_player)
            else:
                print(f"Error {response.status_code}")
                
            time.sleep(0.5) # respect rate limits
        except Exception as e:
            print(f"Exception for {year}: {e}")

    df_ppa = pd.DataFrame(all_ppa)
    df_ppa.to_csv(os.path.join(output_dir, "cfbd_ppa.csv"), index=False)
    print(f"Saved cfbd_ppa.csv with {len(df_ppa)} rows")

if __name__ == "__main__":
    # PPA data reliably goes back to ~2008 in bulk for most teams
    fetch_cfbd_ppa(2008, 2023)
